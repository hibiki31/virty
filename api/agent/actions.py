"""Agent actionのstrict検証、policy、監査、idempotent実行。"""

import importlib
import ipaddress
import json
import os
import socket
import uuid
from dataclasses import replace
from types import SimpleNamespace
from typing import Any
from urllib.parse import urlparse

from pydantic import BaseModel, ValidationError
from sqlalchemy import or_
from sqlalchemy.orm import Session

from task.functions import (
    TaskIdempotencyConflict,
    TaskManager,
    TaskTargetBusy,
    acquire_target_reservations,
    get_operation,
)
from task.models import TaskModel

from .adapters import (
    DIRECT_ADAPTERS,
    READ_ADAPTERS,
    ResolvedTarget,
    _allowed_network_ids,
    _allowed_storage_ids,
)
from .audit import append_audit_event
from .catalog import ACTIONS, PUBLIC_CATALOG, ActionDefinition, get_action
from .crypto import request_hash
from .exceptions import (
    AgentError,
    AuthorizationError,
    ConflictError,
    NotFoundError,
    ServiceUnavailableError,
)
from .policy import (
    LeaseContext,
    authorize_action,
    authorize_operation_access,
    consume_mutation,
    require_scope,
    resolve_generation,
)
from .schemas import ActionRequest, ActionResult, OperationAccepted


def _public_action(action_id: str) -> dict[str, Any]:
    for item in PUBLIC_CATALOG["actions"]:
        if item["action"] == action_id:
            return item
    raise NotFoundError("action_not_found", "action schemaがありません")


def public_input_schema(action_id: str) -> dict[str, Any]:
    item = _public_action(action_id)
    properties: dict[str, Any] = {}
    required: list[str] = []
    parameter_set_name = item.get("parameterSet")
    if parameter_set_name:
        parameter_set = PUBLIC_CATALOG["parameterSets"][parameter_set_name]
        properties.update(parameter_set.get("parameters", {}))
        required.extend(parameter_set.get("required", []))
    properties.update(item.get("parameters", {}))
    required.extend(item.get("required", []))
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": properties,
        "required": list(dict.fromkeys(required)),
        "additionalProperties": False,
    }


def _validate_public_json(action_id: str, value: dict[str, Any]) -> None:
    try:
        from jsonschema import Draft202012Validator
    except ImportError as exc:
        raise ServiceUnavailableError(
            "jsonschema_dependency_missing",
            "Agent strict schema検証libraryがありません",
        ) from exc
    errors = sorted(
        Draft202012Validator(public_input_schema(action_id)).iter_errors(value),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        error = errors[0]
        path = ".".join(str(item) for item in error.absolute_path) or "$"
        # ValidationError.message/input_valueは秘密値を含み得るため公開しない。
        raise AgentError(
            "invalid_action_input",
            f"action inputが不正です: field={path}, rule={error.validator}",
            422,
        )


_PATH_ONLY_FIELDS: dict[str, set[str]] = {
    "task.get": {"uuid"},
    "node.get": {"name"},
    "node.facts": {"name"},
    "node.info": {"name"},
    "node.delete": {"name"},
    "vm.get": {"uuid"},
    "vm.xml.get": {"uuid"},
    "vm.delete": {"uuid"},
    "vm.power.update": {"uuid"},
    "vm.cdrom.update": {"uuid"},
    "vm.network.update": {"uuid"},
    "storage.get": {"uuid"},
    "storage.delete": {"uuid"},
    "network.get": {"uuid"},
    "network.xml.get": {"uuid"},
    "network.delete": {"uuid"},
    "network.ovs.create": {"uuid"},
    "network.ovs.delete": {"uuid"},
}


def _load_input_model(definition: ActionDefinition, value: dict[str, Any]) -> BaseModel:
    from agent.input_models import EmptyInput

    cleaned = {
        key: item
        for key, item in value.items()
        if key not in _PATH_ONLY_FIELDS.get(definition.action_id, set())
    }
    model_type: type[BaseModel]
    if definition.input_model is None:
        model_type = EmptyInput
    else:
        module_name, _, class_name = definition.input_model.rpartition(".")
        model_type = getattr(importlib.import_module(module_name), class_name)
    try:
        return model_type.model_validate(cleaned)
    except ValidationError as exc:
        sanitized = []
        for item in exc.errors(include_input=False, include_url=False):
            sanitized.append({
                "field": ".".join(str(part) for part in item.get("loc", ())) or "$",
                "type": item.get("type", "validation_error"),
            })
        raise AgentError(
            "invalid_action_input",
            f"action inputの型が不正です: {sanitized}",
            422,
        ) from None


def _assert_target_mapping(
    definition: ActionDefinition,
    request: ActionRequest,
) -> None:
    public = _public_action(definition.action_id)
    mapping = public.get("target", {})
    for target_name, input_name in (
        ("resource_id", mapping.get("resourceIdField")),
        ("project_id", mapping.get("projectIdField")),
        ("node_id", mapping.get("nodeIdField")),
    ):
        if input_name is None:
            continue
        expected = request.input.get(input_name)
        actual = getattr(request.target, target_name)
        if expected is None or actual is None or str(expected) != str(actual):
            raise ConflictError(
                "target_mapping_mismatch",
                f"target.{target_name}とinput.{input_name}が一致しません",
            )


def _project_ids_for_resource(
    db: Session,
    *,
    resource_type: str,
    resource_id: str | None,
    node_id: str | None,
) -> set[str]:
    """resource所属をDB relationshipから導出し、client target値を使わない。"""

    if resource_id is None:
        return set()
    from domain.models import DomainModel
    from network.models import NetworkModel
    from project.models import ProjectModel
    from storage.models import StorageModel

    if resource_type == "project":
        return {resource_id} if db.get(ProjectModel, resource_id) is not None else set()
    if resource_type == "vm":
        vm = db.get(DomainModel, resource_id)
        return {vm.owner_project_id} if vm is not None and vm.owner_project_id else set()
    if resource_type == "task":
        task = db.get(TaskModel, resource_id)
        values = [] if task is None else (task.resolved_targets or [])
        if isinstance(values, dict):
            values = [values]
        return {
            str(item["projectId"])
            for item in values
            if isinstance(item, dict) and item.get("projectId") is not None
        }
    storage_uuid: str | None = None
    network_uuid: str | None = None
    pool_id: int | None = None
    flavor_id: int | None = None
    if resource_type == "storage":
        storage_uuid = resource_id
    elif resource_type == "image":
        try:
            storage_uuid, _ = json.loads(resource_id)
        except (TypeError, ValueError, json.JSONDecodeError):
            return set()
    elif resource_type == "network":
        network_uuid = resource_id
    elif resource_type in {"storage-pool", "network-pool"}:
        try:
            pool_id = int(resource_id)
        except ValueError:
            return set()
    elif resource_type == "flavor":
        try:
            flavor_id = int(resource_id)
        except ValueError:
            return set()

    result: set[str] = set()
    for project in db.query(ProjectModel).all():
        if storage_uuid is not None and any(
            association.storage_uuid == storage_uuid
            for pool in project.storage_pools
            for association in pool.storages
        ):
            result.add(str(project.id))
        if network_uuid is not None and any(
            network.uuid == network_uuid
            for pool in project.network_pools
            for network in [*pool.networks, *(port.network for port in pool.ports)]
        ):
            result.add(str(project.id))
        if resource_type == "storage-pool" and any(
            pool.id == pool_id for pool in project.storage_pools
        ):
            result.add(str(project.id))
        if resource_type == "network-pool" and any(
            pool.id == pool_id for pool in project.network_pools
        ):
            result.add(str(project.id))
        if resource_type == "flavor" and any(
            flavor.id == flavor_id for flavor in project.flavors
        ):
            result.add(str(project.id))
    if resource_type == "node" and node_id is not None:
        result.update(
            str(project_id)
            for (project_id,) in db.query(DomainModel.owner_project_id).filter(
                DomainModel.node_name == node_id,
                DomainModel.owner_project_id.is_not(None),
            )
        )
        for storage in db.query(StorageModel).filter(StorageModel.node_name == node_id):
            result.update(_project_ids_for_resource(
                db,
                resource_type="storage",
                resource_id=storage.uuid,
                node_id=node_id,
            ))
        for network in db.query(NetworkModel).filter(NetworkModel.node_name == node_id):
            result.update(_project_ids_for_resource(
                db,
                resource_type="network",
                resource_id=network.uuid,
                node_id=node_id,
            ))
    return result


def _select_server_project(
    context: LeaseContext,
    candidates: set[str],
) -> str | None:
    if context.lease.project_ids:
        candidates &= set(context.lease.project_ids)
    return sorted(candidates)[0] if candidates else None


def resolve_action_target(
    db: Session,
    *,
    context: LeaseContext,
    definition: ActionDefinition,
    request: ActionRequest,
    model: BaseModel,
) -> ResolvedTarget:
    _assert_target_mapping(definition, request)
    public_target = _public_action(definition.action_id).get("target", {})
    mapped_resource = public_target.get("resourceIdField")
    resource_id = (
        str(request.input[mapped_resource])
        if mapped_resource and request.input.get(mapped_resource) is not None
        else definition.action_id
    )
    # projectId/nodeIdは必ずDBまたは検証済み作成inputから再構築する。
    project_id: str | None = None
    node_id: str | None = None
    generation_type: str | None = None
    generation_id: str | None = None
    related_targets: tuple[dict[str, str], ...] = ()

    if definition.action_id in {"node.get", "node.facts", "node.info"}:
        from node.models import NodeModel

        row = db.get(NodeModel, resource_id)
        if row is None:
            raise NotFoundError("node_not_found", "nodeがありません")
        node_id = row.name
    elif definition.action_id in {"vm.get", "vm.xml.get"}:
        from domain.models import DomainModel

        row = db.get(DomainModel, resource_id)
        if row is None:
            raise NotFoundError("vm_not_found", "VMがありません")
        project_id = row.owner_project_id
        node_id = row.node_name
    elif definition.action_id == "storage.get":
        from storage.models import StorageModel

        row = db.get(StorageModel, resource_id)
        if row is None:
            raise NotFoundError("storage_not_found", "storageがありません")
        node_id = row.node_name
    elif definition.action_id in {"network.get", "network.xml.get"}:
        from network.models import NetworkModel

        row = db.get(NetworkModel, resource_id)
        if row is None:
            raise NotFoundError("network_not_found", "networkがありません")
        node_id = row.node_name

    if definition.requires_generation:
        if definition.resource_type == "vm":
            from domain.models import DomainModel

            row = db.get(DomainModel, resource_id)
            if row is None:
                raise NotFoundError("vm_not_found", "VMがありません")
            project_id = row.owner_project_id
            node_id = row.node_name
            generation_type, generation_id = "vm", row.uuid
        elif definition.resource_type == "node":
            from node.models import NodeModel

            row = db.get(NodeModel, resource_id)
            if row is None:
                raise NotFoundError("node_not_found", "nodeがありません")
            node_id = row.name
            generation_type, generation_id = "node", row.name
        elif definition.resource_type == "storage":
            from storage.models import StorageModel

            row = db.get(StorageModel, resource_id)
            if row is None:
                raise NotFoundError("storage_not_found", "storageがありません")
            node_id = row.node_name
            generation_type, generation_id = "storage", row.uuid
        elif definition.resource_type == "network":
            from network.models import NetworkModel

            row = db.get(NetworkModel, resource_id)
            if row is None:
                raise NotFoundError("network_not_found", "networkがありません")
            node_id = row.node_name
            generation_type, generation_id = "network", row.uuid
        elif definition.resource_type == "image":
            from storage.models import ImageModel, StorageModel

            storage_uuid = str(getattr(model, "storage_uuid", request.input.get("uuid", "")))
            image = db.query(ImageModel).filter(
                ImageModel.storage_uuid == storage_uuid,
                or_(
                    ImageModel.path == request.input.get("path"),
                    ImageModel.name == request.input.get("name"),
                ),
            ).one_or_none()
            if image is None:
                raise NotFoundError("image_not_found", "imageがありません")
            storage = db.get(StorageModel, image.storage_uuid)
            node_id = storage.node_name if storage else None
            generation_type = "image"
            generation_id = json.dumps(
                [image.storage_uuid, image.path],
                ensure_ascii=False,
                separators=(",", ":"),
            )
            resource_id = generation_id
        elif definition.resource_type in {"network-pool", "storage-pool"}:
            generation_type = definition.resource_type
            generation_id = str(resource_id)
        elif definition.resource_type in {"project", "user", "flavor", "task"}:
            generation_type = definition.resource_type
            generation_id = str(resource_id)

    # create/readでも実resourceのnode/project制約を解決する。
    if definition.action_id == "image.download":
        from storage.models import StorageModel

        storage = db.get(StorageModel, model.storage_uuid)
        if storage is None:
            raise NotFoundError("storage_not_found", "download先storageがありません")
        node_id = storage.node_name
        project_id = _select_server_project(
            context,
            _project_ids_for_resource(
                db,
                resource_type="storage",
                resource_id=storage.uuid,
                node_id=storage.node_name,
            ),
        )
        # URLそのものではなく実際の保存先(storage + basename)を予約する。
        # query tokenを監査へ残さず、別signed URLの同一destinationも競合する。
        destination_name = urlparse(model.image_url).path.rsplit("/", 1)[-1]
        if destination_name in {"", ".", ".."}:
            raise ConflictError(
                "image_filename_required",
                "image download URLにはfile名が必要です",
            )
        destination_hash = request_hash({
            "storageUuid": storage.uuid,
            "destinationName": destination_name,
        })
        resource_id = f"sha256:{destination_hash}"
    elif definition.action_id == "vm.create":
        node_id = model.node_name
    elif definition.action_id == "node.create":
        # 未作成nodeもlifecycle reservationの安定keyへ含める。
        node_id = model.name
    elif definition.action_id == "storage.create":
        node_id = model.node_name
    elif definition.action_id == "network.create":
        node_id = model.node_name
    elif definition.action_id == "network.provider.create":
        node_id = model.network_node

    # generation不要のmutation/readも既存objectの所属をserver側で解決する。
    if definition.resource_type == "node":
        from node.models import NodeModel

        node = db.get(NodeModel, resource_id)
        if node is not None:
            node_id = node.name
    elif definition.resource_type == "vm":
        from domain.models import DomainModel

        vm = db.get(DomainModel, resource_id)
        if vm is not None:
            node_id = vm.node_name
            project_id = vm.owner_project_id
    elif definition.resource_type == "storage":
        from storage.models import StorageModel

        storage = db.get(StorageModel, resource_id)
        if storage is not None:
            node_id = storage.node_name
    elif definition.resource_type == "network":
        from network.models import NetworkModel

        network = db.get(NetworkModel, resource_id)
        if network is not None:
            node_id = network.node_name
    elif definition.resource_type == "task":
        task = db.get(TaskModel, resource_id)
        values = [] if task is None else (task.resolved_targets or [])
        if isinstance(values, dict):
            values = [values]
        nodes = {
            str(item["nodeId"])
            for item in values
            if isinstance(item, dict) and item.get("nodeId") is not None
        }
        node_id = sorted(nodes)[0] if len(nodes) == 1 else None
        related_targets = tuple(
            {
                str(key): str(value)
                for key, value in item.items()
                if value is not None
            }
            for item in values
            if isinstance(item, dict)
        )

    derived_projects = _project_ids_for_resource(
        db,
        resource_type=definition.resource_type,
        resource_id=resource_id,
        node_id=node_id,
    )
    if project_id is None:
        project_id = _select_server_project(context, derived_projects)

    # identity/system/global collectionへclientがproject/nodeを付けても権限化しない。
    if definition.resource_type in {"system", "metrics", "user"}:
        project_id = None
        node_id = None

    return ResolvedTarget(
        resource_type=definition.resource_type,
        resource_id=resource_id,
        project_id=project_id,
        node_id=node_id,
        generation_resource_type=generation_type,
        generation_resource_id=generation_id,
        related_targets=related_targets,
    )


def _validate_generation(
    db: Session,
    definition: ActionDefinition,
    request: ActionRequest,
    target: ResolvedTarget,
) -> None:
    if not definition.mutation:
        return
    if not definition.requires_generation:
        if request.expected_generation != "0":
            raise ConflictError(
                "generation_sentinel_required",
                "新規作成・refreshにはexpectedGeneration=`0`が必要です",
            )
        return
    if target.generation_resource_type is None or target.generation_resource_id is None:
        raise ConflictError("generation_target_missing", "generation対象がありません")
    current = resolve_generation(
        db,
        resource_type=target.generation_resource_type,
        resource_id=target.generation_resource_id,
    )
    if current != request.expected_generation:
        raise ConflictError(
            "stale_generation",
            "対象resourceは既に変更されています",
        )


def validate_image_download_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ConflictError(
            "image_url_denied",
            "image download URLはuserinfoを含まないhttps URLに限定されます",
        )
    allowed = {
        item.strip().lower()
        for item in os.getenv("AGENT_IMAGE_DOWNLOAD_ALLOWED_HOSTS", "").split(",")
        if item.strip()
    }
    hostname = parsed.hostname.rstrip(".").lower()
    if not allowed or hostname not in allowed:
        raise ConflictError(
            "image_host_denied",
            "image download hostはallowlistにありません",
        )
    if hostname in {"localhost", "localhost.localdomain"}:
        raise ConflictError("image_host_denied", "localhostは指定できません")
    try:
        addresses = {
            item[4][0]
            for item in socket.getaddrinfo(hostname, parsed.port or 443, type=socket.SOCK_STREAM)
        }
    except socket.gaierror as exc:
        raise ConflictError("image_host_unresolved", "image hostを名前解決できません") from exc
    for address in addresses:
        ip = ipaddress.ip_address(address)
        if not ip.is_global:
            raise ConflictError(
                "image_address_denied",
                "private/link-local/metadata宛のimage downloadは禁止されています",
            )


def _validate_action_references(
    db: Session,
    *,
    context: LeaseContext,
    definition: ActionDefinition,
    model: BaseModel,
    target: ResolvedTarget,
) -> ResolvedTarget:
    """入力が参照するstorage/network/project等もlease制約と同一nodeで検査する。"""

    from flavor.models import FlavorModel
    from node.models import NodeModel
    from project.models import ProjectModel
    from storage.models import ImageModel, StorageModel
    from network.models import NetworkModel

    related: list[dict[str, str]] = [
        dict(item) for item in target.related_targets
    ]
    allowed_storages = _allowed_storage_ids(db, context)
    allowed_networks = _allowed_network_ids(db, context)
    constrained_projects = db.query(ProjectModel).filter(
        ProjectModel.id.in_(context.lease.project_ids or ["__none__"]),
    ).all()

    def storage_project_id(storage_uuid: str) -> str | None:
        for project in constrained_projects:
            if any(
                association.storage_uuid == storage_uuid
                for pool in project.storage_pools
                for association in pool.storages
            ):
                return str(project.id)
        return None

    def network_project_id(network_uuid: str) -> str | None:
        for project in constrained_projects:
            if any(
                network.uuid == network_uuid
                for pool in project.network_pools
                for network in [
                    *pool.networks,
                    *(port.network for port in pool.ports),
                ]
            ):
                return str(project.id)
        return None

    def storage_reference(storage_uuid: str, required_node: str | None) -> StorageModel:
        storage = db.get(StorageModel, storage_uuid)
        if storage is None:
            raise NotFoundError("storage_not_found", "参照storageがありません")
        if required_node is not None and storage.node_name != required_node:
            raise ConflictError(
                "storage_node_mismatch",
                "参照storageはtargetと同じnodeにありません",
            )
        if allowed_storages is not None and storage.uuid not in allowed_storages:
            raise AuthorizationError(
                "storage_constraint_denied",
                "参照storageは能力leaseの制約外です",
            )
        item = {
            "resourceType": "storage",
            "resourceId": storage.uuid,
            "nodeId": storage.node_name,
        }
        project_id = storage_project_id(storage.uuid)
        if project_id is not None:
            item["projectId"] = project_id
        related.append(item)
        return storage

    def network_reference(network_uuid: str, required_node: str | None) -> NetworkModel:
        network = db.get(NetworkModel, network_uuid)
        if network is None:
            raise NotFoundError("network_not_found", "参照networkがありません")
        if required_node is not None and network.node_name != required_node:
            raise ConflictError(
                "network_node_mismatch",
                "参照networkはtargetと同じnodeにありません",
            )
        if allowed_networks is not None and network.uuid not in allowed_networks:
            raise AuthorizationError(
                "network_constraint_denied",
                "参照networkは能力leaseの制約外です",
            )
        item = {
            "resourceType": "network",
            "resourceId": network.uuid,
            "nodeId": network.node_name,
        }
        project_id = network_project_id(network.uuid)
        if project_id is not None:
            item["projectId"] = project_id
        related.append(item)
        return network

    action_id = definition.action_id
    if action_id in _FAMILY_EFFECTS or action_id in _FAMILY_MUTATIONS:
        # inventory refresh handlerは全nodeを走査するため、受付時点のnodeを
        # lifecycle readerとして予約する。node追加自身はprimary targetで補う。
        for row in db.query(NodeModel.name).all():
            node_name = str(row[0] if isinstance(row, tuple) else row.name)
            related.append({
                "resourceType": "node-lifecycle",
                "resourceId": node_name,
                "reservationScope": "global",
                "reservationMode": "shared",
                "authorizationTarget": "false",
            })
    if action_id == "vm.create":
        owner_project = db.get(ProjectModel, model.project_id)
        if owner_project is None:
            raise NotFoundError(
                "project_not_found",
                "VM owner projectがありません",
            )
        if (
            context.lease.project_ids
            and model.project_id not in context.lease.project_ids
        ):
            raise AuthorizationError(
                "vm_project_denied",
                "VM owner projectは能力leaseの制約外です",
            )
        target = replace(target, project_id=str(owner_project.id))
        related.append({
            "resourceType": "project",
            "resourceId": str(owner_project.id),
            "projectId": str(owner_project.id),
        })
        project_storage_ids = {
            association.storage_uuid
            for pool in owner_project.storage_pools
            for association in pool.storages
        }
        project_network_ids = {
            network.uuid
            for pool in owner_project.network_pools
            for network in [*pool.networks, *(port.network for port in pool.ports)]
        }
        for disk in model.disks:
            if disk.save_pool_uuid not in project_storage_ids or (
                disk.original_pool_uuid
                and disk.original_pool_uuid not in project_storage_ids
            ):
                raise AuthorizationError(
                    "vm_storage_project_denied",
                    "VM disk storageはowner projectのpool外です",
                )
            storage_reference(disk.save_pool_uuid, model.node_name)
            if disk.original_pool_uuid:
                storage_reference(disk.original_pool_uuid, model.node_name)
        for interface in model.interface:
            if interface.network_uuid not in project_network_ids:
                raise AuthorizationError(
                    "vm_network_project_denied",
                    "VM networkはowner projectのpool外です",
                )
            network_reference(interface.network_uuid, model.node_name)
    elif action_id == "vm.network.update":
        network_reference(model.network_uuid, target.node_id)
    elif action_id == "vm.cdrom.update" and model.path:
        images = db.query(ImageModel).filter(ImageModel.path == model.path).all()
        matching_images = [
            image
            for image in images
            if (
                (storage := db.get(StorageModel, image.storage_uuid)) is not None
                and storage.node_name == target.node_id
            )
        ]
        if len(matching_images) != 1:
            raise ConflictError(
                "cdrom_image_required",
                "CD-ROM pathは対象node上の一意な登録済みimage.pathに限定されます",
            )
        image = matching_images[0]
        storage_reference(image.storage_uuid, target.node_id)
        image_target = {
            "resourceType": "image",
            "resourceId": json.dumps(
                [image.storage_uuid, image.path],
                ensure_ascii=False,
                separators=(",", ":"),
            ),
            "nodeId": target.node_id or "",
        }
        image_project = storage_project_id(image.storage_uuid)
        if image_project is not None:
            image_target["projectId"] = image_project
        related.append(image_target)
    elif action_id == "vm.project.update":
        destination = db.get(ProjectModel, model.project_id)
        if destination is None:
            raise NotFoundError("project_not_found", "移動先projectがありません")
        if context.lease.project_ids and model.project_id not in context.lease.project_ids:
            raise AuthorizationError(
                "destination_project_denied",
                "移動先projectは能力leaseの制約外です",
            )
        related.append({
            "resourceType": "project",
            "resourceId": destination.id,
            "projectId": destination.id,
        })
    elif action_id == "network.provider.create":
        network_node = db.get(NodeModel, model.network_node)
        if network_node is None:
            raise NotFoundError(
                "network_node_not_found",
                "provider networkのnetwork nodeがありません",
            )
        overlay_nodes = [
            node
            for node in db.query(NodeModel).order_by(NodeModel.name).all()
            if any(role.role_name == "vxlan_overlay" for role in node.roles)
        ]
        for node in {item.name: item for item in [network_node, *overlay_nodes]}.values():
            related.append({
                "resourceType": "node",
                "resourceId": node.name,
                "nodeId": node.name,
            })
    elif action_id in {"storage.pool.create", "storage.pool.update"}:
        for storage_uuid in model.storage_uuids:
            storage_reference(storage_uuid, None)
    elif action_id == "network.pool.update":
        network_reference(model.network_uuid, None)
    elif action_id in {"image.delete", "image.download", "image.flavor.update"}:
        storage_uuid = (
            model.uuid if action_id == "image.delete" else model.storage_uuid
        )
        storage = storage_reference(storage_uuid, target.node_id)
        if action_id == "image.flavor.update":
            if storage.node_name != model.node_name:
                raise ConflictError(
                    "image_node_mismatch",
                    "imageのnodeNameがstorageと一致しません",
                )
            flavor = db.get(FlavorModel, model.flavor_id)
            if flavor is None:
                raise NotFoundError("flavor_not_found", "flavorがありません")
            if context.lease.project_ids:
                allowed_flavors = {
                    item.id
                    for project in db.query(ProjectModel).filter(
                        ProjectModel.id.in_(context.lease.project_ids),
                    )
                    for item in project.flavors
                }
                if flavor.id not in allowed_flavors:
                    raise AuthorizationError(
                        "flavor_constraint_denied",
                        "参照flavorは能力leaseの制約外です",
                    )
            flavor_target = {
                "resourceType": "flavor",
                "resourceId": str(flavor.id),
            }
            if target.node_id is not None:
                flavor_target["nodeId"] = target.node_id
            if context.lease.project_ids:
                flavor_project = next(
                    (
                        str(project.id)
                        for project in constrained_projects
                        if flavor in project.flavors
                    ),
                    None,
                )
                if flavor_project is not None:
                    flavor_target["projectId"] = flavor_project
            related.append(flavor_target)

    # 同じ参照が複数disk等に現れてもreservationは1つに正規化する。
    unique = {
        json.dumps(item, ensure_ascii=False, sort_keys=True): item
        for item in related
    }
    for item in unique.values():
        item["relatedTarget"] = "true"
    return replace(target, related_targets=tuple(unique.values()))


def _validate_resolved_constraints(
    context: LeaseContext,
    target: ResolvedTarget,
) -> None:
    """primaryと全参照resourceへproject/node制約をANDで適用する。"""

    values = target.task_value()
    for value in values:
        if str(value.get("authorizationTarget", "true")).lower() == "false":
            continue
        if context.lease.project_ids and value.get("projectId") not in set(
            context.lease.project_ids,
        ):
            raise AuthorizationError(
                "project_denied",
                "resolved targetのprojectが能力leaseの制約外です",
            )
        if context.lease.node_ids and value.get("nodeId") not in set(
            context.lease.node_ids,
        ):
            raise AuthorizationError(
                "node_denied",
                "resolved targetのnodeが能力leaseの制約外です",
            )


def _validate_identity_admin_scope(
    db: Session,
    context: LeaseContext,
    definition: ActionDefinition,
    model: BaseModel,
) -> None:
    """恒久admin credentialへ影響する場合だけ追加能力を要求する。"""

    if definition.action_id not in {"user.create", "user.update", "user.delete"}:
        return
    from user.models import UserScopeModel

    username = str(
        getattr(model, "path_username", None)
        or getattr(model, "username", "")
    )
    existing_admin = db.query(UserScopeModel).filter(
        UserScopeModel.user_id == username,
        UserScopeModel.name == "admin",
    ).first() is not None
    requested_scopes = {
        str(getattr(item, "name", ""))
        for item in (getattr(model, "scopes", None) or [])
    }
    grants_identity = any(
        scope == "admin" or scope.startswith("identity.")
        for scope in requested_scopes
    )
    if existing_admin or grants_identity:
        require_scope(list(context.lease.scopes or []), "identity.admin")


_FAMILY_MUTATIONS = {
    "vm.refresh",
    "image.refresh",
    "network.refresh",
}

_SSH_BACKED_TASK_MUTATIONS = {
    action_id
    for action_id, item in ACTIONS.items()
    if item.kind == "task" and action_id not in {"project.create", "project.delete"}
}

_FAMILY_EFFECTS: dict[str, tuple[str, ...]] = {
    "node.create": ("vm", "storage", "image", "network"),
    "vm.refresh": ("vm", "image"),
    "vm.create": ("vm", "storage", "image"),
    "vm.delete": ("vm", "image"),
    "vm.power.update": ("vm", "image"),
    "vm.cdrom.update": ("vm", "image"),
    "vm.network.update": ("vm", "image"),
    "storage.create": ("storage", "image"),
    "network.create": ("network",),
    "network.delete": ("network",),
    "network.ovs.create": ("network",),
    "network.ovs.delete": ("network",),
    "network.provider.create": ("network",),
    "image.refresh": ("storage", "image"),
}

_NODE_LIFECYCLE_EXCLUSIVE = {
    "node.create",
    "node.delete",
    "node.role.update",
}


def _apply_reservation_contract(
    definition: ActionDefinition,
    target: ResolvedTarget,
) -> ResolvedTarget:
    """resource/family/global reader-writer reservation metadataを付与する。"""

    reservation_scope = (
        "family" if definition.action_id in _FAMILY_MUTATIONS else "resource"
    )
    related = [dict(item) for item in target.related_targets]
    for resource_type in _FAMILY_EFFECTS.get(definition.action_id, ()):
        related.append({
            "resourceType": resource_type,
            "resourceId": "family",
            "reservationScope": "family",
            "reservationMode": "exclusive",
            "authorizationTarget": "false",
        })
    if definition.action_id in _SSH_BACKED_TASK_MUTATIONS:
        related.append({
            "resourceType": "ssh-credentials",
            "resourceId": "global",
            "reservationScope": "global",
            "reservationMode": "shared",
            "authorizationTarget": "false",
        })
    if definition.action_id == "node.ssh-key.write":
        related.append({
            "resourceType": "ssh-credentials",
            "resourceId": "global",
            "reservationScope": "global",
            "reservationMode": "exclusive",
            "authorizationTarget": "false",
        })
    node_ids = {
        str(node_id)
        for node_id in [
            target.node_id,
            *(
                item.get("nodeId") or item.get("node_id")
                for item in target.related_targets
            ),
        ]
        if node_id
    }
    lifecycle_mode = (
        "exclusive"
        if definition.action_id in _NODE_LIFECYCLE_EXCLUSIVE
        else "shared"
    )
    for node_id in node_ids:
        related.append({
            "resourceType": "node-lifecycle",
            "resourceId": node_id,
            "reservationScope": "global",
            "reservationMode": lifecycle_mode,
            "authorizationTarget": "false",
        })
    unique = {
        json.dumps(item, ensure_ascii=False, sort_keys=True): item
        for item in related
    }
    return replace(
        target,
        reservation_scope=reservation_scope,
        reservation_mode="exclusive",
        related_targets=tuple(unique.values()),
    )


def _task_body_and_params(
    definition: ActionDefinition,
    request: ActionRequest,
    model: BaseModel,
) -> tuple[BaseModel | None, dict[str, Any]]:
    body: BaseModel | None = model if definition.input_model else None
    params: dict[str, Any] = {}
    action = definition.action_id
    resource_id = request.target.resource_id
    if action == "node.delete":
        params = {"name": resource_id}
    elif action in {
        "vm.delete", "vm.power.update", "vm.cdrom.update", "vm.network.update",
        "storage.delete", "network.delete", "network.ovs.create", "network.ovs.delete",
    }:
        params = {"uuid": resource_id}
    elif action == "image.delete":
        params = {"uuid": model.uuid, "name": model.name}
        body = None
    if action == "network.ovs.delete":
        params["name"] = model.name
        body = None
    elif action == "project.delete":
        params = {"project_id": model.project_id}
        body = None
    return body, params


def _dependent_selectors(definition: ActionDefinition, model: BaseModel) -> list[tuple[str, str, str, BaseModel | None]]:
    action = definition.action_id
    result: list[tuple[str, str, str, BaseModel | None]] = []
    if action == "node.create":
        if model.libvirt_role:
            from node.schemas import NodeRoleForUpdate

            result.append((
                "patch", "node", "role",
                NodeRoleForUpdate(node_name=model.name, role_name="libvirt"),
            ))
        result.extend([
            ("put", "vm", "list", None),
            ("put", "storage", "list", None),
            ("put", "network", "list", None),
        ])
    elif action == "vm.create":
        result.extend([
            ("put", "vm", "list", None),
            ("put", "storage", "list", None),
        ])
    elif action in {
        "vm.delete", "vm.power.update", "vm.cdrom.update", "vm.network.update",
    }:
        result.append(("put", "vm", "list", None))
    elif action == "storage.create":
        result.append(("put", "storage", "list", None))
    elif action in {
        "network.create", "network.delete", "network.ovs.create", "network.ovs.delete",
    }:
        result.append(("put", "network", "list", None))
    return result


def _execute_task_action(
    db: Session,
    *,
    context: LeaseContext,
    definition: ActionDefinition,
    request: ActionRequest,
    model: BaseModel,
    target: ResolvedTarget,
    correlation_id: str,
    agent_request_hash: str,
) -> OperationAccepted:
    if definition.task_selector is None:
        raise ServiceUnavailableError(
            "task_selector_missing",
            "task selectorが登録されていません",
        )
    method, resource, object_name = definition.task_selector
    body, params = _task_body_and_params(definition, request, model)
    principal = SimpleNamespace(id=context.principal_id)
    append_audit_event(
        db,
        event_type="action.authorized",
        actor_id=context.principal_id,
        device_id=context.device.id,
        lease_id=context.lease.id,
        action_id=definition.action_id,
        resource_type=target.resource_type,
        resource_id=target.resource_id,
        project_id=target.project_id,
        node_id=target.node_id,
        request_hash=request_hash(request.model_dump(mode="json", by_alias=True)),
        policy_decision="allowed",
        correlation_id=correlation_id,
    )
    manager = TaskManager(db)
    manager.select(method, resource, object_name)
    try:
        root = manager.commit(
            user=principal,
            body=body,
            param=params,
            idempotency_key=request.idempotency_key,
            agent_request_hash=agent_request_hash,
            principal_id=context.principal_id,
            correlation_id=correlation_id,
            lease_id=context.lease.id,
            risk=definition.risk,
            resolved_targets=target.task_value(),
            expected_generation=request.expected_generation,
            commit_transaction=False,
        )
    except TaskIdempotencyConflict as exc:
        raise ConflictError("idempotency_key_conflict", str(exc)) from exc
    if not manager.created:
        db.commit()
        operation = get_operation(db, root.uuid)
        return OperationAccepted(
            operation_id=operation["operation_id"],
            task_ids=operation["task_ids"],
            status=operation["normalized_status"],
            risk=definition.risk,
            lease_id=root.lease_id or context.lease.id,
            correlation_id=root.correlation_id or root.uuid,
        )

    consume_mutation(context)
    try:
        acquire_target_reservations(
            db,
            resolved_targets=target.task_value(),
            correlation_id=root.correlation_id or root.uuid,
            lease_id=context.lease.id,
        )
        previous = root
        for dep_method, dep_resource, dep_object, dep_body in _dependent_selectors(
            definition,
            model,
        ):
            dependent = TaskManager(db)
            dependent.select(dep_method, dep_resource, dep_object)
            previous = dependent.commit(
                user=principal,
                body=dep_body,
                # 兄弟並列にせず、unknown/error/cancelledで後続を止める。
                dep_uuid=previous.uuid,
                principal_id=context.principal_id,
                correlation_id=root.correlation_id,
                lease_id=context.lease.id,
                risk=definition.risk,
                commit_transaction=False,
            )
    except TaskTargetBusy as exc:
        raise ConflictError("target_busy", "targetは別operationが変更中です") from exc
    operation = get_operation(db, root.uuid)
    append_audit_event(
        db,
        event_type="operation.accepted",
        actor_id=context.principal_id,
        device_id=context.device.id,
        lease_id=context.lease.id,
        action_id=definition.action_id,
        policy_decision="allowed",
        operation_id=root.uuid,
        correlation_id=root.correlation_id,
        outcome="queued",
    )
    db.commit()
    return OperationAccepted(
        operation_id=root.uuid,
        task_ids=operation["task_ids"],
        status="queued",
        risk=definition.risk,
        lease_id=context.lease.id,
        correlation_id=root.correlation_id or root.uuid,
    )


def _execute_direct_action(
    db: Session,
    *,
    context: LeaseContext,
    definition: ActionDefinition,
    request: ActionRequest,
    model: BaseModel,
    target: ResolvedTarget,
    correlation_id: str,
    agent_request_hash: str,
) -> OperationAccepted:
    if definition.adapter not in DIRECT_ADAPTERS:
        raise ServiceUnavailableError(
            "action_adapter_missing",
            "direct action adapterが登録されていません",
        )
    principal = SimpleNamespace(id=context.principal_id)
    manager = TaskManager(db)
    # direct mutationもAPI process内で実行せず、既存worker queueへ載せる。
    # objectにcatalog action IDを保持することで、generic handlerでも
    # durable resumeと監査のaction逆引きを安定させる。
    manager.select("agent", "direct", definition.action_id)
    append_audit_event(
        db,
        event_type="action.authorized",
        actor_id=context.principal_id,
        device_id=context.device.id,
        lease_id=context.lease.id,
        action_id=definition.action_id,
        resource_type=target.resource_type,
        resource_id=target.resource_id,
        project_id=target.project_id,
        node_id=target.node_id,
        request_hash=agent_request_hash,
        policy_decision="allowed",
        correlation_id=correlation_id,
    )
    try:
        task = manager.commit(
            user=principal,
            body=request.input,
            param={"resourceId": target.resource_id},
            idempotency_key=request.idempotency_key,
            agent_request_hash=agent_request_hash,
            principal_id=context.principal_id,
            correlation_id=correlation_id,
            lease_id=context.lease.id,
            risk=definition.risk,
            resolved_targets=target.task_value(),
            expected_generation=request.expected_generation,
            commit_transaction=False,
        )
    except TaskIdempotencyConflict as exc:
        raise ConflictError("idempotency_key_conflict", str(exc)) from exc
    if not manager.created:
        db.commit()
        operation = get_operation(db, task.uuid)
        return OperationAccepted(
            operation_id=operation["operation_id"],
            task_ids=operation["task_ids"],
            status=operation["normalized_status"],
            risk=definition.risk,
            lease_id=task.lease_id or context.lease.id,
            correlation_id=task.correlation_id or task.uuid,
        )

    consume_mutation(context)
    try:
        acquire_target_reservations(
            db,
            resolved_targets=target.task_value(),
            correlation_id=task.correlation_id or task.uuid,
            lease_id=context.lease.id,
        )
    except TaskTargetBusy as exc:
        raise ConflictError("target_busy", "targetは別operationが変更中です") from exc
    append_audit_event(
        db,
        event_type="operation.accepted",
        actor_id=context.principal_id,
        device_id=context.device.id,
        lease_id=context.lease.id,
        action_id=definition.action_id,
        policy_decision="allowed",
        operation_id=task.uuid,
        correlation_id=task.correlation_id,
        outcome="queued",
    )
    db.commit()
    return OperationAccepted(
        operation_id=task.uuid,
        task_ids=[task.uuid],
        status="queued",
        risk=definition.risk,
        lease_id=context.lease.id,
        correlation_id=task.correlation_id or task.uuid,
    )


def execute_action(
    db: Session,
    *,
    context: LeaseContext,
    action_id: str,
    request: ActionRequest,
) -> ActionResult | OperationAccepted:
    definition = get_action(action_id)
    _validate_public_json(action_id, request.input)
    model = _load_input_model(definition, request.input)
    agent_request_hash = request_hash({
        "action": action_id,
        "input": request.input,
        "target": request.target.model_dump(mode="json", by_alias=True),
        "expectedGeneration": request.expected_generation,
    })
    if definition.mutation and request.idempotency_key is not None:
        existing = db.query(TaskModel).filter(
            TaskModel.principal_id == context.principal_id,
            TaskModel.idempotency_key == request.idempotency_key,
        ).one_or_none()
        if existing is not None:
            if existing.agent_request_hash != agent_request_hash:
                raise ConflictError(
                    "idempotency_key_conflict",
                    "同じidempotencyKeyが異なるrequestに使用されています",
                )
            authorize_operation_access(
                db,
                context=context,
                definition=definition,
                task=existing,
            )
            operation = get_operation(db, existing.uuid)
            db.commit()
            return OperationAccepted(
                operation_id=existing.uuid,
                task_ids=operation["task_ids"],
                status=operation["normalized_status"],
                risk=definition.risk,
                lease_id=existing.lease_id or context.lease.id,
                correlation_id=existing.correlation_id or existing.uuid,
            )
    target = resolve_action_target(
        db,
        context=context,
        definition=definition,
        request=request,
        model=model,
    )
    target = _validate_action_references(
        db,
        context=context,
        definition=definition,
        model=model,
        target=target,
    )
    if definition.mutation:
        target = _apply_reservation_contract(definition, target)
    if definition.mutation:
        if request.idempotency_key is None:
            raise ConflictError(
                "idempotency_key_required",
                "変更操作にはidempotencyKeyが必要です",
            )
        if request.expected_generation is None:
            raise ConflictError(
                "expected_generation_required",
                "変更操作にはexpectedGenerationが必要です",
            )
    _validate_generation(db, definition, request, target)
    if action_id == "image.download":
        validate_image_download_url(model.image_url)
    collection_read = not definition.mutation and (
        action_id.endswith(".list")
        or action_id in {"task.incomplete", "metrics.get", "system.version", "user.me"}
    )
    if not collection_read:
        _validate_resolved_constraints(context, target)
    _validate_identity_admin_scope(db, context, definition, model)
    authorize_action(
        db,
        context=context,
        definition=definition,
        resource_type=target.resource_type,
        project_id=None if collection_read else target.project_id,
        node_id=None if collection_read else target.node_id,
        expected_generation=request.expected_generation,
        collection=collection_read,
    )
    correlation_id = str(uuid.uuid4())
    if definition.kind == "read":
        adapter = READ_ADAPTERS.get(definition.adapter)
        if adapter is None:
            raise ServiceUnavailableError(
                "action_adapter_missing",
                "read action adapterが登録されていません",
            )
        result = adapter(db, context, model, target)
        append_audit_event(
            db,
            event_type="action.read",
            actor_id=context.principal_id,
            device_id=context.device.id,
            lease_id=context.lease.id,
            action_id=definition.action_id,
            resource_type=target.resource_type,
            resource_id=target.resource_id,
            project_id=target.project_id,
            node_id=target.node_id,
            request_hash=request_hash(request.model_dump(mode="json", by_alias=True)),
            policy_decision="allowed",
            correlation_id=correlation_id,
            outcome="succeeded",
        )
        db.commit()
        return ActionResult(
            action=definition.action_id,
            result=result,
            correlation_id=correlation_id,
        )
    if definition.kind == "task":
        return _execute_task_action(
            db,
            context=context,
            definition=definition,
            request=request,
            model=model,
            target=target,
            correlation_id=correlation_id,
            agent_request_hash=agent_request_hash,
        )
    return _execute_direct_action(
        db,
        context=context,
        definition=definition,
        request=request,
        model=model,
        target=target,
        correlation_id=correlation_id,
        agent_request_hash=agent_request_hash,
    )


def catalog_contract_errors() -> list[str]:
    errors: list[str] = []
    for definition in ACTIONS.values():
        if definition.kind == "read" and definition.adapter not in READ_ADAPTERS:
            errors.append(f"read adapter missing: {definition.action_id}")
        if definition.kind == "direct" and definition.adapter not in DIRECT_ADAPTERS:
            errors.append(f"direct adapter missing: {definition.action_id}")
        if definition.kind == "task" and definition.task_selector is None:
            errors.append(f"task selector missing: {definition.action_id}")
    return errors
