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
from sqlalchemy import func, or_
from sqlalchemy.orm import Query, Session

from auth.function import get_password_hash
from domain.models import DomainModel
from flavor.models import FlavorModel
from network.models import NetworkModel, NetworkPoolModel, NetworkPortgroupModel
from node.models import NodeModel
from project.models import ProjectModel
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
    association_users_to_projects,
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
            model._sa_instance_state.session,
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
            model._sa_instance_state.session,
            resource_type="vm",
            resource_id=model.uuid,
        ),
    }


def _network_dict(model: NetworkModel) -> dict[str, Any]:
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
        ],
        "generation": resolve_generation(
            model._sa_instance_state.session,
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
            model._sa_instance_state.session,
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
            model._sa_instance_state.session,
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
        func.coalesce(func.sum(DomainModel.memory), 0),
        func.coalesce(func.sum(DomainModel.core), 0),
    ).filter(DomainModel.owner_project_id == model.id).one()
    return {
        "id": model.id,
        "name": model.name,
        "isAdmin": model.is_admin,
        "limits": {
            "cores": model.core,
            "memoryGiB": model.memory_g,
            "storageGiB": model.storage_capacity_g,
        },
        "usage": {"memoryMiB": int(used[0]), "cores": int(used[1])},
        "users": [user.username for user in model.users],
        "networkPoolIds": [pool.id for pool in model.network_pools],
        "storagePoolIds": [pool.id for pool in model.storage_pools],
        "flavorIds": [flavor.id for flavor in model.flavors],
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
            model._sa_instance_state.session,
            resource_type="task",
            resource_id=model.uuid,
        ),
    }


def _allowed_storage_ids(db: Session, context: LeaseContext) -> set[str] | None:
    constraints: list[set[str]] = []
    if context.lease.node_ids:
        constraints.append({
            row[0]
            for row in db.query(StorageModel.uuid).filter(
                StorageModel.node_name.in_(context.lease.node_ids)
            )
        })
    if context.lease.project_ids:
        projects = db.query(ProjectModel).filter(
            ProjectModel.id.in_(context.lease.project_ids)
        ).all()
        constraints.append({
            association.storage_uuid
            for project in projects
            for pool in project.storage_pools
            for association in pool.storages
        })
    return set.intersection(*constraints) if constraints else None


def _allowed_network_ids(db: Session, context: LeaseContext) -> set[str] | None:
    constraints: list[set[str]] = []
    if context.lease.node_ids:
        constraints.append({
            row[0]
            for row in db.query(NetworkModel.uuid).filter(
                NetworkModel.node_name.in_(context.lease.node_ids)
            )
        })
    if context.lease.project_ids:
        projects = db.query(ProjectModel).filter(
            ProjectModel.id.in_(context.lease.project_ids)
        ).all()
        constraints.append({
            network.uuid
            for project in projects
            for pool in project.network_pools
            for network in [*pool.networks, *(port.network for port in pool.ports)]
        })
    return set.intersection(*constraints) if constraints else None


def _allowed_project_node_ids(db: Session, context: LeaseContext) -> set[str] | None:
    if not context.lease.project_ids:
        return None
    projects = db.query(ProjectModel).filter(
        ProjectModel.id.in_(context.lease.project_ids),
    ).all()
    result = {
        vm.node_name
        for vm in db.query(DomainModel).filter(
            DomainModel.owner_project_id.in_(context.lease.project_ids),
        )
        if vm.node_name is not None
    }
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
    return result


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


def node_list(db: Session, context: LeaseContext, model: Any, _: Any) -> Any:
    query = db.query(NodeModel).order_by(NodeModel.name)
    allowed_project_nodes = _allowed_project_node_ids(db, context)
    if context.lease.node_ids:
        query = query.filter(NodeModel.name.in_(context.lease.node_ids))
    if allowed_project_nodes is not None:
        query = query.filter(NodeModel.name.in_(allowed_project_nodes))
    if getattr(model, "name_like", None):
        query = query.filter(NodeModel.name.like(f"%{model.name_like}%"))
    count, rows = _page(query, model)
    return {"count": count, "data": [_node_dict(row) for row in rows]}


def node_get(db: Session, _: LeaseContext, __: Any, target: Any) -> Any:
    row = db.get(NodeModel, _require_resource_id(target))
    if row is None:
        raise NotFoundError("node_not_found", "nodeがありません")
    return _node_dict(row)


def node_facts(db: Session, _: LeaseContext, __: Any, target: Any) -> Any:
    row = db.get(NodeModel, _require_resource_id(target))
    if row is None:
        raise NotFoundError("node_not_found", "nodeがありません")
    return row.ansible_facts


def node_info(db: Session, _: LeaseContext, __: Any, target: Any) -> Any:
    from module.paramikolib import ParamikoManager

    row = db.get(NodeModel, _require_resource_id(target))
    if row is None:
        raise NotFoundError("node_not_found", "nodeがありません")
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
    if context.lease.project_ids:
        query = query.filter(DomainModel.owner_project_id.in_(context.lease.project_ids))
    elif not _is_admin(db, context.principal_id):
        query = query.filter(DomainModel.owner_user_id == context.principal_id)
    if context.lease.node_ids:
        query = query.filter(DomainModel.node_name.in_(context.lease.node_ids))
    if getattr(model, "name_like", None):
        query = query.filter(DomainModel.name.like(f"%{model.name_like}%"))
    if getattr(model, "node_name_like", None):
        query = query.filter(DomainModel.node_name.like(f"%{model.node_name_like}%"))
    count, rows = _page(query, model)
    return {"count": count, "data": [_vm_dict(row) for row in rows]}


def vm_get(db: Session, _: LeaseContext, __: Any, target: Any) -> Any:
    row = db.get(DomainModel, _require_resource_id(target))
    if row is None:
        raise NotFoundError("vm_not_found", "VMがありません")
    return _vm_dict(row)


def vm_xml(db: Session, _: LeaseContext, __: Any, target: Any) -> Any:
    from module.xmllib import redact_domain_xml_secrets

    resource_id = _require_resource_id(target)
    if db.get(DomainModel, resource_id) is None:
        raise NotFoundError("vm_not_found", "VMがありません")
    try:
        xml = Path(join(DATA_ROOT, "xml/domain", f"{resource_id}.xml")).read_text()
    except FileNotFoundError as exc:
        raise NotFoundError("vm_xml_not_found", "VM XMLがありません") from exc
    return {"xml": redact_domain_xml_secrets(xml)}


def storage_list(db: Session, context: LeaseContext, model: Any, _: Any) -> Any:
    query = db.query(StorageModel).order_by(StorageModel.name, StorageModel.node_name)
    allowed = _allowed_storage_ids(db, context)
    if allowed is not None:
        query = query.filter(StorageModel.uuid.in_(allowed))
    if getattr(model, "node_name", None):
        query = query.filter(StorageModel.node_name == model.node_name)
    if getattr(model, "name_like", None):
        query = query.filter(StorageModel.name.like(f"%{model.name_like}%"))
    count, rows = _page(query, model)
    return {"count": count, "data": [_storage_dict(row) for row in rows]}


def storage_get(db: Session, _: LeaseContext, __: Any, target: Any) -> Any:
    row = db.get(StorageModel, _require_resource_id(target))
    if row is None:
        raise NotFoundError("storage_not_found", "storageがありません")
    return _storage_dict(row)


def storage_pool_list(db: Session, context: LeaseContext, __: Any, ___: Any) -> Any:
    query = db.query(StoragePoolModel).order_by(StoragePoolModel.id)
    if context.lease.project_ids:
        allowed = {
            pool.id
            for project in db.query(ProjectModel).filter(
                ProjectModel.id.in_(context.lease.project_ids)
            )
            for pool in project.storage_pools
        }
        query = query.filter(StoragePoolModel.id.in_(allowed))
    rows = query.all()
    allowed_storages = _allowed_storage_ids(db, context)
    if allowed_storages is not None:
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
            if allowed_storages is None or item.storage_uuid in allowed_storages
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
    allowed = _allowed_storage_ids(db, context)
    if allowed is not None:
        query = query.filter(ImageModel.storage_uuid.in_(allowed))
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
    allowed = _allowed_network_ids(db, context)
    if allowed is not None:
        query = query.filter(NetworkModel.uuid.in_(allowed))
    if getattr(model, "name_like", None):
        query = query.filter(NetworkModel.name.like(f"%{model.name_like}%"))
    if getattr(model, "node_name_like", None):
        query = query.filter(NetworkModel.node_name.like(f"%{model.node_name_like}%"))
    if getattr(model, "type", None):
        query = query.filter(NetworkModel.type == model.type)
    count, rows = _page(query, model)
    return {"count": count, "data": [_network_dict(row) for row in rows]}


def network_get(db: Session, _: LeaseContext, __: Any, target: Any) -> Any:
    row = db.get(NetworkModel, _require_resource_id(target))
    if row is None:
        raise NotFoundError("network_not_found", "networkがありません")
    return _network_dict(row)


def network_xml(db: Session, _: LeaseContext, __: Any, target: Any) -> Any:
    resource_id = _require_resource_id(target)
    if db.get(NetworkModel, resource_id) is None:
        raise NotFoundError("network_not_found", "networkがありません")
    try:
        xml = Path(join(DATA_ROOT, "xml/network", f"{resource_id}.xml")).read_text()
    except FileNotFoundError as exc:
        raise NotFoundError("network_xml_not_found", "network XMLがありません") from exc
    return {"xml": xml}


def network_pool_list(db: Session, context: LeaseContext, __: Any, ___: Any) -> Any:
    query = db.query(NetworkPoolModel).order_by(NetworkPoolModel.id)
    if context.lease.project_ids:
        allowed = {
            pool.id
            for project in db.query(ProjectModel).filter(
                ProjectModel.id.in_(context.lease.project_ids)
            )
            for pool in project.network_pools
        }
        query = query.filter(NetworkPoolModel.id.in_(allowed))
    rows = query.all()
    allowed_networks = _allowed_network_ids(db, context)
    if allowed_networks is not None:
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
            if allowed_networks is None or network.uuid in allowed_networks
        ],
        "ports": [
            {"networkUuid": port.network_uuid, "name": port.name}
            for port in row.ports
            if allowed_networks is None or port.network_uuid in allowed_networks
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
        query = query.filter(False)
    if context.lease.project_ids:
        query = query.filter(ProjectModel.id.in_(context.lease.project_ids))
    elif not _is_admin(db, context.principal_id):
        query = query.filter(ProjectModel.users.any(username=context.principal_id))
    if getattr(model, "name_like", None):
        query = query.filter(ProjectModel.name.like(f"%{model.name_like}%"))
    count, rows = _page(query, model)
    return {"count": count, "data": [_project_dict(db, row) for row in rows]}


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
    if not (getattr(model, "admin", False) and _is_admin(db, context.principal_id)):
        query = query.filter(
            or_(
                TaskModel.principal_id == context.principal_id,
                TaskModel.user_id == context.principal_id,
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
    if not _is_admin(db, context.principal_id) and (
        row.principal_id or row.user_id
    ) != context.principal_id:
        raise AuthorizationError("task_ownership_denied", "別principalのtaskです")
    return _task_dict(row)


def task_incomplete(db: Session, context: LeaseContext, model: Any, __: Any) -> Any:
    _deny_global_read_when_scoped(context)
    query = db.query(TaskModel.uuid, TaskModel.status).filter(
        TaskModel.archived_at.is_(None),
        TaskModel.status.notin_(ARCHIVABLE_STATUSES),
    )
    if not (getattr(model, "admin", False) and _is_admin(db, context.principal_id)):
        query = query.filter(
            or_(
                TaskModel.principal_id == context.principal_id,
                TaskModel.user_id == context.principal_id,
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
        query = query.filter(False)
    if context.lease.project_ids:
        allowed = {
            flavor.id
            for project in db.query(ProjectModel).filter(
                ProjectModel.id.in_(context.lease.project_ids)
            )
            for flavor in project.flavors
        }
        query = query.filter(FlavorModel.id.in_(allowed))
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


def vm_project_update(db: Session, _: LeaseContext, model: Any, __: Any) -> Any:
    vm = db.get(DomainModel, model.uuid)
    project = db.get(ProjectModel, model.project_id)
    if vm is None or project is None:
        raise NotFoundError("vm_or_project_not_found", "VMまたはprojectがありません")
    vm.owner_project_id = project.id
    db.flush()
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
    pool = db.get(StoragePoolModel, int(model.id))
    if pool is None:
        raise NotFoundError("storage_pool_not_found", "storage poolがありません")
    db.query(AssociationStoragePoolModel).filter(
        AssociationStoragePoolModel.pool_id == pool.id
    ).delete(synchronize_session=False)
    for storage_uuid in model.storage_uuids:
        if db.get(StorageModel, storage_uuid) is None:
            raise NotFoundError("storage_not_found", f"storageがありません: {storage_uuid}")
        db.add(AssociationStoragePoolModel(pool_id=pool.id, storage_uuid=storage_uuid))
    db.flush()
    return {"id": pool.id, "name": pool.name, "storageUuids": model.storage_uuids}


def image_flavor_update(db: Session, _: LeaseContext, model: Any, __: Any) -> Any:
    image = db.query(ImageModel).filter(
        ImageModel.storage_uuid == model.storage_uuid,
        ImageModel.path == model.path,
    ).one_or_none()
    if image is None or db.get(FlavorModel, model.flavor_id) is None:
        raise NotFoundError("image_or_flavor_not_found", "imageまたはflavorがありません")
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
    pool = db.get(NetworkPoolModel, model.id)
    if pool is None:
        raise NotFoundError("network_pool_not_found", "network poolがありません")
    db.delete(pool)
    db.flush()
    return {"deleted": True, "id": model.id}


def project_member_add(db: Session, _: LeaseContext, model: Any, __: Any) -> Any:
    project = db.get(ProjectModel, model.project_id)
    user = db.get(UserModel, model.user_id)
    if project is None or user is None:
        raise NotFoundError("project_or_user_not_found", "projectまたはuserがありません")
    if user not in project.users:
        project.users.append(user)
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
    _replace_user_projects(db, user.username, [project.name for project in model.projects])
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
    _replace_user_projects(db, user.username, [project.name for project in model.projects])
    db.flush()
    db.expire(user)
    return _user_dict(db, user)


def _replace_user_projects(db: Session, username: str, project_names: list[str]) -> None:
    projects = db.query(ProjectModel).filter(ProjectModel.name.in_(project_names)).all()
    if len(projects) != len(set(project_names)):
        raise NotFoundError("project_not_found", "指定projectがありません")
    db.execute(
        association_users_to_projects.delete().where(
            association_users_to_projects.c.user_id == username
        )
    )
    if projects:
        db.execute(
            association_users_to_projects.insert(),
            [{"user_id": username, "project_id": project.id} for project in projects],
        )


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
    flavor = db.get(FlavorModel, model.flavor_id)
    if flavor is None:
        raise NotFoundError("flavor_not_found", "flavorがありません")
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
        "network_xml", "network_pool_list", "project_list", "user_me", "user_list",
        "task_list", "task_get", "task_incomplete", "flavor_list", "metrics_get",
        "system_version",
    }
}

DIRECT_ADAPTERS: dict[str, Callable[..., Any]] = {
    name: value
    for name, value in globals().copy().items()
    if callable(value) and name in {
        "node_ssh_key_write", "vm_project_update", "storage_metadata_update",
        "storage_pool_create", "storage_pool_update", "image_flavor_update",
        "network_pool_create", "network_pool_update", "network_pool_delete",
        "project_member_add", "user_create", "user_update", "user_delete",
        "task_delete_all", "flavor_create", "flavor_delete",
    }
}
