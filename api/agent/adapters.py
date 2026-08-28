"""catalog actionから既存model/task selectorへの明示adapter。

既存routerは呼ばず、readは列allowlist、変更はSQLAlchemyまたはTaskManagerだけを
使用する。汎用HTTP proxyや任意shell実行口は提供しない。
"""

import json
import subprocess
import tempfile
from dataclasses import dataclass
from os.path import join
from pathlib import Path
from typing import Any, Callable

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa
from sqlalchemy import and_, false, func, or_
from sqlalchemy.orm import Query, Session, object_session

from auth.function import get_password_hash
from domain.models import DomainModel
from domain.service import (
    DomainProjectMoveConflictError,
    DomainProjectMoveNotFoundError,
    move_domain_to_project,
)
from flavor.models import FlavorModel
from network.models import NetworkModel, NetworkPoolModel, NetworkPortgroupModel
from node.models import NodeModel
from project.models import ProjectModel
from project.schemas import ProjectResourceGrantsUpdate
from project.service import (
    ProjectConflictError,
    ProjectGrantNotFoundError,
    ProjectMemberNotFoundError,
    ProjectNotFoundError,
    add_project_member,
    ensure_flavor_deletable,
    ensure_network_pool_deletable,
    ensure_storage_pool_deletable,
    ensure_storage_pool_update_allowed,
    ensure_user_memberships_deletable,
    lock_project,
    remove_storage_pool,
    remove_project_member,
    rename_project,
    replace_project_resource_grants,
)
from settings import API_VERSION, DATA_ROOT
from storage.models import (
    AssociationStoragePoolModel,
    ImageModel,
    StorageMetadataModel,
    StorageModel,
    StoragePoolModel,
)
from task.models import TaskModel
from task.functions import ARCHIVABLE_STATUSES, archive_terminal_tasks
from user.admin_guard import would_remove_last_admin
from user.models import (
    UserModel,
    UserPublickeyModel,
    UserScopeModel,
)

from .audit import redact_secrets
from .exceptions import AuthorizationError, ConflictError, NotFoundError
from .policy import LeaseContext, resolve_generation


@dataclass(frozen=True)
class ResolvedTarget:
    resource_type: str
    resource_id: str | None
    project_id: str | None
    node_id: str | None
    generation_resource_type: str | None = None
    generation_resource_id: str | None = None
    related_targets: tuple[dict[str, str], ...] = ()
    reservation_scope: str = "resource"
    reservation_mode: str = "exclusive"

    def task_value(self) -> list[dict[str, str]]:
        if self.generation_resource_type is None or self.generation_resource_id is None:
            value = {
                "resourceType": self.resource_type,
                "resourceId": self.resource_id or "0",
            }
        else:
            value = {
                "resourceType": self.generation_resource_type,
                "resourceId": self.generation_resource_id,
            }
        if self.project_id is not None:
            value["projectId"] = self.project_id
        if self.node_id is not None:
            value["nodeId"] = self.node_id
        if self.generation_resource_type is not None:
            value["generationTarget"] = "true"
        value["reservationScope"] = self.reservation_scope
        value["reservationMode"] = self.reservation_mode
        return [value, *[dict(item) for item in self.related_targets]]


def _is_admin(db: Session, principal_id: str) -> bool:
    return db.query(UserScopeModel).filter(
        UserScopeModel.user_id == principal_id,
        UserScopeModel.name == "admin",
    ).first() is not None


def _page(query: Query, model: Any) -> tuple[int, list[Any]]:
    count = query.count()
    limit = int(getattr(model, "limit", 25))
    page = int(getattr(model, "page", 0))
    if limit > 0:
        query = query.limit(min(limit, 1000)).offset(limit * page)
    return count, query.all()


def _model_session(model: object) -> Session:
    """serializerが受け取った永続modelのSessionを安全に取得する。"""

    session = object_session(model)
    if session is None:
        raise RuntimeError("永続化されていないmodelはserializeできません")
    return session


def _node_dict(model: NodeModel) -> dict[str, Any]:
    return {
        "name": model.name,
        "description": model.description,
        "domain": model.domain,
        "sshUser": model.user_name,
        "port": model.port,
        "core": model.core,
        "memory": model.memory,
        "cpuGeneration": model.cpu_gen,
        "osLike": model.os_like,
        "osName": model.os_name,
        "osVersion": model.os_version,
        "status": model.status,
        "qemuVersion": model.qemu_version,
        "libvirtVersion": model.libvirt_version,
        "roles": [
            {"name": role.role_name, "extra": role.extra_json}
            for role in model.roles
        ],
        "generation": resolve_generation(
            _model_session(model),
            resource_type="node",
            resource_id=model.name,
        ),
    }


def _vm_dict(model: DomainModel) -> dict[str, Any]:
    return {
        "uuid": model.uuid,
        "name": model.name,
        "core": model.core,
        "memory": model.memory,
        "status": model.status,
        "description": model.description,
        "storageUsed": model.storage_used,
        "nodeName": model.node_name,
        "ownerUserId": model.owner_user_id,
        "ownerProjectId": model.owner_project_id,
        "interfaces": [
            {
                "mac": item.mac,
                "type": item.type,
                "target": item.target,
                "bridge": item.bridge,
                "network": item.network,
                "port": item.port,
            }
            for item in model.interfaces
        ],
        "drives": [
            {
                "target": item.target,
                "device": item.device,
                "type": item.type,
                "source": item.source,
            }
            for item in model.drives
        ],
        # vnc_port/vnc_passwordはAgent readへ公開しない。
        "generation": resolve_generation(
            _model_session(model),
            resource_type="vm",
            resource_id=model.uuid,
        ),
    }


def _network_dict(
    model: NetworkModel,
    allowed_port_names: set[str] | None = None,
) -> dict[str, Any]:
    return {
        "uuid": model.uuid,
        "name": model.name,
        "description": model.description,
        "nodeName": model.node_name,
        "bridge": model.bridge,
        "type": model.type,
        "active": model.active,
        "autoStart": model.auto_start,
        "dhcp": model.dhcp,
        "ip": model.ip,
        "mac": model.mac,
        "portgroups": [
            {
                "name": item.name,
                "vlanId": item.vlan_id,
                "isDefault": item.is_default,
            }
            for item in model.portgroups
            if allowed_port_names is None or item.name in allowed_port_names
        ],
        "generation": resolve_generation(
            _model_session(model),
            resource_type="network",
            resource_id=model.uuid,
        ),
    }


def _storage_dict(model: StorageModel) -> dict[str, Any]:
    metadata = model.meta_data
    return {
        "uuid": model.uuid,
        "name": model.name,
        "nodeName": model.node_name,
        "capacity": model.capacity,
        "available": model.available,
        "path": model.path,
        "active": model.active,
        "autoStart": model.auto_start,
        "status": model.status,
        "metadata": None if metadata is None else {
            "role": metadata.rool,
            "protocol": metadata.protocol,
            "deviceType": metadata.device_type,
        },
        "generation": resolve_generation(
            _model_session(model),
            resource_type="storage",
            resource_id=model.uuid,
        ),
    }


def _image_dict(model: ImageModel) -> dict[str, Any]:
    return {
        "name": model.name,
        "storageUuid": model.storage_uuid,
        "capacity": model.capacity,
        "allocation": model.allocation,
        "path": model.path,
        "domainUuid": model.domain_uuid,
        "flavorId": model.flavor_id,
        "generation": resolve_generation(
            _model_session(model),
            resource_type="image",
            resource_id=json.dumps(
                [model.storage_uuid, model.path],
                ensure_ascii=False,
                separators=(",", ":"),
            ),
        ),
    }


def _project_dict(db: Session, model: ProjectModel) -> dict[str, Any]:
    used = db.query(
        func.coalesce(func.sum(DomainModel.core), 0),
        func.coalesce(func.sum(DomainModel.memory), 0),
        func.coalesce(func.sum(DomainModel.storage_used), 0),
    ).filter(DomainModel.owner_project_id == model.id).one()
    return {
        "id": model.id,
        "name": model.name,
        "memberCount": len(model.users),
        "usedCore": int(used[0]),
        "usedMemoryG": float(used[1]) / 1024,
        "usedStorageG": int(used[2]),
        "limits": {
            "core": model.core,
            "memoryG": model.memory_g,
            "storageCapacityG": model.storage_capacity_g,
            "enforced": False,
        },
        "members": [
            {"username": user.username}
            for user in sorted(model.users, key=lambda item: item.username)
        ],
        "resourceGrants": {
            "storagePoolIds": sorted(pool.id for pool in model.storage_pools),
            "networkPoolIds": sorted(pool.id for pool in model.network_pools),
            "flavorIds": sorted(flavor.id for flavor in model.flavors),
        },
        "storagePools": [
            {"id": pool.id, "name": pool.name or f"Pool {pool.id}"}
            for pool in sorted(model.storage_pools, key=lambda item: item.id)
        ],
        "networkPools": [
            {"id": pool.id, "name": pool.name or f"Pool {pool.id}"}
            for pool in sorted(model.network_pools, key=lambda item: item.id)
        ],
        "flavors": [
            {"id": flavor.id, "name": flavor.name}
            for flavor in sorted(model.flavors, key=lambda item: item.id)
        ],
        "generation": resolve_generation(
            db,
            resource_type="project",
            resource_id=model.id,
        ),
    }


def _user_dict(db: Session, model: UserModel) -> dict[str, Any]:
    return {
        "username": model.username,
        "scopes": [scope.name for scope in model.scopes],
        "projectIds": [project.id for project in model.projects],
        # SSH公開鍵も投入経路はwrite-onlyとし、名前だけを返す。
        "publicKeyNames": [key.name for key in model.publickeys],
        "generation": resolve_generation(
            db,
            resource_type="user",
            resource_id=model.username,
        ),
    }


def _flavor_dict(db: Session, model: FlavorModel) -> dict[str, Any]:
    return {
        "id": model.id,
        "name": model.name,
        "os": model.os,
        "manualUrl": model.manual_url,
        "icon": model.icon,
        "cloudInitReady": model.cloud_init_ready,
        "cloudInitUser": model.cloud_init_user,
        "description": model.description,
        "generation": resolve_generation(
            db,
            resource_type="flavor",
            resource_id=str(model.id),
        ),
    }


def _task_dict(model: TaskModel) -> dict[str, Any]:
    return {
        "uuid": model.uuid,
        "postTime": model.post_time,
        "startTime": model.start_time,
        "updateTime": model.update_time,
        "runTime": model.run_time,
        "principalId": model.principal_id or model.user_id,
        "status": model.status,
        "resource": model.resource,
        "object": model.object,
        "method": model.method,
        "result": redact_secrets(model.result),
        "message": redact_secrets(model.message),
        "log": redact_secrets(model.log),
        "errorCode": model.error_code,
        "retryable": model.retryable,
        "correlationId": model.correlation_id,
        "generation": resolve_generation(
            _model_session(model),
            resource_type="task",
            resource_id=model.uuid,
        ),
    }


def _effective_project_ids(db: Session, context: LeaseContext) -> set[str]:
    """現在の所属と能力leaseのProject制約を交差して返す。"""

    principal = db.get(UserModel, context.principal_id)
    memberships = {
        str(project.id)
        for project in ([] if principal is None else principal.projects)
    }
    if context.lease.project_ids:
        memberships &= set(context.lease.project_ids)
    return memberships


def _selected_project_ids(
    db: Session,
    context: LeaseContext,
    project_id: str | None = None,
) -> set[str]:
    effective = _effective_project_ids(db, context)
    if project_id is None:
        return effective
    if project_id not in effective:
        raise NotFoundError("project_not_found", "projectがありません")
    return {project_id}


def _allowed_storage_ids(
    db: Session,
    context: LeaseContext,
    project_id: str | None = None,
) -> set[str]:
    project_ids = _selected_project_ids(db, context, project_id)
    projects = db.query(ProjectModel).filter(
        ProjectModel.id.in_(project_ids),
    ).all()
    allowed = {
        association.storage_uuid
        for project in projects
        for pool in project.storage_pools
        for association in pool.storages
    }
    if context.lease.node_ids:
        allowed &= {
            row[0]
            for row in db.query(StorageModel.uuid).filter(
                StorageModel.node_name.in_(context.lease.node_ids)
            )
        }
    return allowed


def _allowed_network_grants(
    db: Session,
    context: LeaseContext,
    project_id: str | None = None,
) -> tuple[set[str], set[tuple[str, str]]]:
    effective_project_ids = _selected_project_ids(db, context, project_id)
    project_ids = (
        {project_id}
        if project_id is not None
        else effective_project_ids
    )

    direct_network_ids: set[str] = set()
    network_ports: set[tuple[str, str]] = set()
    projects = db.query(ProjectModel).filter(
        ProjectModel.id.in_(project_ids),
    ).all()
    for project in projects:
        direct_network_ids.update(
            network.uuid
            for pool in project.network_pools
            for network in pool.networks
        )
        network_ports.update(
            (port.network_uuid, port.name)
            for pool in project.network_pools
            for port in pool.ports
        )

    if context.lease.node_ids:
        node_network_ids = {
            str(row[0])
            for row in db.query(NetworkModel.uuid).filter(
                NetworkModel.node_name.in_(context.lease.node_ids),
            )
        }
        direct_network_ids &= node_network_ids
        network_ports = {
            item for item in network_ports if item[0] in node_network_ids
        }
    return direct_network_ids, network_ports


def _allowed_network_ids(
    db: Session,
    context: LeaseContext,
    project_id: str | None = None,
) -> set[str]:
    grants = _allowed_network_grants(db, context, project_id)
    direct_network_ids, network_ports = grants
    return direct_network_ids | {
        network_id for network_id, _ in network_ports
    }


def _allowed_network_port_names(
    db: Session,
    context: LeaseContext,
    network_id: str,
    project_id: str | None = None,
) -> set[str] | None:
    grants = _allowed_network_grants(db, context, project_id)
    direct_network_ids, network_ports = grants
    if network_id in direct_network_ids:
        return None
    return {
        port_name
        for granted_network_id, port_name in network_ports
        if granted_network_id == network_id
    }


def _allowed_project_node_ids(
    db: Session,
    context: LeaseContext,
    project_id: str | None = None,
) -> set[str]:
    project_ids = _selected_project_ids(db, context, project_id)
    projects = db.query(ProjectModel).filter(
        ProjectModel.id.in_(project_ids),
    ).all()
    result = {
        vm.node_name
        for vm in db.query(DomainModel).filter(
            DomainModel.owner_project_id.in_(project_ids),
        )
        if vm.node_name is not None
    }
    if project_id is None and not context.lease.project_ids:
        result.update(
            vm.node_name
            for vm in db.query(DomainModel).filter(
                DomainModel.owner_user_id == context.principal_id,
                DomainModel.owner_project_id.is_(None),
            )
            if vm.node_name is not None
        )
    result.update(
        storage.node_name
        for project in projects
        for pool in project.storage_pools
        for association in pool.storages
        for storage in [db.get(StorageModel, association.storage_uuid)]
        if storage is not None and storage.node_name is not None
    )
    result.update(
        network.node_name
        for project in projects
        for pool in project.network_pools
        for network in [*pool.networks, *(port.network for port in pool.ports)]
        if network.node_name is not None
    )
    if context.lease.node_ids:
        result &= set(context.lease.node_ids)
    return result


def _allowed_storage_pool_ids(
    db: Session,
    context: LeaseContext,
    project_id: str | None = None,
) -> set[int]:
    return {
        int(pool.id)
        for project in db.query(ProjectModel).filter(
            ProjectModel.id.in_(_selected_project_ids(db, context, project_id)),
        )
        for pool in project.storage_pools
    }


def _allowed_network_pool_ids(
    db: Session,
    context: LeaseContext,
    project_id: str | None = None,
) -> set[int]:
    return {
        int(pool.id)
        for project in db.query(ProjectModel).filter(
            ProjectModel.id.in_(_selected_project_ids(db, context, project_id)),
        )
        for pool in project.network_pools
    }


def _allowed_flavor_ids(
    db: Session,
    context: LeaseContext,
    project_id: str | None = None,
) -> set[int]:
    return {
        int(flavor.id)
        for project in db.query(ProjectModel).filter(
            ProjectModel.id.in_(_selected_project_ids(db, context, project_id)),
        )
        for flavor in project.flavors
    }


def _deny_global_read_when_scoped(context: LeaseContext) -> None:
    if context.lease.project_ids or context.lease.node_ids:
        raise AuthorizationError(
            "scoped_global_read_denied",
            "制約付きleaseではglobal情報を取得できません",
        )


def _require_resource_id(target: Any) -> str:
    if not target.resource_id:
        raise ConflictError("resource_id_required", "resourceIdが必要です")
    return target.resource_id


def _require_allowed_node(
    db: Session,
    context: LeaseContext,
    resource_id: str,
    project_id: str | None = None,
) -> NodeModel:
    row = db.get(NodeModel, resource_id)
    if row is None or row.name not in _allowed_project_node_ids(
        db,
        context,
        project_id,
    ):
        raise NotFoundError("node_not_found", "nodeがありません")
    return row


def _require_allowed_vm(
    db: Session,
    context: LeaseContext,
    resource_id: str,
) -> DomainModel:
    row = db.get(DomainModel, resource_id)
    project_ids = _effective_project_ids(db, context)
    personal_allowed = (
        not context.lease.project_ids
        and row is not None
        and row.owner_user_id == context.principal_id
        and row.owner_project_id is None
    )
    project_allowed = (
        row is not None
        and row.owner_project_id is not None
        and row.owner_project_id in project_ids
    )
    node_allowed = (
        row is not None
        and (
            not context.lease.node_ids
            or row.node_name in context.lease.node_ids
        )
    )
    if row is None or not node_allowed or not (personal_allowed or project_allowed):
        raise NotFoundError("vm_not_found", "VMがありません")
    return row


def node_list(db: Session, context: LeaseContext, model: Any, _: Any) -> Any:
    query = db.query(NodeModel).order_by(NodeModel.name)
    allowed_project_nodes = _allowed_project_node_ids(
        db,
        context,
        getattr(model, "project_id", None),
    )
    query = query.filter(NodeModel.name.in_(allowed_project_nodes))
    if getattr(model, "name_like", None):
        query = query.filter(NodeModel.name.like(f"%{model.name_like}%"))
    count, rows = _page(query, model)
    return {"count": count, "data": [_node_dict(row) for row in rows]}


def node_get(db: Session, context: LeaseContext, __: Any, target: Any) -> Any:
    row = _require_allowed_node(
        db,
        context,
        _require_resource_id(target),
        getattr(target, "project_id", None),
    )
    return _node_dict(row)


def node_facts(db: Session, context: LeaseContext, __: Any, target: Any) -> Any:
    row = _require_allowed_node(
        db,
        context,
        _require_resource_id(target),
        getattr(target, "project_id", None),
    )
    return row.ansible_facts


def node_info(db: Session, context: LeaseContext, __: Any, target: Any) -> Any:
    from module.paramikolib import ParamikoManager

    row = _require_allowed_node(
        db,
        context,
        _require_resource_id(target),
        getattr(target, "project_id", None),
    )
    manager = ParamikoManager(user=row.user_name, domain=row.domain, port=row.port)
    commands = {
        "ipAddress": "ip a",
        "ipRoute": "ip r",
        "ipNeigh": "ip neigh",
        "dfH": "df -h",
        "lsblk": "lsblk",
        "uptime": "uptime -p",
        "free": "free -h",
        "top": "top -b -n 1|head -n 20",
        "iptablesNat": "sudo iptables -L -t nat",
        "iptables": "sudo iptables -L",
        "netplanGet": "sudo netplan get",
    }
    return {name: manager.run_cmd(command).stdout for name, command in commands.items()}


def node_ssh_public_key(db: Session, _: LeaseContext, __: Any, ___: Any) -> Any:
    del db
    for name in ("id_rsa.pub", "id_ed25519.pub"):
        path = Path.home() / ".ssh" / name
        if path.is_file():
            return {"publicKey": path.read_text()}
    raise NotFoundError("ssh_public_key_not_found", "SSH公開鍵が設定されていません")


def vm_list(db: Session, context: LeaseContext, model: Any, _: Any) -> Any:
    query = db.query(DomainModel).order_by(DomainModel.name)
    project_ids = _effective_project_ids(db, context)
    project_id = getattr(model, "project_id", None)
    if project_id is not None:
        query = query.filter(
            DomainModel.owner_project_id.in_(
                _selected_project_ids(db, context, project_id),
            ),
        )
    elif context.lease.project_ids:
        query = query.filter(DomainModel.owner_project_id.in_(project_ids))
    else:
        query = query.filter(or_(
            DomainModel.owner_project_id.in_(project_ids),
            DomainModel.owner_user_id == context.principal_id,
        ))
    if context.lease.node_ids:
        query = query.filter(DomainModel.node_name.in_(context.lease.node_ids))
    if getattr(model, "name_like", None):
        query = query.filter(DomainModel.name.like(f"%{model.name_like}%"))
    if getattr(model, "node_name_like", None):
        query = query.filter(DomainModel.node_name.like(f"%{model.node_name_like}%"))
    count, rows = _page(query, model)
    return {"count": count, "data": [_vm_dict(row) for row in rows]}


def vm_get(db: Session, context: LeaseContext, __: Any, target: Any) -> Any:
    row = _require_allowed_vm(db, context, _require_resource_id(target))
    return _vm_dict(row)


def vm_xml(db: Session, context: LeaseContext, __: Any, target: Any) -> Any:
    from module.xmllib import redact_domain_xml_secrets

    resource_id = _require_resource_id(target)
    _require_allowed_vm(db, context, resource_id)
    try:
        xml = Path(join(DATA_ROOT, "xml/domain", f"{resource_id}.xml")).read_text()
    except FileNotFoundError as exc:
        raise NotFoundError("vm_xml_not_found", "VM XMLがありません") from exc
    return {"xml": redact_domain_xml_secrets(xml)}


def storage_list(db: Session, context: LeaseContext, model: Any, _: Any) -> Any:
    query = db.query(StorageModel).order_by(StorageModel.name, StorageModel.node_name)
    allowed = _allowed_storage_ids(
        db,
        context,
        getattr(model, "project_id", None),
    )
    query = query.filter(StorageModel.uuid.in_(allowed))
    if getattr(model, "node_name", None):
        query = query.filter(StorageModel.node_name == model.node_name)
    if getattr(model, "name_like", None):
        query = query.filter(StorageModel.name.like(f"%{model.name_like}%"))
    count, rows = _page(query, model)
    return {"count": count, "data": [_storage_dict(row) for row in rows]}


def storage_get(db: Session, context: LeaseContext, __: Any, target: Any) -> Any:
    row = db.get(StorageModel, _require_resource_id(target))
    if row is None or row.uuid not in _allowed_storage_ids(
        db,
        context,
        getattr(target, "project_id", None),
    ):
        raise NotFoundError("storage_not_found", "storageがありません")
    return _storage_dict(row)


def storage_pool_list(db: Session, context: LeaseContext, model: Any, _: Any) -> Any:
    project_id = getattr(model, "project_id", None)
    query = db.query(StoragePoolModel).filter(
        StoragePoolModel.id.in_(
            _allowed_storage_pool_ids(db, context, project_id),
        ),
    ).order_by(StoragePoolModel.id)
    rows = query.all()
    allowed_storages = _allowed_storage_ids(db, context, project_id)
    if context.lease.node_ids:
        rows = [
            row
            for row in rows
            if {item.storage_uuid for item in row.storages}.intersection(
                allowed_storages,
            )
        ]
    data = [{
        "id": row.id,
        "name": row.name,
        "storageUuids": [
            item.storage_uuid
            for item in row.storages
            if item.storage_uuid in allowed_storages
        ],
        "generation": resolve_generation(
            db,
            resource_type="storage-pool",
            resource_id=str(row.id),
        ),
    } for row in rows]
    return {"count": len(data), "data": data}


def image_list(db: Session, context: LeaseContext, model: Any, _: Any) -> Any:
    query = db.query(ImageModel).join(StorageModel).order_by(ImageModel.name)
    project_id = getattr(model, "project_id", None)
    if project_id is not None:
        projects = [_agent_project(db, context, project_id)]
    else:
        projects = db.query(ProjectModel).filter(
            ProjectModel.id.in_(_effective_project_ids(db, context)),
        ).all()
    project_conditions = []
    for project in projects:
        storage_ids = {
            association.storage_uuid
            for pool in project.storage_pools
            for association in pool.storages
        }
        flavor_ids = {flavor.id for flavor in project.flavors}
        project_conditions.append(and_(
            ImageModel.storage_uuid.in_(storage_ids),
            or_(
                ImageModel.flavor_id.is_(None),
                ImageModel.flavor_id.in_(flavor_ids),
            ),
        ))
    query = query.filter(
        or_(*project_conditions) if project_conditions else false(),
    )
    if context.lease.node_ids:
        query = query.filter(StorageModel.node_name.in_(context.lease.node_ids))
    if getattr(model, "pool_uuid", None):
        query = query.filter(ImageModel.storage_uuid == model.pool_uuid)
    if getattr(model, "node_name", None):
        query = query.filter(StorageModel.node_name == model.node_name)
    if getattr(model, "name", None):
        query = query.filter(ImageModel.name == model.name)
    if getattr(model, "name_like", None):
        query = query.filter(ImageModel.name.like(f"%{model.name_like}%"))
    count, rows = _page(query, model)
    return {"count": count, "data": [_image_dict(row) for row in rows]}


def network_list(db: Session, context: LeaseContext, model: Any, _: Any) -> Any:
    query = db.query(NetworkModel).order_by(NetworkModel.name)
    project_id = getattr(model, "project_id", None)
    allowed = _allowed_network_ids(db, context, project_id)
    query = query.filter(NetworkModel.uuid.in_(allowed))
    if getattr(model, "name_like", None):
        query = query.filter(NetworkModel.name.like(f"%{model.name_like}%"))
    if getattr(model, "node_name_like", None):
        query = query.filter(NetworkModel.node_name.like(f"%{model.node_name_like}%"))
    if getattr(model, "type", None):
        query = query.filter(NetworkModel.type == model.type)
    count, rows = _page(query, model)
    return {
        "count": count,
        "data": [
            _network_dict(
                row,
                _allowed_network_port_names(
                    db,
                    context,
                    row.uuid,
                    project_id,
                ),
            )
            for row in rows
        ],
    }


def network_get(db: Session, context: LeaseContext, __: Any, target: Any) -> Any:
    row = db.get(NetworkModel, _require_resource_id(target))
    target_project_id = getattr(target, "project_id", None)
    if row is None or row.uuid not in _allowed_network_ids(
        db,
        context,
        target_project_id,
    ):
        raise NotFoundError("network_not_found", "networkがありません")
    return _network_dict(
        row,
        _allowed_network_port_names(
            db,
            context,
            row.uuid,
            target_project_id,
        ),
    )


def network_xml(db: Session, context: LeaseContext, __: Any, target: Any) -> Any:
    resource_id = _require_resource_id(target)
    target_project_id = getattr(target, "project_id", None)
    if (
        db.get(NetworkModel, resource_id) is None
        or resource_id not in _allowed_network_ids(
            db,
            context,
            target_project_id,
        )
    ):
        raise NotFoundError("network_not_found", "networkがありません")
    if _allowed_network_port_names(
        db,
        context,
        resource_id,
        target_project_id,
    ) is not None:
        raise NotFoundError(
            "network_xml_not_found",
            "port単位grantではnetwork XMLを取得できません",
        )
    try:
        xml = Path(join(DATA_ROOT, "xml/network", f"{resource_id}.xml")).read_text()
    except FileNotFoundError as exc:
        raise NotFoundError("network_xml_not_found", "network XMLがありません") from exc
    return {"xml": xml}


def network_pool_list(db: Session, context: LeaseContext, model: Any, _: Any) -> Any:
    project_id = getattr(model, "project_id", None)
    query = db.query(NetworkPoolModel).filter(
        NetworkPoolModel.id.in_(
            _allowed_network_pool_ids(db, context, project_id),
        ),
    ).order_by(NetworkPoolModel.id)
    rows = query.all()
    allowed_networks = _allowed_network_ids(db, context, project_id)
    if context.lease.node_ids:
        rows = [
            row
            for row in rows
            if {
                network.uuid
                for network in [
                    *row.networks,
                    *(port.network for port in row.ports),
                ]
            }.intersection(allowed_networks)
        ]
    data = [{
        "id": row.id,
        "name": row.name,
        "networkUuids": [
            network.uuid
            for network in row.networks
            if network.uuid in allowed_networks
        ],
        "ports": [
            {"networkUuid": port.network_uuid, "name": port.name}
            for port in row.ports
            if port.network_uuid in allowed_networks
        ],
        "generation": resolve_generation(
            db,
            resource_type="network-pool",
            resource_id=str(row.id),
        ),
    } for row in rows]
    return {"count": len(data), "data": data}


def project_list(db: Session, context: LeaseContext, model: Any, _: Any) -> Any:
    query = db.query(ProjectModel).order_by(ProjectModel.name)
    if context.lease.node_ids:
        # projectはnode単独制約から安全に完全対応付けできない。
        query = query.filter(false())
    query = query.filter(ProjectModel.id.in_(_effective_project_ids(db, context)))
    if getattr(model, "name_like", None):
        query = query.filter(ProjectModel.name.like(f"%{model.name_like}%"))
    count, rows = _page(query, model)
    return {"count": count, "data": [_project_dict(db, row) for row in rows]}


def project_get(db: Session, context: LeaseContext, __: Any, target: Any) -> Any:
    project = _agent_project(db, context, _require_resource_id(target))
    return _project_dict(db, project)


def project_member_candidates(
    db: Session,
    context: LeaseContext,
    model: Any,
    target: Any,
) -> Any:
    project = _agent_project(db, context, _require_resource_id(target))
    member_names = [user.username for user in project.users]
    query = db.query(UserModel).filter(
        UserModel.username.notin_(member_names),
    ).order_by(UserModel.username)
    if model.name_like:
        query = query.filter(UserModel.username.like(f"%{model.name_like}%"))
    count, rows = _page(query, model)
    return {
        "count": count,
        "data": [{"username": user.username} for user in rows],
    }


def project_resource_grant_candidates(
    db: Session,
    context: LeaseContext,
    model: Any,
    _: Any,
) -> Any:
    """global adminへ現在存在する全pool/flavor候補をtyped fieldで返す。"""

    if not _is_admin(db, context.principal_id):
        raise AuthorizationError(
            "global_admin_required",
            "Project resource grant候補の取得にはglobal adminが必要です",
        )
    _agent_project(db, context, model.project_id, allow_admin=True)

    def reference(resource: Any) -> dict[str, Any]:
        return {"id": resource.id, "name": resource.name or f"Pool {resource.id}"}

    return {
        "storagePools": [
            reference(pool)
            for pool in db.query(StoragePoolModel).order_by(StoragePoolModel.id)
        ],
        "networkPools": [
            reference(pool)
            for pool in db.query(NetworkPoolModel).order_by(NetworkPoolModel.id)
        ],
        "flavors": [
            {"id": flavor.id, "name": flavor.name}
            for flavor in db.query(FlavorModel).order_by(FlavorModel.id)
        ],
    }


def user_me(db: Session, context: LeaseContext, __: Any, ___: Any) -> Any:
    row = db.get(UserModel, context.principal_id)
    if row is None:
        raise NotFoundError("principal_not_found", "principalがありません")
    return _user_dict(db, row)


def user_list(db: Session, context: LeaseContext, model: Any, __: Any) -> Any:
    _deny_global_read_when_scoped(context)
    query = db.query(UserModel).order_by(UserModel.username)
    if getattr(model, "name_like", None):
        query = query.filter(UserModel.username.like(f"%{model.name_like}%"))
    count, rows = _page(query, model)
    return {"count": count, "data": [_user_dict(db, row) for row in rows]}


def task_list(db: Session, context: LeaseContext, model: Any, _: Any) -> Any:
    _deny_global_read_when_scoped(context)
    query = db.query(TaskModel).filter(TaskModel.archived_at.is_(None))
    query = query.filter(
        or_(
            TaskModel.principal_id == context.principal_id,
            and_(
                TaskModel.principal_id.is_(None),
                TaskModel.user_id == context.principal_id,
            ),
        )
    )
    for field in ("resource", "object", "method"):
        value = getattr(model, field, None)
        if value:
            query = query.filter(getattr(TaskModel, field) == value)
    status = getattr(model, "status", None)
    if status == "incomplete":
        query = query.filter(TaskModel.status.notin_(ARCHIVABLE_STATUSES))
    elif status:
        query = query.filter(TaskModel.status == status)
    query = query.order_by(TaskModel.post_time.desc())
    count, rows = _page(query, model)
    return {"count": count, "data": [_task_dict(row) for row in rows]}


def task_get(db: Session, context: LeaseContext, __: Any, target: Any) -> Any:
    row = db.get(TaskModel, _require_resource_id(target))
    if row is None:
        raise NotFoundError("task_not_found", "taskがありません")
    if (row.principal_id or row.user_id) != context.principal_id:
        raise AuthorizationError("task_ownership_denied", "別principalのtaskです")
    return _task_dict(row)


def task_incomplete(db: Session, context: LeaseContext, model: Any, __: Any) -> Any:
    _deny_global_read_when_scoped(context)
    query = db.query(TaskModel.uuid, TaskModel.status).filter(
        TaskModel.archived_at.is_(None),
        TaskModel.status.notin_(ARCHIVABLE_STATUSES),
    )
    query = query.filter(
        or_(
            TaskModel.principal_id == context.principal_id,
            and_(
                TaskModel.principal_id.is_(None),
                TaskModel.user_id == context.principal_id,
            ),
        )
    )
    rows = query.order_by(TaskModel.uuid).all()
    import hashlib

    digest = hashlib.md5(
        ";".join(f"{uuid}:{status}" for uuid, status in rows).encode(),
        usedforsecurity=False,
    ).hexdigest()
    return {"hash": digest, "count": len(rows), "uuids": [row[0] for row in rows]}


def flavor_list(db: Session, context: LeaseContext, model: Any, _: Any) -> Any:
    query = db.query(FlavorModel).order_by(FlavorModel.name)
    if context.lease.node_ids:
        query = query.filter(false())
    query = query.filter(FlavorModel.id.in_(_allowed_flavor_ids(
        db,
        context,
        getattr(model, "project_id", None),
    )))
    if getattr(model, "name_like", None):
        query = query.filter(FlavorModel.name.like(f"%{model.name_like}%"))
    count, rows = _page(query, model)
    return {"count": count, "data": [_flavor_dict(db, row) for row in rows]}


def metrics_get(db: Session, context: LeaseContext, __: Any, ___: Any) -> Any:
    _deny_global_read_when_scoped(context)
    vm = db.query(
        func.count(DomainModel.uuid),
        func.coalesce(func.sum(DomainModel.core), 0),
        func.coalesce(func.sum(DomainModel.memory), 0),
    ).one()
    task = db.query(
        func.count(TaskModel.uuid),
        func.coalesce(func.sum(TaskModel.run_time), 0),
    ).one()
    statuses = db.query(TaskModel.status, func.count(TaskModel.uuid)).group_by(
        TaskModel.status
    ).all()
    return {
        "vmCount": vm[0],
        "vmCpus": vm[1],
        "vmMemoryMiB": vm[2],
        "taskCount": task[0],
        "taskRuntimeSeconds": task[1],
        "tasksByStatus": {status: count for status, count in statuses},
    }


def system_version(db: Session, _: LeaseContext, __: Any, ___: Any) -> Any:
    return {"initialized": db.query(UserModel).first() is not None, "version": API_VERSION}


# 以下は同期direct mutation。commitはorchestratorだけが行う。


def node_ssh_key_write(db: Session, _: LeaseContext, model: Any, __: Any) -> Any:
    del db
    from node.router import SSH_DIRECTORY, _install_ssh_key_pair

    if model.generate:
        SSH_DIRECTORY.mkdir(mode=0o700, parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(
            prefix=".virty-agent-generate-",
            dir=SSH_DIRECTORY,
        ) as temp:
            generated = Path(temp) / "id_ed25519"
            subprocess.run(
                [
                    "ssh-keygen",
                    "-t",
                    "ed25519",
                    "-f",
                    str(generated),
                    "-N",
                    "",
                    "-q",
                ],
                check=True,
            )
            _install_ssh_key_pair(
                key_name="id_ed25519",
                private_key=generated.read_text(encoding="utf-8"),
                public_key=generated.with_suffix(".pub").read_text(
                    encoding="utf-8",
                ),
            )
    else:
        if not model.private_key or not model.public_key:
            raise ConflictError(
                "ssh_key_pair_required",
                "generate=falseではprivateKeyとpublicKeyが必要です",
            )
        try:
            private_key = serialization.load_ssh_private_key(
                model.private_key.encode(),
                password=None,
            )
        except (TypeError, ValueError) as exc:
            raise ConflictError("invalid_ssh_private_key", "SSH秘密鍵形式が不正です") from exc
        if isinstance(private_key, rsa.RSAPrivateKey):
            key_name = "id_rsa"
        elif isinstance(private_key, ed25519.Ed25519PrivateKey):
            key_name = "id_ed25519"
        else:
            raise ConflictError("unsupported_ssh_key", "未対応のSSH鍵形式です")
        derived_public_key = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH,
        ).decode("ascii")
        if model.public_key.strip().split()[:2] != derived_public_key.split()[:2]:
            raise ConflictError(
                "ssh_public_key_mismatch",
                "SSH公開鍵が秘密鍵と一致しません",
            )
        _install_ssh_key_pair(
            key_name=key_name,
            private_key=model.private_key,
            public_key=derived_public_key,
        )
    return {"configured": True}


def vm_project_update(
    db: Session,
    context: LeaseContext,
    model: Any,
    __: Any,
) -> Any:
    _require_allowed_vm(db, context, model.uuid)
    _agent_project(db, context, model.project_id)

    def authorize_locked(vm: DomainModel, project: ProjectModel) -> bool:
        effective_project_ids = _effective_project_ids(db, context)
        personal_allowed = (
            not context.lease.project_ids
            and vm.owner_user_id == context.principal_id
            and vm.owner_project_id is None
        )
        project_allowed = (
            vm.owner_project_id is not None
            and vm.owner_project_id in effective_project_ids
        )
        node_allowed = (
            not context.lease.node_ids
            or vm.node_name in context.lease.node_ids
        )
        return (
            node_allowed
            and (personal_allowed or project_allowed)
            and project.id in effective_project_ids
        )

    try:
        vm = move_domain_to_project(
            db,
            domain_uuid=model.uuid,
            destination_project_id=model.project_id,
            authorize_locked=authorize_locked,
        )
    except DomainProjectMoveNotFoundError as exc:
        raise NotFoundError(
            "vm_or_project_not_found",
            "VMまたはprojectがありません",
        ) from exc
    except DomainProjectMoveConflictError as exc:
        raise ConflictError(
            "vm_project_resource_conflict",
            "移動先projectへgrantされていないVM resourceがあります: "
            + ", ".join(exc.conflicts),
        ) from exc
    return _vm_dict(vm)


def storage_metadata_update(db: Session, _: LeaseContext, model: Any, __: Any) -> Any:
    storage = db.get(StorageModel, model.uuid)
    if storage is None:
        raise NotFoundError("storage_not_found", "storageがありません")
    metadata = db.get(StorageMetadataModel, model.uuid)
    if metadata is None:
        metadata = StorageMetadataModel(uuid=model.uuid)
        db.add(metadata)
    metadata.rool = model.rool
    metadata.protocol = model.protocol
    metadata.device_type = model.device_type
    db.flush()
    return _storage_dict(storage)


def storage_pool_create(db: Session, _: LeaseContext, model: Any, __: Any) -> Any:
    pool = StoragePoolModel(name=model.name)
    db.add(pool)
    db.flush()
    for storage_uuid in model.storage_uuids:
        if db.get(StorageModel, storage_uuid) is None:
            raise NotFoundError("storage_not_found", f"storageがありません: {storage_uuid}")
        db.add(AssociationStoragePoolModel(pool_id=pool.id, storage_uuid=storage_uuid))
    db.flush()
    return {"id": pool.id, "name": pool.name, "storageUuids": model.storage_uuids}


def storage_pool_update(db: Session, _: LeaseContext, model: Any, __: Any) -> Any:
    storage_uuids = set(model.storage_uuids)
    for storage_uuid in storage_uuids:
        if db.get(StorageModel, storage_uuid) is None:
            raise NotFoundError("storage_not_found", f"storageがありません: {storage_uuid}")
    try:
        pool = ensure_storage_pool_update_allowed(
            db,
            int(model.id),
            storage_uuids,
        )
    except ProjectGrantNotFoundError as exc:
        raise NotFoundError("storage_pool_not_found", str(exc)) from exc
    except ProjectConflictError as exc:
        raise ConflictError("storage_pool_in_use", str(exc)) from exc
    db.query(AssociationStoragePoolModel).filter(
        AssociationStoragePoolModel.pool_id == pool.id
    ).delete(synchronize_session=False)
    for storage_uuid in sorted(storage_uuids):
        db.add(AssociationStoragePoolModel(pool_id=pool.id, storage_uuid=storage_uuid))
    db.flush()
    return {"id": pool.id, "name": pool.name, "storageUuids": sorted(storage_uuids)}


def storage_pool_delete(db: Session, _: LeaseContext, model: Any, __: Any) -> Any:
    try:
        pool = ensure_storage_pool_deletable(db, int(model.id))
    except ProjectGrantNotFoundError as exc:
        raise NotFoundError("storage_pool_not_found", str(exc)) from exc
    except ProjectConflictError as exc:
        raise ConflictError("storage_pool_in_use", str(exc)) from exc
    result = {"deleted": True, "id": pool.id}
    remove_storage_pool(db, pool)
    db.flush()
    return result


def image_flavor_update(
    db: Session,
    context: LeaseContext,
    model: Any,
    __: Any,
) -> Any:
    project = _agent_project(db, context, model.project_id, lock=True)
    if context.lease.project_ids and project.id not in context.lease.project_ids:
        raise AuthorizationError(
            "project_constraint_denied",
            "対象Projectは能力leaseの制約外です",
        )
    image = db.query(ImageModel).filter(
        ImageModel.storage_uuid == model.storage_uuid,
        ImageModel.path == model.path,
    ).one_or_none()
    if image is None or db.get(FlavorModel, model.flavor_id) is None:
        raise NotFoundError("image_or_flavor_not_found", "imageまたはflavorがありません")
    if image.storage.node_name != model.node_name:
        raise NotFoundError("image_not_found", "imageがありません")
    if image.storage_uuid not in {
        association.storage_uuid
        for pool in project.storage_pools
        for association in pool.storages
    } or model.flavor_id not in {flavor.id for flavor in project.flavors}:
        raise AuthorizationError(
            "image_project_grant_denied",
            "imageのstorageとflavorは同じProjectにgrantされている必要があります",
        )
    image.flavor_id = model.flavor_id
    db.flush()
    return _image_dict(image)


def network_pool_create(db: Session, _: LeaseContext, model: Any, __: Any) -> Any:
    pool = NetworkPoolModel(name=model.name)
    db.add(pool)
    db.flush()
    return {"id": pool.id, "name": pool.name}


def network_pool_update(db: Session, _: LeaseContext, model: Any, __: Any) -> Any:
    pool = db.get(NetworkPoolModel, model.pool_id)
    if pool is None:
        raise NotFoundError("network_pool_not_found", "network poolがありません")
    if model.port_name is not None:
        port = db.query(NetworkPortgroupModel).filter(
            NetworkPortgroupModel.network_uuid == model.network_uuid,
            NetworkPortgroupModel.name == model.port_name,
        ).one_or_none()
        if port is None:
            raise NotFoundError("network_port_not_found", "network portがありません")
        if port not in pool.ports:
            pool.ports.append(port)
    else:
        network = db.get(NetworkModel, model.network_uuid)
        if network is None:
            raise NotFoundError("network_not_found", "networkがありません")
        if network not in pool.networks:
            pool.networks.append(network)
    db.flush()
    return {"id": pool.id, "name": pool.name}


def network_pool_delete(db: Session, _: LeaseContext, model: Any, __: Any) -> Any:
    try:
        pool = ensure_network_pool_deletable(db, model.id)
    except ProjectGrantNotFoundError as exc:
        raise NotFoundError("network_pool_not_found", str(exc)) from exc
    except ProjectConflictError as exc:
        raise ConflictError("network_pool_in_use", str(exc)) from exc
    db.delete(pool)
    db.flush()
    return {"deleted": True, "id": model.id}


def _agent_project(
    db: Session,
    context: LeaseContext,
    project_id: str,
    *,
    allow_admin: bool = False,
    lock: bool = False,
) -> ProjectModel:
    project: ProjectModel | None
    if lock:
        try:
            project = lock_project(db, project_id)
        except ProjectNotFoundError as exc:
            raise NotFoundError(
                "project_not_found",
                "projectがありません",
            ) from exc
    else:
        project = db.get(ProjectModel, project_id)
    if project is None:
        raise NotFoundError("project_not_found", "projectがありません")
    if project.id in _effective_project_ids(db, context):
        return project
    if allow_admin and _is_admin(db, context.principal_id):
        return project
    raise NotFoundError("project_not_found", "projectがありません")


def project_update(db: Session, context: LeaseContext, model: Any, __: Any) -> Any:
    project = _agent_project(db, context, model.project_id, lock=True)
    try:
        rename_project(project, model.name)
    except ProjectConflictError as exc:
        raise ConflictError("project_update_conflict", str(exc)) from exc
    db.flush()
    return _project_dict(db, project)


def project_member_add(
    db: Session,
    context: LeaseContext,
    model: Any,
    __: Any,
) -> Any:
    project = _agent_project(db, context, model.project_id, lock=True)
    try:
        add_project_member(db, project, model.username)
    except ProjectMemberNotFoundError as exc:
        raise NotFoundError("project_member_not_found", str(exc)) from exc
    db.flush()
    return _project_dict(db, project)


def project_member_remove(
    db: Session,
    context: LeaseContext,
    model: Any,
    __: Any,
) -> Any:
    project = _agent_project(db, context, model.project_id, lock=True)
    try:
        remove_project_member(project, model.username)
    except ProjectConflictError as exc:
        raise ConflictError("project_member_conflict", str(exc)) from exc
    db.flush()
    return _project_dict(db, project)


def project_resource_grants_update(
    db: Session,
    context: LeaseContext,
    model: Any,
    __: Any,
) -> Any:
    if not _is_admin(db, context.principal_id):
        raise AuthorizationError(
            "global_admin_required",
            "Project resource grant更新にはglobal adminが必要です",
        )
    project = _agent_project(
        db,
        context,
        model.project_id,
        allow_admin=True,
        lock=True,
    )
    request = ProjectResourceGrantsUpdate.model_validate(
        model.model_dump(exclude={"project_id"}),
    )
    try:
        replace_project_resource_grants(db, project, request)
    except ProjectGrantNotFoundError as exc:
        raise NotFoundError("project_grant_not_found", str(exc)) from exc
    except ProjectConflictError as exc:
        raise ConflictError("project_grant_conflict", str(exc)) from exc
    db.flush()
    return _project_dict(db, project)


def user_create(db: Session, _: LeaseContext, model: Any, __: Any) -> Any:
    if db.get(UserModel, model.username) is not None:
        raise ConflictError("user_exists", "userは既に存在します")
    user = UserModel(
        username=model.username,
        hashed_password=get_password_hash(model.password),
    )
    db.add(user)
    scopes = {scope.name for scope in model.scopes} | {"user"}
    for scope in scopes:
        db.add(UserScopeModel(user_id=user.username, name=scope))
    for key in model.publickeys:
        db.add(UserPublickeyModel(
            user_id=user.username,
            name=key.name,
            publickey=key.publickey,
        ))
    db.flush()
    db.expire(user)
    return _user_dict(db, user)


def user_update(db: Session, _: LeaseContext, model: Any, __: Any) -> Any:
    if model.path_username != model.username:
        raise ConflictError(
            "username_mismatch",
            "pathUsernameとusernameは一致する必要があります",
        )
    user = db.get(UserModel, model.path_username)
    if user is None:
        raise NotFoundError("user_not_found", "userがありません")
    user.hashed_password = get_password_hash(model.password)
    user.publickeys = [
        UserPublickeyModel(name=key.name, publickey=key.publickey)
        for key in model.publickeys
    ]
    existing_scopes = {item.name: item for item in user.scopes}
    requested_scopes = {item.name for item in model.scopes}
    if would_remove_last_admin(db, user.username, requested_scopes):
        raise ConflictError(
            "last_admin_required",
            "最後の管理者からadmin scopeを削除できません",
        )
    for name in existing_scopes.keys() - requested_scopes:
        db.delete(existing_scopes[name])
    for name in requested_scopes - existing_scopes.keys():
        db.add(UserScopeModel(user_id=user.username, name=name))
    db.flush()
    db.expire(user)
    return _user_dict(db, user)


def user_delete(db: Session, context: LeaseContext, model: Any, __: Any) -> Any:
    if model.username == context.principal_id:
        raise AuthorizationError(
            "self_delete_denied",
            "Agentは自身のbreak-glass principalを削除できません",
        )
    user = db.get(UserModel, model.username)
    if user is None:
        raise NotFoundError("user_not_found", "userがありません")
    if would_remove_last_admin(db, user.username, None):
        raise ConflictError(
            "last_admin_required",
            "最後の管理者は削除できません",
        )
    try:
        ensure_user_memberships_deletable(db, user.username)
    except ProjectConflictError as exc:
        raise ConflictError("last_project_member_required", str(exc)) from exc
    db.delete(user)
    db.flush()
    return {"deleted": True, "username": model.username}


def task_delete_all(db: Session, _: LeaseContext, __: Any, ___: Any) -> Any:
    rows = archive_terminal_tasks(db)
    return {"archived": len(rows)}


def flavor_create(db: Session, _: LeaseContext, model: Any, __: Any) -> Any:
    if db.query(FlavorModel).filter(FlavorModel.name == model.name).first():
        raise ConflictError("flavor_exists", "flavorは既に存在します")
    flavor = FlavorModel(**model.model_dump())
    db.add(flavor)
    db.flush()
    return _flavor_dict(db, flavor)


def flavor_delete(db: Session, _: LeaseContext, model: Any, __: Any) -> Any:
    try:
        flavor = ensure_flavor_deletable(db, model.flavor_id)
    except ProjectGrantNotFoundError as exc:
        raise NotFoundError("flavor_not_found", str(exc)) from exc
    except ProjectConflictError as exc:
        raise ConflictError("flavor_in_use", str(exc)) from exc
    result = {"deleted": True, "id": flavor.id, "name": flavor.name}
    db.delete(flavor)
    db.flush()
    return result


READ_ADAPTERS: dict[str, Callable[..., Any]] = {
    name: value
    for name, value in globals().copy().items()
    if callable(value) and name in {
        "node_list", "node_get", "node_facts", "node_info", "node_ssh_public_key",
        "vm_list", "vm_get", "vm_xml", "storage_list", "storage_get",
        "storage_pool_list", "image_list", "network_list", "network_get",
        "network_xml", "network_pool_list", "project_list", "project_get",
        "project_member_candidates", "project_resource_grant_candidates",
        "user_me", "user_list",
        "task_list", "task_get", "task_incomplete", "flavor_list", "metrics_get",
        "system_version",
    }
}

DIRECT_ADAPTERS: dict[str, Callable[..., Any]] = {
    name: value
    for name, value in globals().copy().items()
    if callable(value) and name in {
        "node_ssh_key_write", "vm_project_update", "storage_metadata_update",
        "storage_pool_create", "storage_pool_update", "storage_pool_delete",
        "image_flavor_update",
        "network_pool_create", "network_pool_update", "network_pool_delete",
        "project_update", "project_member_add", "project_member_remove",
        "project_resource_grants_update", "user_create", "user_update", "user_delete",
        "task_delete_all", "flavor_create", "flavor_delete",
    }
}
