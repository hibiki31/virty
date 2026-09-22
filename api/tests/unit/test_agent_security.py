"""Agent API境界・能力lease・queue契約の副作用なし回帰test。"""

import json
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from typing import Any, TypeVar, cast

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

import models as _all_models  # noqa: F401
from auth.router import CurrentUser
from agent.actions import (
    _apply_reservation_contract,
    _preflight_task_action,
    _validate_action_references,
    _validate_identity_admin_scope,
    _validate_public_json,
    public_input_schema,
    resolve_action_target,
)
from agent.adapters import ResolvedTarget, _agent_project
from agent import actions, adapters, tasks as agent_tasks
from agent.audit import redact_secrets
from agent.catalog import ACTIONS, PUBLIC_CATALOG
from agent.crypto import (
    _consume_dpop_replay,
    base64url_encode,
    create_capability_token,
    jwk_thumbprint,
    sha256_hex,
    verify_dpop_proof,
)
from agent.exceptions import (
    AgentError,
    AuditWriteError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    NotFoundError,
)
from agent.input_models import EmptyInput
from agent.models import (
    AgentDeviceModel,
    AgentCapabilityLeaseModel,
    AgentControlModel,
    AgentDpopReplayModel,
    AgentWebAuthnChallengeModel,
    AgentWebAuthnCredentialModel,
    AuditEventModel,
    new_agent_model,
)
from agent.policy import (
    LeaseContext,
    _check_concurrency,
    _task_action_id,
    _validate_dispatch_action_contract,
    _validate_related_target_binding,
    _validate_task_constraints,
    authenticate_lease,
    authorize_operation_access,
    resolve_generation,
    validate_worker_dispatch,
)
from agent.project_boundary import (
    PROJECT_MEMBERSHIP_MUTATIONS,
    validate_mutation_lease_constraints,
    validate_project_mutation_targets,
)
from agent.schemas import (
    ActionRequest,
    ActionTarget,
    LeaseRequest,
    PairingApproveRequest,
    PairingCreateRequest,
)
from agent.router import AgentAPIRoute, app as agent_router, list_operation_reconciliations
from agent.service import AgentIdentityService, AgentManagementService
from agent.tasks import worker_task
from agent.webauthn import (
    AuthenticationVerification,
    PythonWebAuthnBackend,
    WebAuthnBackend,
    WebAuthnService,
)
from task.functions import calculate_target_reservation_specs
from task.models import TaskModel, TaskTargetReservationModel
from task.schemas import TaskRequest
from user.models import UserModel, UserScopeModel
from flavor.models import FlavorModel
from mixin.database import Base
from domain.models import DomainModel
from network.models import (
    NetworkModel,
    NetworkPoolModel,
    NetworkPortgroupModel,
)
from node.models import NodeModel
from project.models import ProjectModel
from storage.models import (
    AssociationStoragePoolModel,
    ImageModel,
    StorageModel,
    StoragePoolModel,
)

_T = TypeVar("_T")


def _typed(model_type: type[_T], value: object) -> _T:
    """Protocol相当のtest doubleを期待する静的型へ局所的に適合させる。"""

    return cast(_T, value)


def _session(value: object) -> Session:
    return _typed(Session, value)


def _lease(value: object) -> AgentCapabilityLeaseModel:
    return _typed(AgentCapabilityLeaseModel, value)


def _device(value: object) -> AgentDeviceModel:
    return _typed(AgentDeviceModel, value)


def _control(value: object) -> AgentControlModel:
    return _typed(AgentControlModel, value)


def _task(value: object) -> TaskModel:
    return _typed(TaskModel, value)


def _context(
    *,
    scopes: list[str],
    projects: list[str] | None = None,
    nodes: list[str] | None = None,
    destructive: bool = True,
) -> LeaseContext:
    lease = _lease(SimpleNamespace(
        id="lease-1",
        principal_id="admin",
        scopes=scopes,
        project_ids=projects or [],
        node_ids=nodes or [],
        allow_destructive=destructive,
    ))
    device = _device(SimpleNamespace(id="device-1"))
    return LeaseContext(lease=lease, device=device, claims={}, token="")


def test_catalog_is_explicit_and_strict() -> None:
    assert len(ACTIONS) == 69
    assert "network.provider.create" not in ACTIONS

    def assert_strict(schema: object) -> None:
        if isinstance(schema, dict):
            if schema.get("type") == "object":
                assert schema.get("additionalProperties") is False
            for value in schema.values():
                assert_strict(value)
        elif isinstance(schema, list):
            for value in schema:
                assert_strict(value)

    for action_id in ACTIONS:
        assert_strict(public_input_schema(action_id))
    assert {item["action"] for item in PUBLIC_CATALOG["actions"]} == set(ACTIONS)
    assert {
        definition.adapter
        for definition in ACTIONS.values()
        if definition.kind == "direct"
    } <= set(adapters.DIRECT_ADAPTERS)
    assert {
        definition.adapter
        for definition in ACTIONS.values()
        if definition.kind == "read"
    } <= set(adapters.READ_ADAPTERS)
    assert ACTIONS["user.create"].risk == "R3"
    assert ACTIONS["user.create"].destructive is True
    assert ACTIONS["user.update"].risk == "R3"
    assert ACTIONS["project.resource-grants.update"].risk == "R3"
    assert ACTIONS["project.resource-grants.update"].destructive is False
    assert ACTIONS["project.resource-grant-candidates.get"].risk == "R0"
    assert ACTIONS["project.resource-grant-candidates.get"].mutation is False
    assert ACTIONS["node.create"].network_change is True
    assert ACTIONS["vm.create"].network_change is True


def test_agent_resource_list_catalog_exposes_optional_project_filter() -> None:
    project_filtered_actions = {
        "node.list",
        "vm.list",
        "storage.list",
        "storage.pool.list",
        "image.list",
        "network.list",
        "network.pool.list",
        "flavor.list",
    }
    for action_id in project_filtered_actions:
        schema = public_input_schema(action_id)
        assert "projectId" in schema["properties"], action_id
        _validate_public_json(action_id, {"projectId": "aaaaaa"})
    assert "projectId" not in public_input_schema("project.list")["properties"]

    assert ACTIONS["storage.pool.list"].input_model == (
        "agent.input_models.AgentProjectFilterInput"
    )
    assert ACTIONS["network.pool.list"].input_model == (
        "agent.input_models.AgentProjectFilterInput"
    )


def test_agent_network_serializer_hides_ungranted_portgroups(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    network = SimpleNamespace(
        uuid="network-a",
        name="network-a",
        description=None,
        node_name="node-a",
        bridge="virbr-a",
        type="openvswitch",
        active=True,
        auto_start=True,
        dhcp=False,
        ip=None,
        mac=None,
        portgroups=[
            SimpleNamespace(name="tenant-a", vlan_id="101", is_default=False),
            SimpleNamespace(name="tenant-b", vlan_id="202", is_default=False),
        ],
    )
    monkeypatch.setattr(adapters, "_model_session", lambda _: None)
    monkeypatch.setattr(adapters, "resolve_generation", lambda *_, **__: "gen")

    serialized = adapters._network_dict(cast(Any, network), {"tenant-a"})

    assert serialized["portgroups"] == [{
        "name": "tenant-a",
        "vlanId": "101",
        "isDefault": False,
    }]


def test_agent_network_xml_is_hidden_for_port_only_grant(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db = SimpleNamespace(get=lambda *_: object())
    monkeypatch.setattr(
        adapters,
        "_allowed_network_ids",
        lambda *_: {"network-a"},
    )
    monkeypatch.setattr(
        adapters,
        "_allowed_network_port_names",
        lambda *_: {"tenant-a"},
    )

    with pytest.raises(NotFoundError) as raised:
        adapters.network_xml(
            cast(Session, db),
            _context(scopes=["network.xml.get"], projects=["project-a"]),
            None,
            SimpleNamespace(
                resource_id="network-a",
                project_id="project-a",
            ),
        )

    assert raised.value.code == "network_xml_not_found"


def test_agent_reads_use_current_effective_project_membership(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """global adminでも通常readは現在のProject所属境界を越えない。"""

    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    monkeypatch.setattr(adapters, "resolve_generation", lambda *_, **__: "gen")

    def node(name: str) -> NodeModel:
        return NodeModel(
            name=name,
            description=name,
            domain=f"{name}.example.invalid",
            user_name="virty",
            port=22,
            core=8,
            memory=16384,
            cpu_gen="x86_64",
            os_like="linux",
            os_name="Linux",
            os_version="1",
            status=1,
            ansible_facts={"node": name},
        )

    def storage(name: str, node_name: str) -> StorageModel:
        return StorageModel(
            uuid=name,
            name=name,
            node_name=node_name,
            capacity=1024,
            available=512,
            path=f"/{name}",
            active=True,
            auto_start=True,
            status=1,
            update_token=f"token-{name}",
        )

    def network(name: str, node_name: str) -> NetworkModel:
        model = NetworkModel(
            uuid=name,
            name=name,
            node_name=node_name,
            bridge=f"br-{name}",
            type="openvswitch",
            active=True,
            auto_start=True,
            update_token=f"token-{name}",
        )
        model.description = name
        model.dhcp = False
        return model

    def flavor(name: str) -> FlavorModel:
        return FlavorModel(
            name=name,
            os="linux",
            manual_url=f"https://docs.example.invalid/{name}",
            icon="linux",
            cloud_init_ready=False,
            cloud_init_user="cloud-user",
            description=name,
        )

    def vm(
        name: str,
        node_name: str,
        *,
        owner_user_id: str | None = None,
        owner_project_id: str | None = None,
    ) -> DomainModel:
        model = DomainModel(
            uuid=name,
            name=name,
            core=1,
            memory=1024,
            status=1,
            update_token=f"token-{name}",
            storage_used=0,
            node_name=node_name,
        )
        model.description = name
        model.owner_user_id = owner_user_id
        model.owner_project_id = owner_project_id
        return model

    with Session(engine) as db:
        admin = UserModel(username="admin", hashed_password="unused")
        other = UserModel(username="other", hashed_password="unused")
        node_a = node("node-a")
        node_b = node("node-b")
        node_personal = node("node-personal")
        storage_a = storage("storage-a", node_a.name)
        storage_b = storage("storage-b", node_b.name)
        storage_pool_a = StoragePoolModel(
            name="storage-pool-a",
            storages=[AssociationStoragePoolModel(storage=storage_a)],
        )
        storage_pool_b = StoragePoolModel(
            name="storage-pool-b",
            storages=[AssociationStoragePoolModel(storage=storage_b)],
        )
        network_a = network("network-a", node_a.name)
        network_b = network("network-b", node_b.name)
        port_a = NetworkPortgroupModel(
            network=network_a,
            name="tenant-a",
            is_default=False,
            update_token="token-port-a",
        )
        port_a.vlan_id = "101"
        hidden_port = NetworkPortgroupModel(
            network=network_a,
            name="tenant-hidden",
            is_default=False,
            update_token="token-port-hidden",
        )
        hidden_port.vlan_id = "999"
        network_pool_a = NetworkPoolModel(
            name="network-pool-a",
            ports=[port_a],
        )
        network_pool_b = NetworkPoolModel(
            name="network-pool-b",
            networks=[network_b],
        )
        flavor_a = flavor("flavor-a")
        flavor_b = flavor("flavor-b")
        project_a = ProjectModel(
            id="aaaaaa",
            name="Project A",
            users=[admin],
            storage_pools=[storage_pool_a],
            network_pools=[network_pool_a],
            flavors=[flavor_a],
        )
        project_b = ProjectModel(
            id="bbbbbb",
            name="Project B",
            users=[other],
            storage_pools=[storage_pool_b],
            network_pools=[network_pool_b],
            flavors=[flavor_b],
        )
        images = [
            ImageModel(
                name="generic-a.qcow2",
                storage=storage_a,
                capacity=1,
                allocation=1,
                path="/storage-a/generic-a.qcow2",
                update_token="image-generic-a",
            ),
            ImageModel(
                name="flavor-a.qcow2",
                storage=storage_a,
                flavor=flavor_a,
                capacity=1,
                allocation=1,
                path="/storage-a/flavor-a.qcow2",
                update_token="image-flavor-a",
            ),
            ImageModel(
                name="cross-project.qcow2",
                storage=storage_a,
                flavor=flavor_b,
                capacity=1,
                allocation=1,
                path="/storage-a/cross-project.qcow2",
                update_token="image-cross",
            ),
            ImageModel(
                name="generic-b.qcow2",
                storage=storage_b,
                capacity=1,
                allocation=1,
                path="/storage-b/generic-b.qcow2",
                update_token="image-generic-b",
            ),
        ]
        db.add_all([
            admin,
            other,
            UserScopeModel(user_id=admin.username, name="admin"),
            node_a,
            node_b,
            node_personal,
            project_a,
            project_b,
            hidden_port,
            *images,
            vm("vm-project-a", node_a.name, owner_project_id=project_a.id),
            vm("vm-project-b", node_b.name, owner_project_id=project_b.id),
            vm(
                "vm-personal-admin",
                node_personal.name,
                owner_user_id=admin.username,
            ),
            vm("vm-personal-other", node_b.name, owner_user_id=other.username),
        ])
        db.commit()
        db.expire_all()

        context = _context(scopes=[
            "project.list",
            "project.get",
            "vm.list",
            "vm.get",
            "node.list",
            "node.get",
            "node.facts",
            "storage.list",
            "storage.get",
            "storage.pool.list",
            "image.list",
            "network.list",
            "network.get",
            "network.xml.get",
            "network.pool.list",
            "flavor.list",
        ])
        query = SimpleNamespace(limit=25, page=0)

        assert {
            item["id"] for item in adapters.project_list(db, context, query, None)["data"]
        } == {project_a.id}
        assert {
            item["uuid"] for item in adapters.vm_list(db, context, query, None)["data"]
        } == {"vm-project-a", "vm-personal-admin"}
        assert {
            item["name"] for item in adapters.node_list(db, context, query, None)["data"]
        } == {node_a.name, node_personal.name}
        assert {
            item["uuid"] for item in adapters.storage_list(db, context, query, None)["data"]
        } == {storage_a.uuid}
        assert {
            item["id"] for item in adapters.storage_pool_list(db, context, None, None)["data"]
        } == {storage_pool_a.id}
        assert {
            item["name"] for item in adapters.image_list(db, context, query, None)["data"]
        } == {"generic-a.qcow2", "flavor-a.qcow2"}
        network_result = adapters.network_list(db, context, query, None)
        assert [item["uuid"] for item in network_result["data"]] == [network_a.uuid]
        assert network_result["data"][0]["portgroups"] == [{
            "name": port_a.name,
            "vlanId": port_a.vlan_id,
            "isDefault": False,
        }]
        assert {
            item["id"] for item in adapters.network_pool_list(db, context, None, None)["data"]
        } == {network_pool_a.id}
        assert {
            item["id"] for item in adapters.flavor_list(db, context, query, None)["data"]
        } == {flavor_a.id}
        assert adapters.node_facts(
            db,
            context,
            None,
            SimpleNamespace(resource_id=node_a.name),
        ) == {"node": node_a.name}
        assert actions._select_server_project(
            db,
            context,
            {project_a.id, project_b.id},
        ) == project_a.id

        project_query = SimpleNamespace(
            limit=25,
            page=0,
            project_id=project_a.id,
        )
        assert {
            item["uuid"]
            for item in adapters.vm_list(db, context, project_query, None)["data"]
        } == {"vm-project-a"}
        assert {
            item["name"]
            for item in adapters.node_list(db, context, project_query, None)["data"]
        } == {node_a.name}
        assert {
            item["uuid"]
            for item in adapters.storage_list(db, context, project_query, None)["data"]
        } == {storage_a.uuid}
        assert adapters.storage_pool_list(
            db,
            context,
            project_query,
            None,
        )["count"] == 1
        assert {
            item["name"]
            for item in adapters.image_list(db, context, project_query, None)["data"]
        } == {"generic-a.qcow2", "flavor-a.qcow2"}
        assert {
            item["uuid"]
            for item in adapters.network_list(db, context, project_query, None)["data"]
        } == {network_a.uuid}
        assert adapters.network_pool_list(
            db,
            context,
            project_query,
            None,
        )["count"] == 1
        assert {
            item["id"]
            for item in adapters.flavor_list(db, context, project_query, None)["data"]
        } == {flavor_a.id}

        with pytest.raises(NotFoundError, match="project"):
            adapters.vm_list(
                db,
                context,
                SimpleNamespace(limit=25, page=0, project_id=project_b.id),
                None,
            )

        cdrom_target = ResolvedTarget(
            "vm",
            "vm-project-a",
            project_a.id,
            node_a.name,
        )
        with pytest.raises(AuthorizationError, match="CD-ROM image"):
            _validate_action_references(
                db,
                context=context,
                definition=ACTIONS["vm.cdrom.update"],
                model=SimpleNamespace(path="/storage-a/cross-project.qcow2"),
                target=cdrom_target,
            )
        cdrom_allowed = _validate_action_references(
            db,
            context=context,
            definition=ACTIONS["vm.cdrom.update"],
            model=SimpleNamespace(path="/storage-a/generic-a.qcow2"),
            target=cdrom_target,
        )
        assert any(
            item.get("resourceType") == "image"
            and item.get("projectId") == project_a.id
            for item in cdrom_allowed.related_targets
        )

        unauthorized_targets = [
            (adapters.project_get, project_b.id, project_b.id),
            (adapters.vm_get, "vm-project-b", project_b.id),
            (adapters.node_get, node_b.name, project_a.id),
            (adapters.storage_get, storage_b.uuid, project_a.id),
            (adapters.network_get, network_b.uuid, project_a.id),
            (adapters.network_xml, network_b.uuid, project_a.id),
        ]
        for adapter, resource_id, target_project_id in unauthorized_targets:
            with pytest.raises(NotFoundError):
                adapter(
                    db,
                    context,
                    None,
                    SimpleNamespace(
                        resource_id=resource_id,
                        project_id=target_project_id,
                    ),
                )

        constrained = _context(scopes=["vm.list"], projects=[project_a.id])
        assert {
            item["uuid"]
            for item in adapters.vm_list(db, constrained, query, None)["data"]
        } == {"vm-project-a"}
        revoked = _context(scopes=["project.list", "vm.list"], projects=[project_b.id])
        assert adapters.project_list(db, revoked, query, None)["count"] == 0
        assert adapters.vm_list(db, revoked, query, None)["count"] == 0


def test_unscoped_agent_mutations_use_current_membership_and_personal_owner() -> None:
    """空projectIdsは全Project許可ではなく、DB上の現在所属を使う。"""

    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        admin = UserModel(username="admin", hashed_password="unused")
        other = UserModel(username="other", hashed_password="unused")
        node = NodeModel(name="node-1")
        storage_a = StorageModel(
            uuid="storage-a",
            name="storage-a",
            node_name=node.name,
            capacity=1024,
            available=512,
            path="/storage-a",
            active=True,
            auto_start=True,
            status=1,
            update_token="storage-a-token",
        )
        storage_b = StorageModel(
            uuid="storage-b",
            name="storage-b",
            node_name=node.name,
            capacity=1024,
            available=512,
            path="/storage-b",
            active=True,
            auto_start=True,
            status=1,
            update_token="storage-b-token",
        )
        project_a = ProjectModel(
            id="aaaaaa",
            name="Project A",
            users=[admin],
            storage_pools=[StoragePoolModel(
                name="pool-a",
                storages=[AssociationStoragePoolModel(storage=storage_a)],
            )],
        )
        project_b = ProjectModel(
            id="bbbbbb",
            name="Project B",
            users=[other],
            storage_pools=[StoragePoolModel(
                name="pool-b",
                storages=[AssociationStoragePoolModel(storage=storage_b)],
            )],
        )

        def vm(
            uuid: str,
            *,
            owner_user_id: str | None = None,
            owner_project_id: str | None = None,
        ) -> DomainModel:
            model = DomainModel(
                uuid=uuid,
                name=uuid,
                core=1,
                memory=1024,
                status=1,
                update_token=f"{uuid}-token",
                storage_used=0,
                node_name=node.name,
            )
            model.owner_user_id = owner_user_id
            model.owner_project_id = owner_project_id
            return model

        db.add_all([
            node,
            project_a,
            project_b,
            vm("vm-project-a", owner_project_id=project_a.id),
            vm("vm-project-b", owner_project_id=project_b.id),
            vm("vm-personal-admin", owner_user_id=admin.username),
            vm("vm-personal-other", owner_user_id=other.username),
        ])
        db.commit()
        db.expire_all()

        def primary(
            resource_type: str,
            resource_id: str,
            project_id: str | None = None,
        ) -> list[dict[str, str]]:
            target = {
                "resourceType": resource_type,
                "resourceId": resource_id,
            }
            if project_id is not None:
                target["projectId"] = project_id
            return [target]

        existing_vm_actions = {
            "vm.delete",
            "vm.power.update",
            "vm.cdrom.update",
            "vm.network.update",
            "vm.project.update",
        }
        for action_id in existing_vm_actions:
            with pytest.raises(AuthorizationError, match="所属範囲外"):
                validate_project_mutation_targets(
                    db,
                    principal_id=admin.username,
                    action_id=action_id,
                    targets=primary("vm", "vm-project-b", project_b.id),
                )
            with pytest.raises(AuthorizationError, match="個人owner"):
                validate_project_mutation_targets(
                    db,
                    principal_id=admin.username,
                    action_id=action_id,
                    targets=primary("vm", "vm-personal-other"),
                )

        validate_project_mutation_targets(
            db,
            principal_id=admin.username,
            action_id="vm.delete",
            targets=primary("vm", "vm-project-a", project_a.id),
        )
        validate_project_mutation_targets(
            db,
            principal_id=admin.username,
            action_id="vm.delete",
            targets=primary("vm", "vm-personal-admin"),
        )

        with pytest.raises(AuthorizationError, match="所属範囲外"):
            validate_project_mutation_targets(
                db,
                principal_id=admin.username,
                action_id="project.update",
                targets=primary("project", project_b.id, project_b.id),
            )
        validate_project_mutation_targets(
            db,
            principal_id=admin.username,
            action_id="project.update",
            targets=primary("project", project_a.id, project_a.id),
        )

        with pytest.raises(AuthorizationError, match="所属範囲外"):
            validate_project_mutation_targets(
                db,
                principal_id=admin.username,
                action_id="storage.metadata.update",
                targets=primary("storage", storage_b.uuid, project_b.id),
            )
        with pytest.raises(AuthorizationError, match="grant範囲外"):
            validate_project_mutation_targets(
                db,
                principal_id=admin.username,
                action_id="storage.metadata.update",
                targets=primary("storage", storage_b.uuid, project_a.id),
            )
        validate_project_mutation_targets(
            db,
            principal_id=admin.username,
            action_id="storage.metadata.update",
            targets=primary("storage", storage_a.uuid, project_a.id),
        )

        with pytest.raises(AuthorizationError, match="grant範囲外"):
            validate_project_mutation_targets(
                db,
                principal_id=admin.username,
                action_id="image.download",
                targets=[
                    *primary("image", "sha256:destination", project_a.id),
                    *primary("storage", storage_b.uuid, project_a.id),
                ],
            )
        validate_project_mutation_targets(
            db,
            principal_id=admin.username,
            action_id="image.download",
            targets=[
                *primary("image", "sha256:destination", project_a.id),
                *primary("storage", storage_a.uuid, project_a.id),
            ],
        )

        # storage lifecycleはglobal admin操作なのでProject grantに依存しない。
        validate_project_mutation_targets(
            db,
            principal_id=admin.username,
            action_id="storage.delete",
            targets=primary("storage", storage_b.uuid),
        )

        replay_task = _task(SimpleNamespace(
            uuid="operation-1",
            dependence_uuid=None,
            correlation_id=None,
            method="agent",
            resource="direct",
            object="storage.metadata.update",
            principal_id=admin.username,
            user_id=admin.username,
            resolved_targets=primary("storage", storage_b.uuid, project_b.id),
        ))
        context = _context(scopes=["storage.metadata.update"])
        with pytest.raises(AuthorizationError, match="所属範囲外"):
            authorize_operation_access(
                db,
                context=context,
                definition=ACTIONS["storage.metadata.update"],
                task=replay_task,
            )
        with pytest.raises(AuthorizationError, match="所属範囲外"):
            _validate_task_constraints(db, replay_task, context.lease)


def test_agent_vm_handlers_recheck_owner_binding_after_domain_lock(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """dispatch後のVM移動・除籍・個人owner変更をbackend呼出前に拒否する。"""

    from domain import tasks as domain_tasks

    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    backend_calls: list[str] = []

    def unexpected_backend(**_kwargs: object) -> None:
        backend_calls.append("create_libvirt_backend")
        raise AssertionError("lock後のAgent再認可より先にbackendが呼ばれました")

    monkeypatch.setattr(
        domain_tasks,
        "create_libvirt_backend",
        unexpected_backend,
    )

    with Session(engine) as db:
        admin = UserModel(username="admin", hashed_password="unused")
        other = UserModel(username="other", hashed_password="unused")
        node = NodeModel(name="node-agent-lock")
        source = ProjectModel(
            id="aaaaaa",
            name="Agent source",
            users=[admin, other],
        )
        destination = ProjectModel(
            id="bbbbbb",
            name="Agent destination",
            users=[admin, other],
        )

        def vm(
            uuid: str,
            *,
            owner_user_id: str | None = None,
            owner_project: ProjectModel | None = None,
        ) -> DomainModel:
            model = DomainModel(
                uuid=uuid,
                name=uuid,
                core=1,
                memory=1024,
                status=5,
                update_token=f"{uuid}-token",
                storage_used=0,
                node=node,
                owner_project=owner_project,
            )
            model.owner_user_id = owner_user_id
            return model

        moved = vm("vm-agent-moved", owner_project=destination)
        membership_revoked = vm(
            "vm-agent-membership-revoked",
            owner_project=source,
        )
        personal_changed = vm(
            "vm-agent-personal-changed",
            owner_user_id=other.username,
        )
        db.add_all([
            source,
            destination,
            node,
            moved,
            membership_revoked,
            personal_changed,
        ])
        db.commit()

        def agent_task(
            *,
            uuid: str,
            project_id: str | None,
            object_name: str,
            method: str,
            body: dict[str, Any],
        ) -> tuple[TaskModel, TaskRequest]:
            target: dict[str, str] = {
                "resourceType": "vm",
                "resourceId": uuid,
                "nodeId": node.name,
            }
            if project_id is not None:
                target["projectId"] = project_id
            request = TaskRequest(path_param={"uuid": uuid}, body=body)
            return (
                TaskModel(
                    uuid=f"task-{uuid}-{object_name}",
                    post_time=datetime.now(UTC),
                    user_id=admin.username,
                    principal_id=admin.username,
                    lease_id="lease-agent-lock",
                    status="start",
                    resource="vm",
                    object=object_name,
                    method=method,
                    request=request.model_dump_json(),
                    resolved_targets=[target],
                ),
                request,
            )

        operations: list[tuple[Any, str, str, dict[str, Any]]] = [
            (domain_tasks.delete_vm_root, "root", "delete", {}),
            (domain_tasks.patch_vm_root, "power", "patch", {"status": "on"}),
            (
                domain_tasks.patch_vm_cdrom,
                "cdrom",
                "patch",
                {"target": "sda", "path": None},
            ),
            (
                domain_tasks.patch_vm_network,
                "network",
                "patch",
                {
                    "mac": "52:54:00:00:00:01",
                    "networkUuid": "not-used-after-owner-check",
                    "port": None,
                },
            ),
        ]
        for handler, object_name, method, body in operations:
            task, request = agent_task(
                uuid=moved.uuid,
                project_id=source.id,
                object_name=object_name,
                method=method,
                body=body,
            )
            with pytest.raises(AuthorizationError, match="Project binding"):
                handler(db, task, request)

        source.users.remove(admin)
        db.flush()
        membership_task, membership_request = agent_task(
            uuid=membership_revoked.uuid,
            project_id=source.id,
            object_name="power",
            method="patch",
            body={"status": "on"},
        )
        with pytest.raises(AuthorizationError, match="所属範囲外"):
            domain_tasks.patch_vm_root(db, membership_task, membership_request)

        personal_task, personal_request = agent_task(
            uuid=personal_changed.uuid,
            project_id=None,
            object_name="power",
            method="patch",
            body={"status": "on"},
        )
        with pytest.raises(AuthorizationError, match="個人owner"):
            domain_tasks.patch_vm_root(db, personal_task, personal_request)

    assert backend_calls == []


def test_project_membership_mutation_catalog_is_explicit() -> None:
    assert PROJECT_MEMBERSHIP_MUTATIONS == {
        "vm.create",
        "vm.delete",
        "vm.power.update",
        "vm.cdrom.update",
        "vm.network.update",
        "vm.project.update",
        "storage.metadata.update",
        "image.download",
        "image.flavor.update",
        "project.update",
        "project.member.add",
        "project.member.remove",
    }
    assert all(ACTIONS[action_id].mutation for action_id in PROJECT_MEMBERSHIP_MUTATIONS)


def test_global_mutation_catalog_requires_unscoped_lease() -> None:
    global_mutations = {
        action_id
        for action_id, definition in ACTIONS.items()
        if definition.mutation and action_id not in PROJECT_MEMBERSHIP_MUTATIONS
    }
    assert {
        "storage.pool.create",
        "storage.pool.update",
        "storage.pool.delete",
        "storage.create",
        "storage.delete",
        "image.delete",
        "network.pool.create",
        "network.pool.update",
        "network.pool.delete",
        "network.create",
        "network.delete",
        "network.ovs.create",
        "network.ovs.delete",
        "project.create",
        "project.delete",
        "project.resource-grants.update",
    } <= global_mutations

    for action_id in global_mutations:
        with pytest.raises(AuthorizationError) as project_denied:
            validate_mutation_lease_constraints(
                action_id=action_id,
                mutation=True,
                project_ids=["aaaaaa"],
                node_ids=[],
            )
        assert project_denied.value.code == (
            "global_mutation_requires_unscoped_lease"
        )
        with pytest.raises(AuthorizationError) as node_denied:
            validate_mutation_lease_constraints(
                action_id=action_id,
                mutation=True,
                project_ids=[],
                node_ids=["node-a"],
            )
        assert node_denied.value.code == "global_mutation_requires_unscoped_lease"
        validate_mutation_lease_constraints(
            action_id=action_id,
            mutation=True,
            project_ids=[],
            node_ids=[],
        )


def test_scoped_lease_cannot_mutate_resource_shared_with_another_project() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        admin = UserModel(username="admin", hashed_password="unused")
        other = UserModel(username="other", hashed_password="unused")
        node = NodeModel(name="node-a")
        storage = StorageModel(
            uuid="storage-shared",
            name="storage-shared",
            node_name=node.name,
            capacity=1024,
            available=512,
            path="/storage-shared",
            active=True,
            auto_start=True,
            status=1,
            update_token="storage-shared-token",
        )
        shared_pool = StoragePoolModel(
            name="pool-shared",
            storages=[AssociationStoragePoolModel(storage=storage)],
        )
        project_a = ProjectModel(
            id="aaaaaa",
            name="Project A",
            users=[admin],
            storage_pools=[shared_pool],
        )
        project_b = ProjectModel(
            id="bbbbbb",
            name="Project B",
            users=[other],
            storage_pools=[shared_pool],
        )
        image = ImageModel(
            name="shared.qcow2",
            storage=storage,
            capacity=1,
            allocation=1,
            path="/storage-shared/shared.qcow2",
            update_token="shared-image-token",
        )
        db.add_all([
            node,
            project_a,
            project_b,
            image,
            UserScopeModel(user_id=admin.username, name="admin"),
        ])
        db.commit()
        db.refresh(shared_pool)
        assert {
            project.id
            for project in db.query(ProjectModel).filter(
                ProjectModel.storage_pools.contains(shared_pool),
            )
        } == {project_a.id, project_b.id}

        cases: list[tuple[str, dict[str, Any], str, str]] = [
            (
                "storage.pool.update",
                {"id": shared_pool.id, "storageUuids": [storage.uuid]},
                "storage-pool",
                str(shared_pool.id),
            ),
            (
                "storage.pool.delete",
                {"id": shared_pool.id},
                "storage-pool",
                str(shared_pool.id),
            ),
            (
                "storage.delete",
                {"uuid": storage.uuid},
                "storage",
                storage.uuid,
            ),
            (
                "image.delete",
                {"uuid": storage.uuid, "name": image.name},
                "image",
                image.name,
            ),
        ]
        for action_id, input_value, resource_type, resource_id in cases:
            request = ActionRequest(
                input=input_value,
                target=ActionTarget(
                    resource_type=resource_type,
                    resource_id=resource_id,
                    project_id=project_a.id,
                    node_id=node.name,
                ),
                expected_generation="generation",
                idempotency_key=f"restricted-{action_id}",
            )
            for context in (
                _context(scopes=[action_id], projects=[project_a.id]),
                _context(scopes=[action_id], nodes=[node.name]),
            ):
                with pytest.raises(AuthorizationError) as denied:
                    actions.execute_action(
                        db,
                        context=context,
                        action_id=action_id,
                        request=request,
                    )
                assert denied.value.code == (
                    "global_mutation_requires_unscoped_lease"
                )

        unscoped = _context(scopes=["storage.pool.delete"])
        validate_mutation_lease_constraints(
            action_id="storage.pool.delete",
            mutation=True,
            project_ids=unscoped.lease.project_ids,
            node_ids=unscoped.lease.node_ids,
        )
        _validate_identity_admin_scope(
            db,
            unscoped,
            ACTIONS["storage.pool.delete"],
            SimpleNamespace(id=shared_pool.id),
        )


def test_global_resource_reference_validation_does_not_require_a_grant(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """明示global操作はunscoped leaseで通常read用grant helperを使わない。"""

    storage = SimpleNamespace(uuid="storage-a", node_name="node-a")
    network = SimpleNamespace(uuid="network-a", node_name="node-a")

    class FakeDB:
        @staticmethod
        def get(model: object, key: object) -> object | None:
            name = getattr(model, "__name__", "")
            if name == "StorageModel" and key == storage.uuid:
                return storage
            if name == "NetworkModel" and key == network.uuid:
                return network
            return None

    monkeypatch.setattr(
        actions,
        "_allowed_storage_ids",
        lambda *_: pytest.fail("global storage操作でgrant helperを呼んではならない"),
    )
    monkeypatch.setattr(
        actions,
        "_allowed_network_ids",
        lambda *_: pytest.fail("global network操作でgrant helperを呼んではならない"),
    )
    db = _session(FakeDB())
    context = _context(scopes=[
        "storage.pool.create",
        "image.delete",
        "network.pool.update",
    ])

    storage_pool = _validate_action_references(
        db,
        context=context,
        definition=ACTIONS["storage.pool.create"],
        model=SimpleNamespace(storage_uuids=[storage.uuid]),
        target=ResolvedTarget("storage-pool", "storage.pool.create", None, None),
    )
    image_delete = _validate_action_references(
        db,
        context=context,
        definition=ACTIONS["image.delete"],
        model=SimpleNamespace(uuid=storage.uuid),
        target=ResolvedTarget("image", "image-a", None, storage.node_name),
    )
    network_pool = _validate_action_references(
        db,
        context=context,
        definition=ACTIONS["network.pool.update"],
        model=SimpleNamespace(network_uuid=network.uuid),
        target=ResolvedTarget("network-pool", "1", None, None),
    )
    assert {item["resourceId"] for item in storage_pool.related_targets} == {
        storage.uuid,
    }
    assert {item["resourceId"] for item in image_delete.related_targets} == {
        storage.uuid,
    }
    assert {item["resourceId"] for item in network_pool.related_targets} == {
        network.uuid,
    }


def test_public_schemas_reject_unknown_fields_and_empty_allowed_scopes() -> None:
    with pytest.raises(ValidationError):
        PairingCreateRequest.model_validate({
            "deviceName": "codex",
            "publicKeyJwk": {
                "kty": "EC",
                "crv": "P-256",
                "x": "A" * 43,
                "y": "B" * 43,
            },
            "requestedScopes": ["vm.list"],
            "unexpectedSecret": "never echo this",
        })
    with pytest.raises(ValidationError):
        PairingApproveRequest.model_validate({
            "pairingCode": "a" * 16,
            "challengeId": "challenge",
            "credential": {
                "id": "credential",
                "rawId": "credential",
                "type": "public-key",
                "response": {},
            },
            "allowedScopes": [],
        })
    with pytest.raises(ValidationError):
        PairingApproveRequest.model_validate({
            "pairingCode": "a" * 16,
            "challengeId": "challenge",
            "credential": {
                "id": "credential",
                "rawId": "credential",
                "type": "public-key",
                "response": {},
            },
            "allowedScopes": ["vm.get", "vm.get"],
        })
    with pytest.raises(ValidationError):
        LeaseRequest.model_validate({
            "deviceId": "device-1",
            "principalId": "admin",
            "requestedScopes": ["vm.get"],
            "projectIds": ["p1", "p1"],
        })
    with pytest.raises(ValidationError):
        LeaseRequest.model_validate({
            "deviceId": "device-1",
            "principalId": "admin",
            "requestedScopes": ["vm.get"],
            "nodeIds": ["n" * 256],
        })


def test_agent_route_sanitizes_request_validation_errors() -> None:
    validation_router = APIRouter(route_class=AgentAPIRoute)

    @validation_router.post("/validate")
    def validate(body: dict[str, int]) -> dict[str, bool]:
        return {"accepted": bool(body)}

    application = FastAPI()
    application.include_router(validation_router)
    secret = "password=DoNotReturnThisSecret"

    response = TestClient(application).post(
        "/validate",
        json={"unexpectedSecret": secret},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == {
        "code": "validation_error",
        "message": "Request validation failed.",
        "errors": [
            {
                "field": "body.unexpectedSecret",
                "code": "invalid_type",
                "params": {"expected": "integer"},
            }
        ],
    }
    assert response.headers["cache-control"] == "no-store"
    assert secret not in response.text
    assert "input" not in response.text


def test_vm_create_requires_owner_project_in_public_input() -> None:
    payload = {
        "type": "manual",
        "name": "agent-vm",
        "nodeName": "node-1",
        "projectId": "a1b2c3",
        "memoryMegaByte": 1024,
        "cpu": 1,
        "disks": [],
        "interface": [],
    }
    _validate_public_json("vm.create", payload)
    model = actions._load_input_model(ACTIONS["vm.create"], payload)
    assert model.project_id == "a1b2c3"
    with pytest.raises(AgentError, match="input"):
        _validate_public_json(
            "vm.create",
            {key: value for key, value in payload.items() if key != "projectId"},
        )


def test_image_flavor_update_requires_explicit_project() -> None:
    payload = {
        "projectId": "a1b2c3",
        "storageUuid": "storage-1",
        "path": "/images/base.qcow2",
        "nodeName": "node-1",
        "flavorId": 1,
    }
    _validate_public_json("image.flavor.update", payload)
    model = actions._load_input_model(ACTIONS["image.flavor.update"], payload)
    assert model.project_id == "a1b2c3"

    with pytest.raises(AgentError, match="input"):
        actions._load_input_model(
            ACTIONS["image.flavor.update"],
            {key: value for key, value in payload.items() if key != "projectId"},
        )


def test_project_resource_grant_candidates_requires_explicit_project() -> None:
    payload = {"projectId": "a1b2c3"}
    _validate_public_json("project.resource-grant-candidates.get", payload)
    model = actions._load_input_model(
        ACTIONS["project.resource-grant-candidates.get"],
        payload,
    )
    assert model.project_id == "a1b2c3"


def test_agent_update_models_keep_fields_removed_from_rest_bodies() -> None:
    vm_model = actions._load_input_model(
        ACTIONS["vm.project.update"],
        {"uuid": "vm-1", "projectId": "a1b2c3"},
    )
    assert vm_model.uuid == "vm-1"
    assert vm_model.project_id == "a1b2c3"

    user_payload = {
        "pathUsername": "alice",
        "username": "alice",
        "password": "Virty-Test_2026!",
        "scopes": [{"name": "user"}],
        "publickeys": [{"name": "main", "publickey": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6MDEyMzQ1"}],
    }
    _validate_public_json("user.update", user_payload)
    user_model = actions._load_input_model(ACTIONS["user.update"], user_payload)
    assert user_model.path_username == "alice"
    assert user_model.username == "alice"
    assert user_model.password == "Virty-Test_2026!"
    assert not hasattr(user_model, "projects")

    with pytest.raises(AgentError, match="input"):
        _validate_public_json(
            "user.update",
            {**user_payload, "projects": [{"id": "a1b2c3", "name": "Project"}]},
        )


def test_project_actions_use_dedicated_member_and_grant_inputs() -> None:
    project_id = "a1b2c3"
    update = actions._load_input_model(
        ACTIONS["project.update"],
        {"projectId": project_id, "name": "Platform"},
    )
    member = actions._load_input_model(
        ACTIONS["project.member.remove"],
        {"projectId": project_id, "username": "alice"},
    )
    grants = actions._load_input_model(
        ACTIONS["project.resource-grants.update"],
        {
            "projectId": project_id,
            "storagePoolIds": [1],
            "networkPoolIds": [2],
            "flavorIds": [3],
        },
    )

    assert update.name == "Platform"
    assert member.username == "alice"
    assert grants.storage_pool_ids == [1]
    assert grants.network_pool_ids == [2]
    assert grants.flavor_ids == [3]
    assert "projects" not in public_input_schema("user.create")["properties"]
    assert "projects" not in public_input_schema("user.update")["properties"]


def test_project_generation_includes_members_limits_and_resource_grants() -> None:
    project = SimpleNamespace(
        id="a1b2c3",
        name="Platform",
        users=[SimpleNamespace(username="alice")],
        core=8,
        memory_g=16,
        storage_capacity_g=128,
        storage_pools=[],
        network_pools=[],
        flavors=[],
    )

    class FakeDB:
        @staticmethod
        def get(_: object, key: object) -> object | None:
            return project if key == project.id else None

    db = _session(FakeDB())
    initial = resolve_generation(
        db,
        resource_type="project",
        resource_id=project.id,
    )
    project.users.append(SimpleNamespace(username="bob"))
    member_changed = resolve_generation(
        db,
        resource_type="project",
        resource_id=project.id,
    )
    project.core = 12
    limit_changed = resolve_generation(
        db,
        resource_type="project",
        resource_id=project.id,
    )
    project.storage_pools.append(SimpleNamespace(id=7))
    grant_changed = resolve_generation(
        db,
        resource_type="project",
        resource_id=project.id,
    )

    assert len({initial, member_changed, limit_changed, grant_changed}) == 4


def test_py_webauthn_v3_registration_options_accept_binary_descriptors() -> None:
    backend = PythonWebAuthnBackend(
        rp_id="virty.internal",
        origin="https://virty.internal",
        rp_name="Virty",
    )
    options = backend.registration_options(
        challenge=b"c" * 32,
        user_id="admin",
        user_name="admin",
        excluded_credential_ids=[base64url_encode(b"credential-id")],
    )
    assert options["rp"]["id"] == "virty.internal"
    assert options["excludeCredentials"][0]["id"] == base64url_encode(
        b"credential-id",
    )


def test_webauthn_challenge_is_subject_bound_and_single_use(tmp_path: Path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'webauthn.sqlite'}")
    UserModel.__table__.create(engine)
    AgentWebAuthnCredentialModel.__table__.create(engine)
    AgentWebAuthnChallengeModel.__table__.create(engine)

    class FakeBackend:
        @staticmethod
        def verify_authentication(**_: object) -> AuthenticationVerification:
            return AuthenticationVerification(new_sign_count=2)

    now = datetime.now(UTC)
    with Session(engine) as db:
        db.add(UserModel(username="admin", hashed_password="unused"))
        db.add(new_agent_model(
            AgentWebAuthnCredentialModel,
            credential_id="credential-1",
            user_id="admin",
            name="security-key",
            credential_public_key=b"public-key",
            sign_count=1,
            transports=[],
            created_at=now,
        ))
        db.add_all([
            new_agent_model(
                AgentWebAuthnChallengeModel,
                id="challenge-1",
                user_id="admin",
                purpose="lease",
                subject_id="lease-request-1",
                challenge=b"c" * 32,
                created_at=now,
                expires_at=now + timedelta(minutes=5),
            ),
            new_agent_model(
                AgentWebAuthnChallengeModel,
                id="challenge-2",
                user_id="admin",
                purpose="lease",
                subject_id="lease-request-2",
                challenge=b"d" * 32,
                created_at=now,
                expires_at=now + timedelta(minutes=5),
            ),
        ])
        db.commit()

        service = WebAuthnService(
            backend=cast(WebAuthnBackend, FakeBackend()),
        )
        with pytest.raises(AuthenticationError, match="対象が一致"):
            service.verify_authentication(
                db,
                user_id="admin",
                purpose="pairing",
                subject_id="lease-request-2",
                challenge_id="challenge-2",
                credential={"id": "credential-1", "response": {}},
            )
        service.verify_authentication(
            db,
            user_id="admin",
            purpose="lease",
            subject_id="lease-request-1",
            challenge_id="challenge-1",
            credential={"id": "credential-1", "response": {}},
        )
        db.commit()
        consumed = db.get(AgentWebAuthnChallengeModel, "challenge-1")
        assert consumed is not None
        assert consumed.used_at is not None
        with pytest.raises(ConflictError, match="既に使用"):
            service.verify_authentication(
                db,
                user_id="admin",
                purpose="lease",
                subject_id="lease-request-1",
                challenge_id="challenge-1",
                credential={"id": "credential-1", "response": {}},
            )


def test_audit_redacts_nested_fields_and_free_text_credentials() -> None:
    private_key = (
        "-----BEGIN PRIVATE KEY-----\nsecret material\n"
        "-----END PRIVATE KEY-----"
    )
    jwt_value = "a" * 12 + "." + "b" * 12 + "." + "c" * 12
    value = redact_secrets({
        "reason": f"password=hunter2 {jwt_value} {private_key}",
        "nested": {"accessToken": "token-value"},
    })
    serialized = json.dumps(value)
    assert "hunter2" not in serialized
    assert jwt_value not in serialized
    assert "secret material" not in serialized
    assert "token-value" not in serialized


def test_dpop_replay_consumption_survives_business_rollback(tmp_path: Path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'dpop.sqlite'}")
    UserModel.__table__.create(engine)
    AgentDeviceModel.__table__.create(engine)
    AgentDpopReplayModel.__table__.create(engine)
    with Session(engine) as seed:
        seed.add(new_agent_model(
            AgentDeviceModel,
            id="device-1",
            name="codex",
            public_key_jwk={"kty": "EC"},
            public_key_thumbprint="f" * 64,
            allowed_scopes=[],
            status="active",
        ))
        seed.commit()

    business = Session(engine)
    assert business.get(AgentDeviceModel, "device-1") is not None
    _consume_dpop_replay(
        business,
        device_id="device-1",
        jti="proof-1",
        now=datetime.now(UTC),
    )
    business.rollback()
    business.close()

    with Session(engine) as check:
        assert check.get(AgentDpopReplayModel, ("device-1", "proof-1")) is not None
        with pytest.raises(ConflictError, match="既に使用"):
            _consume_dpop_replay(
                check,
                device_id="device-1",
                jti="proof-1",
                now=datetime.now(UTC),
            )


def test_deleted_principal_cannot_resurrect_old_lease_or_queued_task(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AGENT_LEASE_SIGNING_KEY", "t" * 32)
    engine = create_engine(f"sqlite:///{tmp_path / 'principal-binding.sqlite'}")

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection: sqlite3.Connection, _: object) -> None:
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    UserModel.__table__.create(engine)
    UserScopeModel.__table__.create(engine)
    AgentDeviceModel.__table__.create(engine)
    AgentCapabilityLeaseModel.__table__.create(engine)
    now = datetime.now(UTC)
    expires_at = now + timedelta(minutes=30)
    token = create_capability_token(
        lease_id="lease-1",
        jti="lease-jti-1",
        principal_id="admin",
        device_id="device-1",
        device_thumbprint="f" * 64,
        scopes=["vm.list"],
        project_ids=[],
        node_ids=[],
        max_mutations=20,
        allow_destructive=False,
        allow_delete_without_recovery=False,
        allow_network_change_without_oob=False,
        issued_at=now,
        expires_at=expires_at,
    )
    with Session(engine) as db:
        db.execute(UserModel.__table__.insert().values(
            username="admin",
            hashed_password="old",
        ))
        db.add(new_agent_model(
            AgentDeviceModel,
            id="device-1",
            principal_id="admin",
            name="codex",
            public_key_jwk={"kty": "EC"},
            public_key_thumbprint="f" * 64,
            allowed_scopes=["vm.list"],
            status="active",
        ))
        db.flush()
        db.add(new_agent_model(
            AgentCapabilityLeaseModel,
            id="lease-1",
            jti="lease-jti-1",
            principal_id="admin",
            device_id="device-1",
            token_hash=sha256_hex(token),
            scopes=["vm.list"],
            project_ids=[],
            node_ids=[],
            max_mutations=20,
            mutations_used=0,
            issued_at=now,
            expires_at=expires_at,
        ))
        db.commit()

        db.execute(UserModel.__table__.delete().where(
            UserModel.username == "admin",
        ))
        db.commit()
        db.execute(UserModel.__table__.insert().values(
            username="admin",
            hashed_password="replacement",
        ))
        db.execute(UserScopeModel.__table__.insert().values(
            user_id="admin",
            name="admin",
        ))
        db.commit()
        db.expire_all()
        persisted_device = db.get(AgentDeviceModel, "device-1")
        assert persisted_device is not None
        assert persisted_device.principal_id is None

        with pytest.raises(AuthenticationError, match="現在の所有者"):
            authenticate_lease(
                db,
                authorization=f"DPoP {token}",
                dpop_proof="principal mismatchなので検証前に拒否される",
                method="GET",
                url="https://virty.internal/api/agent/v1/actions/vm.list",
            )
        with pytest.raises(AuthorizationError, match="principal束縛"):
            validate_worker_dispatch(
                db,
                SimpleNamespace(lease_id="lease-1"),
            )


def test_mutation_concurrency_limit_is_global_across_leases(
    tmp_path: Path,
) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'concurrency.sqlite'}")
    UserModel.__table__.create(engine)
    TaskModel.__table__.create(engine)
    with Session(engine) as db:
        db.add_all([
            TaskModel(
                uuid=f"task-{index}",
                principal_id="admin",
                lease_id=f"lease-device-{index}",
                correlation_id=f"operation-{index}",
                status="init",
                risk="R3" if index == 0 else "R2",
            )
            for index in range(3)
        ])
        db.commit()

        with pytest.raises(ConflictError, match="全端末"):
            _check_concurrency(db, "R2")

        completed = db.get(TaskModel, "task-2")
        assert completed is not None
        completed.status = "finish"
        db.flush()
        _check_concurrency(db, "R2")
        with pytest.raises(ConflictError, match="全端末"):
            _check_concurrency(db, "R3")


def test_worker_rechecks_catalog_scope_risk_and_safety_flags() -> None:
    class RootOnlyDB:
        @staticmethod
        def get(*_: object) -> None:
            return None

    db = _session(RootOnlyDB())
    task = _task(SimpleNamespace(
        uuid="task-1",
        dependence_uuid=None,
        correlation_id=None,
        method="delete",
        resource="node",
        object="root",
        principal_id="admin",
        user_id="admin",
        risk="R3",
    ))
    lease = _lease(SimpleNamespace(
        principal_id="admin",
        scopes=["node.delete"],
        allow_destructive=True,
        allow_delete_without_recovery=True,
        allow_network_change_without_oob=True,
    ))
    control = _control(SimpleNamespace(
        allow_delete_without_recovery=True,
        allow_network_change_without_oob=True,
    ))
    definition = ACTIONS["node.delete"]
    _validate_dispatch_action_contract(
        db,
        task=task,
        lease=lease,
        control=control,
        definition=definition,
    )

    task.principal_id = "another-admin"
    with pytest.raises(AuthorizationError, match="task principal"):
        _validate_dispatch_action_contract(
            db,
            task=task,
            lease=lease,
            control=control,
            definition=definition,
        )
    task.principal_id = "admin"
    lease.scopes = ["vm.get"]
    with pytest.raises(AuthorizationError, match="scope"):
        _validate_dispatch_action_contract(
            db,
            task=task,
            lease=lease,
            control=control,
            definition=definition,
        )
    lease.scopes = ["node.delete"]
    task.risk = "R2"
    with pytest.raises(AuthorizationError, match="risk"):
        _validate_dispatch_action_contract(
            db,
            task=task,
            lease=lease,
            control=control,
            definition=definition,
        )
    task.risk = "R3"
    control.allow_delete_without_recovery = False
    with pytest.raises(AuthorizationError, match="復旧手段"):
        _validate_dispatch_action_contract(
            db,
            task=task,
            lease=lease,
            control=control,
            definition=definition,
        )

    network_task = _task(SimpleNamespace(
        uuid="task-2",
        dependence_uuid=None,
        correlation_id=None,
        method="patch",
        resource="vm",
        object="network",
        principal_id="admin",
        user_id="admin",
        risk="R3",
    ))
    network_lease = _lease(SimpleNamespace(
        principal_id="admin",
        scopes=["vm.network.update"],
        allow_destructive=True,
        allow_delete_without_recovery=True,
        allow_network_change_without_oob=True,
    ))
    network_control = _control(SimpleNamespace(
        allow_delete_without_recovery=True,
        allow_network_change_without_oob=False,
    ))
    with pytest.raises(AuthorizationError, match="帯域外復旧"):
        _validate_dispatch_action_contract(
            db,
            task=network_task,
            lease=network_lease,
            control=network_control,
            definition=ACTIONS["vm.network.update"],
        )


def test_worker_requires_identity_admin_after_target_is_promoted() -> None:
    target_user = SimpleNamespace(
        username="target-user",
        scopes=[SimpleNamespace(name="admin")],
    )

    class FakeDB:
        @staticmethod
        def get(model: object, key: object) -> object | None:
            if getattr(model, "__name__", "") == "UserModel" and key == "target-user":
                return target_user
            return None

    db = _session(FakeDB())
    task = _task(SimpleNamespace(
        uuid="user-update",
        dependence_uuid=None,
        correlation_id=None,
        method="agent",
        resource="direct",
        object="user.update",
        principal_id="admin",
        user_id="admin",
        risk="R3",
        resolved_targets=[{
            "resourceType": "user",
            "resourceId": "target-user",
            "generationTarget": "true",
        }],
    ))
    lease = _lease(SimpleNamespace(
        principal_id="admin",
        scopes=["user.update"],
        allow_destructive=True,
        allow_delete_without_recovery=False,
        allow_network_change_without_oob=False,
    ))
    control = _control(SimpleNamespace(
        allow_delete_without_recovery=False,
        allow_network_change_without_oob=False,
    ))
    with pytest.raises(AuthorizationError, match="identity.admin"):
        _validate_dispatch_action_contract(
            db,
            task=task,
            lease=lease,
            control=control,
            definition=ACTIONS["user.update"],
        )

    lease.scopes.append("identity.admin")
    _validate_dispatch_action_contract(
        db,
        task=task,
        lease=lease,
        control=control,
        definition=ACTIONS["user.update"],
    )


def test_worker_rejects_unknown_or_unrelated_dependent_selector() -> None:
    root = _task(SimpleNamespace(
        uuid="root",
        dependence_uuid=None,
        correlation_id=None,
        method="post",
        resource="node",
        object="root",
        principal_id="admin",
        user_id="admin",
        risk="R2",
    ))
    malicious = _task(SimpleNamespace(
        uuid="child",
        dependence_uuid="root",
        correlation_id=None,
        method="delete",
        resource="vm",
        object="root",
        principal_id="admin",
        user_id="admin",
        risk="R2",
    ))

    class FakeDB:
        @staticmethod
        def get(_: object, key: str) -> object | None:
            return root if key == "root" else None

    db = _session(FakeDB())
    assert _task_action_id(db, malicious) == "node.create"
    with pytest.raises(AuthorizationError, match="selector"):
        _validate_dispatch_action_contract(
            db,
            task=malicious,
            lease=_lease(SimpleNamespace(
                principal_id="admin",
                scopes=["node.create"],
                allow_destructive=False,
                allow_delete_without_recovery=False,
                allow_network_change_without_oob=False,
            )),
            control=_control(SimpleNamespace(
                allow_delete_without_recovery=False,
                allow_network_change_without_oob=False,
            )),
            definition=ACTIONS["node.create"],
        )

    unknown_root = _task(SimpleNamespace(
        uuid="unknown",
        dependence_uuid=None,
        correlation_id=None,
        method="post",
        resource="secret",
        object="proxy",
        principal_id="admin",
        user_id="admin",
    ))
    assert _task_action_id(db, unknown_root).startswith("internal.")
    assert _task_action_id(db, unknown_root) not in ACTIONS

    direct_root = _task(SimpleNamespace(
        uuid="direct-root",
        dependence_uuid=None,
        correlation_id=None,
        method="agent",
        resource="direct",
        object="user.create",
        principal_id="admin",
        user_id="admin",
        risk="R3",
    ))
    direct_child = _task(SimpleNamespace(
        uuid="direct-child",
        dependence_uuid="direct-root",
        correlation_id=None,
        method="delete",
        resource="node",
        object="root",
        principal_id="admin",
        user_id="admin",
        risk="R3",
    ))

    class DirectDB:
        @staticmethod
        def get(_: object, key: str) -> object | None:
            return direct_root if key == "direct-root" else None

    with pytest.raises(AuthorizationError, match="selector"):
        _validate_dispatch_action_contract(
            _session(DirectDB()),
            task=direct_child,
            lease=_lease(SimpleNamespace(
                principal_id="admin",
                scopes=["user.create", "identity.admin"],
                allow_destructive=True,
                allow_delete_without_recovery=True,
                allow_network_change_without_oob=True,
            )),
            control=_control(SimpleNamespace(
                allow_delete_without_recovery=True,
                allow_network_change_without_oob=True,
            )),
            definition=ACTIONS["user.create"],
        )


def test_worker_rejects_multiple_operation_roots(
    tmp_path: Path,
) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'multiple-roots.sqlite'}")
    UserModel.__table__.create(engine)
    TaskModel.__table__.create(engine)
    now = datetime.now(UTC)
    with Session(engine) as db:
        db.add_all([
            TaskModel(
                uuid=f"root-{index}",
                post_time=now + timedelta(seconds=index),
                principal_id="admin",
                correlation_id="same-operation",
                status="init",
                method="post",
                resource="node",
                object="root",
                risk="R2",
            )
            for index in range(2)
        ])
        db.commit()

        duplicate_root = db.get(TaskModel, "root-1")
        assert duplicate_root is not None
        with pytest.raises(AuthorizationError, match="root"):
            _validate_dispatch_action_contract(
                db,
                task=duplicate_root,
                lease=_lease(SimpleNamespace(
                    principal_id="admin",
                    scopes=["node.create"],
                    allow_destructive=False,
                    allow_delete_without_recovery=False,
                    allow_network_change_without_oob=False,
                )),
                control=_control(SimpleNamespace(
                    allow_delete_without_recovery=False,
                    allow_network_change_without_oob=False,
                )),
                definition=ACTIONS["node.create"],
            )


def test_create_dependent_uses_root_sentinel_and_rechecks_related_targets() -> None:
    project = SimpleNamespace(
        id="p1",
        storage_pools=[SimpleNamespace(
            storages=[SimpleNamespace(storage_uuid="storage-1")],
        )],
        network_pools=[],
        flavors=[],
    )
    node = SimpleNamespace(name="node-1")
    storage = SimpleNamespace(uuid="storage-1", node_name="node-1")
    root = SimpleNamespace(
        uuid="vm-create-root",
        dependence_uuid=None,
        correlation_id="vm-create-operation",
        method="post",
        resource="vm",
        object="root",
        principal_id="admin",
        user_id="admin",
        expected_generation="0",
    )
    dependent = SimpleNamespace(
        uuid="vm-create-refresh",
        dependence_uuid=root.uuid,
        correlation_id=root.correlation_id,
        method="put",
        resource="vm",
        object="list",
        principal_id="admin",
        user_id="admin",
        expected_generation=None,
        resolved_targets=[
            {
                "resourceType": "vm",
                "resourceId": "not-created-yet",
                "projectId": "p1",
                "nodeId": "node-1",
            },
            {
                "resourceType": "storage",
                "resourceId": "storage-1",
                "projectId": "p1",
                "nodeId": "node-1",
            },
        ],
    )
    storage_exists = True

    class RootQuery:
        def __init__(self, entity: object) -> None:
            self.entity = entity

        def filter(self, *_: object) -> "RootQuery":
            return self

        def order_by(self, *_: object) -> "RootQuery":
            return self

        def all(self) -> list[object]:
            if getattr(self.entity, "key", None) == "project_id":
                return [(project.id,)]
            return [root]

    class FakeDB:
        @staticmethod
        def query(entity: object, *_: object) -> RootQuery:
            return RootQuery(entity)

        @staticmethod
        def get(model: object, key: object) -> object | None:
            name = getattr(model, "__name__", "")
            if name == "TaskModel" and key == root.uuid:
                return root
            if name == "NodeModel" and key == node.name:
                return node
            if name == "ProjectModel" and key == project.id:
                return project
            if name == "StorageModel" and key == storage.uuid and storage_exists:
                return storage
            return None

    db = _session(FakeDB())
    lease = _lease(SimpleNamespace(
        principal_id="admin",
        project_ids=["p1"],
        node_ids=["node-1"],
    ))
    _validate_task_constraints(db, dependent, lease)

    storage_exists = False
    with pytest.raises(AuthorizationError, match="参照resource"):
        _validate_task_constraints(db, dependent, lease)


def test_worker_resolves_user_generation_target() -> None:
    user = SimpleNamespace(username="target-user")

    class FakeDB:
        @staticmethod
        def get(model: object, key: object) -> object | None:
            if getattr(model, "__name__", "") == "UserModel" and key == "target-user":
                return user
            return None

    _validate_related_target_binding(
        _session(FakeDB()),
        {
            "resourceType": "user",
            "resourceId": "target-user",
            "generationTarget": "true",
        },
        _lease(SimpleNamespace(project_ids=[], node_ids=[])),
    )


@pytest.mark.parametrize(
    ("claim", "value"),
    [("htm", 1), ("htu", False), ("iat", True), ("jti", ["bad"])],
)
def test_malformed_dpop_claims_are_normalized_to_authentication_error(
    claim: str,
    value: object,
) -> None:
    private_key = ec.generate_private_key(ec.SECP256R1())
    numbers = private_key.public_key().public_numbers()
    jwk = {
        "kty": "EC",
        "crv": "P-256",
        "x": base64url_encode(numbers.x.to_bytes(32, "big")),
        "y": base64url_encode(numbers.y.to_bytes(32, "big")),
    }
    claims: dict[str, object] = {
        "htm": "POST",
        "htu": "https://virty.internal/api/agent/v1/leases",
        "iat": int(datetime.now(UTC).timestamp()),
        "jti": "proof-1",
    }
    claims[claim] = value
    proof = jwt.encode(
        claims,
        private_key,
        algorithm="ES256",
        headers={"typ": "dpop+jwt", "jwk": jwk},
    )
    device = _device(SimpleNamespace(
        id="device-1",
        public_key_thumbprint=jwk_thumbprint(jwk),
    ))
    with pytest.raises(AuthenticationError, match="claimの型"):
        verify_dpop_proof(
            _session(SimpleNamespace()),
            proof=proof,
            device=device,
            method="POST",
            url="https://virty.internal/api/agent/v1/leases",
        )


def test_server_derives_vm_scope_and_ignores_client_project_node() -> None:
    vm = SimpleNamespace(
        uuid="vm-1",
        owner_project_id="project-real",
        node_name="node-real",
    )

    class FakeDB:
        @staticmethod
        def get(model: object, key: object) -> object | None:
            if getattr(model, "__name__", "") == "DomainModel" and key == "vm-1":
                return vm
            return None

    request = ActionRequest(
        input={"uuid": "vm-1"},
        target=ActionTarget(
            resource_type="vm",
            resource_id="vm-1",
            project_id="project-spoof",
            node_id="node-spoof",
        ),
    )
    target = resolve_action_target(
        _session(FakeDB()),
        context=_context(scopes=["vm.get"]),
        definition=ACTIONS["vm.get"],
        request=request,
        model=EmptyInput(),
    )
    assert target.project_id == "project-real"
    assert target.node_id == "node-real"


def test_vm_create_resolves_owner_project_and_enforces_lease_constraint() -> None:
    network = SimpleNamespace(uuid="network-1", node_name="node-1")
    port = SimpleNamespace(
        network_uuid=network.uuid,
        name="tenant-a",
        network=network,
    )
    project = SimpleNamespace(
        id="p1",
        storage_pools=[],
        network_pools=[SimpleNamespace(networks=[], ports=[port])],
        flavors=[],
    )
    principal = SimpleNamespace(projects=[project])
    node = SimpleNamespace(name="node-1")

    class FakeQuery:
        def __init__(self, entity: object) -> None:
            self.entity = entity

        def filter(self, *_: object) -> "FakeQuery":
            return self

        def all(self) -> list[object]:
            model = getattr(self.entity, "class_", self.entity)
            name = getattr(model, "__name__", "")
            if name == "ProjectModel":
                return [project]
            if name == "NodeModel":
                return [(node.name,)]
            if name == "NetworkModel":
                return [(network.uuid,)]
            return []

        def __iter__(self):
            return iter(self.all())

    class FakeDB:
        @staticmethod
        def query(entity: object, *_: object) -> FakeQuery:
            return FakeQuery(entity)

        @staticmethod
        def get(model: object, key: object) -> object | None:
            name = getattr(model, "__name__", "")
            if name == "ProjectModel" and key == project.id:
                return project
            if name == "NodeModel" and key == node.name:
                return node
            if name == "NetworkModel" and key == network.uuid:
                return network
            if name == "UserModel" and key == "admin":
                return principal
            return None

    model = SimpleNamespace(
        project_id="p1",
        node_name="node-1",
        disks=[],
        interface=[SimpleNamespace(
            network_uuid=network.uuid,
            port=port.name,
        )],
    )
    db = _session(FakeDB())
    resolved = _validate_action_references(
        db,
        context=_context(
            scopes=["vm.create"],
            projects=["p1"],
            nodes=["node-1"],
        ),
        definition=ACTIONS["vm.create"],
        model=model,
        target=ResolvedTarget("vm", "agent-vm", None, "node-1"),
    )
    assert resolved.project_id == "p1"
    assert any(
        item.get("resourceType") == "project"
        and item.get("resourceId") == "p1"
        for item in resolved.related_targets
    )

    with pytest.raises(AuthorizationError, match="network/port"):
        _validate_action_references(
            db,
            context=_context(
                scopes=["vm.create"],
                projects=["p1"],
                nodes=["node-1"],
            ),
            definition=ACTIONS["vm.create"],
            model=SimpleNamespace(
                project_id="p1",
                node_name="node-1",
                disks=[],
                interface=[SimpleNamespace(
                    network_uuid=network.uuid,
                    port="tenant-b",
                )],
            ),
            target=ResolvedTarget("vm", "agent-vm", None, "node-1"),
        )

    with pytest.raises(AuthorizationError, match="owner project"):
        _validate_action_references(
            db,
            context=_context(
                scopes=["vm.create"],
                projects=["p2"],
                nodes=["node-1"],
            ),
            definition=ACTIONS["vm.create"],
            model=model,
            target=ResolvedTarget("vm", "agent-vm", None, "node-1"),
        )


def test_agent_vm_copy_and_image_flavor_use_one_project_grant() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        user = UserModel(username="admin", hashed_password="unused")
        node = NodeModel(name="node-1")
        storage = StorageModel(
            uuid="storage-1",
            name="storage-1",
            node_name=node.name,
            path="/images",
        )
        pool = StoragePoolModel(
            name="pool-1",
            storages=[AssociationStoragePoolModel(storage=storage)],
        )
        flavor_a = FlavorModel(
            name="flavor-a",
            os="linux",
            manual_url="https://docs.example.invalid/a",
            icon="linux",
            cloud_init_ready=False,
            cloud_init_user="cloud-user",
            description="a",
        )
        flavor_b = FlavorModel(
            name="flavor-b",
            os="linux",
            manual_url="https://docs.example.invalid/b",
            icon="linux",
            cloud_init_ready=False,
            cloud_init_user="cloud-user",
            description="b",
        )
        project_a = ProjectModel(
            id="aaaaaa",
            name="Project A",
            users=[user],
            storage_pools=[pool],
            flavors=[flavor_a],
        )
        project_b = ProjectModel(
            id="bbbbbb",
            name="Project B",
            users=[user],
            flavors=[flavor_b],
        )
        cross_image = ImageModel(
            name="cross.qcow2",
            storage=storage,
            path="/images/cross.qcow2",
            flavor=flavor_b,
        )
        generic_image = ImageModel(
            name="generic.qcow2",
            storage=storage,
            path="/images/generic.qcow2",
            flavor=None,
        )
        db.add_all([
            node,
            project_a,
            project_b,
            cross_image,
            generic_image,
            UserScopeModel(user_id=user.username, name="admin"),
        ])
        db.flush()

        context = _context(
            scopes=["vm.create", "image.flavor.update"],
            projects=[project_a.id, project_b.id],
            nodes=[node.name],
        )

        listed = adapters.image_list(
            db,
            context,
            SimpleNamespace(
                project_id=project_a.id,
                limit=25,
                page=0,
                pool_uuid=None,
                node_name=None,
                name=None,
                name_like=None,
            ),
            None,
        )
        assert {row["name"] for row in listed["data"]} == {generic_image.name}

        def vm_input(source_name: str) -> SimpleNamespace:
            return SimpleNamespace(
                project_id=project_a.id,
                node_name=node.name,
                disks=[SimpleNamespace(
                    save_pool_uuid=storage.uuid,
                    original_pool_uuid=storage.uuid,
                    original_name=source_name,
                )],
                interface=[],
            )

        with pytest.raises(AuthorizationError, match="copy元image"):
            _validate_action_references(
                db,
                context=context,
                definition=ACTIONS["vm.create"],
                model=vm_input(cross_image.name),
                target=ResolvedTarget("vm", "cross-copy", None, node.name),
            )

        generic_target = _validate_action_references(
            db,
            context=context,
            definition=ACTIONS["vm.create"],
            model=vm_input(generic_image.name),
            target=ResolvedTarget("vm", "generic-copy", None, node.name),
        )
        assert any(
            item.get("resourceType") == "image"
            and item.get("projectId") == project_a.id
            for item in generic_target.related_targets
        )

        cross_flavor_update = SimpleNamespace(
            project_id=project_a.id,
            storage_uuid=storage.uuid,
            path=generic_image.path,
            node_name=node.name,
            flavor_id=flavor_b.id,
        )
        with pytest.raises(AuthorizationError, match="flavor"):
            _validate_action_references(
                db,
                context=context,
                definition=ACTIONS["image.flavor.update"],
                model=cross_flavor_update,
                target=ResolvedTarget(
                    "image",
                    '["storage-1","/images/generic.qcow2"]',
                    project_a.id,
                    node.name,
                ),
            )
        with pytest.raises(AuthorizationError, match="同じProject"):
            adapters.image_flavor_update(db, context, cross_flavor_update, None)

        allowed_update = SimpleNamespace(
            **{
                **vars(cross_flavor_update),
                "flavor_id": flavor_a.id,
            },
        )
        result = adapters.image_flavor_update(db, context, allowed_update, None)
        assert result["flavorId"] == flavor_a.id

        candidates = adapters.project_resource_grant_candidates(
            db,
            context,
            SimpleNamespace(project_id=project_a.id),
            None,
        )
        assert candidates == {
            "storagePools": [{"id": pool.id, "name": pool.name}],
            "networkPools": [],
            "flavors": [
                {"id": flavor_a.id, "name": flavor_a.name},
                {"id": flavor_b.id, "name": flavor_b.name},
            ],
        }

        db.query(UserScopeModel).filter(
            UserScopeModel.user_id == user.username,
            UserScopeModel.name == "admin",
        ).delete()
        with pytest.raises(AuthorizationError, match="global admin"):
            adapters.project_resource_grant_candidates(
                db,
                context,
                SimpleNamespace(project_id=project_a.id),
                None,
            )


def test_project_grant_replacement_can_reserve_new_resources() -> None:
    class EmptyQuery:
        def filter(self, *_: object) -> "EmptyQuery":
            return self

        @staticmethod
        def all() -> list[object]:
            return []

    class FakeDB:
        @staticmethod
        def query(*_: object) -> EmptyQuery:
            return EmptyQuery()

        @staticmethod
        def get(model: object, key: object) -> object | None:
            resources = {
                ("StoragePoolModel", 1),
                ("NetworkPoolModel", 2),
                ("FlavorModel", 3),
            }
            return object() if (getattr(model, "__name__", ""), key) in resources else None

    resolved = _validate_action_references(
        _session(FakeDB()),
        context=_context(scopes=["project.resource-grants.update"]),
        definition=ACTIONS["project.resource-grants.update"],
        model=SimpleNamespace(
            project_id="p1",
            storage_pool_ids=[1],
            network_pool_ids=[2],
            flavor_ids=[3],
        ),
        target=ResolvedTarget("project", "p1", "p1", None),
    )

    assert {
        (item["resourceType"], item["resourceId"])
        for item in resolved.related_targets
    } == {
        ("storage-pool", "1"),
        ("network-pool", "2"),
        ("flavor", "3"),
    }
    assert all(
        item.get("authorizationTarget") == "false"
        for item in resolved.related_targets
    )


def test_agent_project_mutation_requires_principal_membership() -> None:
    project = SimpleNamespace(
        id="p1",
        users=[SimpleNamespace(username="member")],
        storage_pools=[],
        network_pools=[],
        flavors=[],
    )
    principal = SimpleNamespace(projects=[])

    class FakeDB:
        @staticmethod
        def get(model: object, key: object) -> object | None:
            if getattr(model, "__name__", "") == "ProjectModel" and key == "p1":
                return project
            if getattr(model, "__name__", "") == "UserModel" and key == "admin":
                return principal
            return None

    db = _session(FakeDB())
    with pytest.raises(NotFoundError, match="project"):
        _agent_project(db, _context(scopes=["project.manage"]), "p1")

    project.users.append(SimpleNamespace(username="admin"))
    principal.projects.append(project)
    assert _agent_project(
        db,
        _context(scopes=["project.manage"]),
        "p1",
    ) is project

    class LockQuery:
        locked = False

        def filter(self, *args: object) -> "LockQuery":
            return self

        def with_for_update(self) -> "LockQuery":
            self.locked = True
            return self

        @staticmethod
        def scalar() -> str:
            return "p1"

    lock_query = LockQuery()

    class LockingDB(FakeDB):
        @staticmethod
        def query(model: object) -> LockQuery:
            return lock_query

        @staticmethod
        def expire(_: object, __: object) -> None:
            return None

    assert _agent_project(
        _session(LockingDB()),
        _context(scopes=["project.resource-grants.update"]),
        "p1",
        allow_admin=True,
        lock=True,
    ) is project
    assert lock_query.locked is True


def test_long_signed_image_url_is_hashed_instead_of_target_resource_id() -> None:
    signed_url = "https://images.example.invalid/file?signature=" + "x" * 1000
    _validate_public_json(
        "image.download",
        {"storageUuid": "storage-1", "imageUrl": signed_url},
    )
    storage = SimpleNamespace(uuid="storage-1", node_name="node-1")

    class EmptyQuery:
        @staticmethod
        def all() -> list[object]:
            return []

    class FakeDB:
        @staticmethod
        def get(model: object, key: object) -> object | None:
            if getattr(model, "__name__", "") == "StorageModel" and key == "storage-1":
                return storage
            return None

        @staticmethod
        def query(*_: object) -> EmptyQuery:
            return EmptyQuery()

    db = _session(FakeDB())
    target = resolve_action_target(
        db,
        context=_context(scopes=["image.download"]),
        definition=ACTIONS["image.download"],
        request=ActionRequest(
            input={"storageUuid": "storage-1", "imageUrl": signed_url},
            target=ActionTarget(resource_type="image"),
        ),
        model=SimpleNamespace(storage_uuid="storage-1", image_url=signed_url),
    )
    assert target.resource_id is not None
    assert target.resource_id.startswith("sha256:")
    assert signed_url not in target.resource_id
    assert len(target.resource_id) <= 256

    same_destination = resolve_action_target(
        db,
        context=_context(scopes=["image.download"]),
        definition=ACTIONS["image.download"],
        request=ActionRequest(
            input={
                "storageUuid": "storage-1",
                "imageUrl": "https://mirror.example.invalid/file?token=different",
            },
            target=ActionTarget(resource_type="image"),
        ),
        model=SimpleNamespace(
            storage_uuid="storage-1",
            image_url="https://mirror.example.invalid/file?token=different",
        ),
    )
    assert same_destination.resource_id == target.resource_id


def test_image_generation_target_uses_canonical_id_and_server_project() -> None:
    image = SimpleNamespace(
        storage_uuid="storage-1",
        path="/images/base.qcow2",
        name="base.qcow2",
    )
    storage = SimpleNamespace(uuid="storage-1", node_name="node-1")
    association = SimpleNamespace(storage_uuid="storage-1")
    project = SimpleNamespace(
        id="p1",
        storage_pools=[SimpleNamespace(storages=[association])],
        network_pools=[],
        flavors=[],
    )

    class FakeQuery:
        def __init__(self, model: object) -> None:
            self.model = model

        def filter(self, *_: object) -> "FakeQuery":
            return self

        def one_or_none(self) -> object | None:
            return image if getattr(self.model, "__name__", "") == "ImageModel" else None

        def all(self) -> list[object]:
            return [project] if getattr(self.model, "__name__", "") == "ProjectModel" else []

    class FakeDB:
        @staticmethod
        def get(model: object, key: object) -> object | None:
            if getattr(model, "__name__", "") == "StorageModel" and key == "storage-1":
                return storage
            return None

        @staticmethod
        def query(model: object, *_: object) -> FakeQuery:
            return FakeQuery(model)

    target = resolve_action_target(
        _session(FakeDB()),
        context=_context(scopes=["image.flavor.update"], projects=["p1"]),
        definition=ACTIONS["image.flavor.update"],
        request=ActionRequest(
            input={
                "projectId": "p1",
                "storageUuid": "storage-1",
                "path": "/images/base.qcow2",
                "nodeName": "node-1",
                "flavorId": 1,
            },
            target=ActionTarget(
                resource_type="image",
                resource_id="/images/base.qcow2",
                project_id="p1",
                node_id="node-1",
            ),
            expected_generation="generation",
            idempotency_key="idempotency-1",
        ),
        model=SimpleNamespace(
            project_id="p1",
            storage_uuid="storage-1",
            path="/images/base.qcow2",
        ),
    )
    assert target.resource_id == '["storage-1","/images/base.qcow2"]'
    assert target.project_id == "p1"
    assert target.node_id == "node-1"


def test_operation_access_rechecks_current_scope_and_all_targets() -> None:
    vm = SimpleNamespace(
        uuid="vm-1",
        owner_project_id="p1",
        owner_user_id=None,
    )

    class MembershipQuery:
        def filter(self, *_: object) -> "MembershipQuery":
            return self

        @staticmethod
        def all() -> list[tuple[str]]:
            return [("p1",)]

    class FakeDB:
        @staticmethod
        def query(*_: object) -> MembershipQuery:
            return MembershipQuery()

        @staticmethod
        def get(model: object, key: object) -> object | None:
            if getattr(model, "__name__", "") == "DomainModel" and key == vm.uuid:
                return vm
            return None

    task = _task(SimpleNamespace(
        uuid="operation-1",
        dependence_uuid=None,
        correlation_id=None,
        method="agent",
        object="vm.network.update",
        principal_id="admin",
        user_id="admin",
        resolved_targets=[
            {"resourceType": "vm", "resourceId": "vm-1", "projectId": "p1", "nodeId": "n1"},
            {"resourceType": "network", "resourceId": "net-1", "projectId": "p1", "nodeId": "n1"},
            {
                "resourceType": "ssh-credentials",
                "resourceId": "global",
                "authorizationTarget": "false",
            },
        ],
    ))
    db = _session(FakeDB())
    authorize_operation_access(
        db,
        context=_context(
            scopes=["vm.network.update"],
            projects=["p1"],
            nodes=["n1"],
        ),
        definition=ACTIONS["vm.network.update"],
        task=task,
    )
    with pytest.raises(AuthorizationError, match="scope"):
        authorize_operation_access(
            db,
            context=_context(scopes=["vm.get"], projects=["p1"], nodes=["n1"]),
            definition=ACTIONS["vm.network.update"],
            task=task,
        )
    assert task.resolved_targets is not None
    task.resolved_targets[1]["projectId"] = "p2"
    with pytest.raises(AuthorizationError, match="project"):
        authorize_operation_access(
            db,
            context=_context(
                scopes=["vm.network.update"],
                projects=["p1"],
                nodes=["n1"],
            ),
            definition=ACTIONS["vm.network.update"],
            task=task,
        )


def test_dispatch_rederives_storage_project_binding_from_database() -> None:
    storage = SimpleNamespace(uuid="storage-1", node_name="node-1")
    node = SimpleNamespace(name="node-1")
    project = SimpleNamespace(
        id="p1",
        storage_pools=[],
        network_pools=[],
        flavors=[],
    )

    class FakeDB:
        @staticmethod
        def get(model: object, key: object) -> object | None:
            name = getattr(model, "__name__", "")
            if name == "StorageModel" and key == "storage-1":
                return storage
            if name == "NodeModel" and key == "node-1":
                return node
            if name == "ProjectModel" and key == "p1":
                return project
            return None

    task = _task(SimpleNamespace(
        uuid="storage-delete",
        dependence_uuid=None,
        correlation_id=None,
        method="agent",
        object="storage.delete",
        user_id="admin",
        principal_id="admin",
        expected_generation="generation",
        resolved_targets=[{
            "resourceType": "storage",
            "resourceId": "storage-1",
            "projectId": "p1",
            "nodeId": "node-1",
            "generationTarget": "true",
        }],
    ))
    db = _session(FakeDB())
    lease = _lease(SimpleNamespace(
        principal_id="admin",
        project_ids=[],
        node_ids=[],
    ))
    with pytest.raises(AuthorizationError, match="project所属"):
        _validate_task_constraints(db, task, lease)

    project.storage_pools = [SimpleNamespace(
        storages=[SimpleNamespace(storage_uuid="storage-1")],
    )]
    _validate_task_constraints(db, task, lease)


def test_reservation_contract_covers_family_refresh_and_ssh_key_exclusion() -> None:
    base = ResolvedTarget("node", "node-1", None, "node-1")
    node_create = _apply_reservation_contract(ACTIONS["node.create"], base)
    values = node_create.task_value()
    family = {
        item["resourceType"]
        for item in values
        if item.get("reservationScope") == "family"
    }
    assert family == {"vm", "storage", "image", "network"}
    assert any(
        item.get("resourceType") == "ssh-credentials"
        and item.get("reservationMode") == "shared"
        for item in values
    )

    key_write = _apply_reservation_contract(ACTIONS["node.ssh-key.write"], base)
    assert any(
        item.get("resourceType") == "ssh-credentials"
        and item.get("reservationMode") == "exclusive"
        and item.get("authorizationTarget") == "false"
        for item in key_write.task_value()
    )

    expected_effects = {
        "vm.refresh": {"vm", "image"},
        "image.refresh": {"storage", "image"},
        "network.refresh": {"network"},
        "vm.create": {"vm", "storage", "image"},
        "storage.create": {"storage", "image"},
        "network.create": {"network"},
    }
    for action_id, expected in expected_effects.items():
        definition = ACTIONS[action_id]
        resolved = _apply_reservation_contract(
            definition,
            ResolvedTarget(definition.resource_type, "target", None, None),
        )
        actual = {
            item["resourceType"]
            for item in resolved.task_value()
            if item.get("reservationScope") == "family"
        }
        assert expected <= actual, action_id


def test_image_mutation_reserves_its_parent_storage_without_global_serialization() -> None:
    image = _apply_reservation_contract(
        ACTIONS["image.delete"],
        ResolvedTarget(
            "image",
            '["storage-1","/images/a.qcow2"]',
            None,
            "node-1",
            related_targets=({
                "resourceType": "storage",
                "resourceId": "storage-1",
                "nodeId": "node-1",
            },),
        ),
    )
    storage_same = _apply_reservation_contract(
        ACTIONS["storage.delete"],
        ResolvedTarget("storage", "storage-1", None, "node-1"),
    )
    storage_other = _apply_reservation_contract(
        ACTIONS["storage.delete"],
        ResolvedTarget("storage", "storage-2", None, "node-1"),
    )

    def exclusive_keys(target: ResolvedTarget) -> set[str]:
        return {
            spec.target_key
            for spec in calculate_target_reservation_specs(target.task_value())
            if spec.lock_mode == "exclusive"
        }

    assert exclusive_keys(image) & exclusive_keys(storage_same)
    assert not (exclusive_keys(image) & exclusive_keys(storage_other))


def test_node_lifecycle_reservation_is_node_scoped_reader_writer() -> None:
    node_delete = _apply_reservation_contract(
        ACTIONS["node.delete"],
        ResolvedTarget("node", "node-1", None, "node-1"),
    )
    vm_update_same_node = _apply_reservation_contract(
        ACTIONS["vm.network.update"],
        ResolvedTarget("vm", "vm-1", None, "node-1"),
    )
    vm_update_other_node = _apply_reservation_contract(
        ACTIONS["vm.network.update"],
        ResolvedTarget("vm", "vm-2", None, "node-2"),
    )

    def lifecycle_key(node_id: str, mode: str) -> str:
        return calculate_target_reservation_specs([{
            "resourceType": "node-lifecycle",
            "resourceId": node_id,
            "reservationScope": "global",
            "reservationMode": mode,
        }])[0].target_key

    node_1_key = lifecycle_key("node-1", "shared")
    node_2_key = lifecycle_key("node-2", "shared")
    assert node_1_key != node_2_key
    delete_specs = {
        spec.target_key: spec.lock_mode
        for spec in calculate_target_reservation_specs(node_delete.task_value())
    }
    same_node_specs = {
        spec.target_key: spec.lock_mode
        for spec in calculate_target_reservation_specs(
            vm_update_same_node.task_value(),
        )
    }
    other_node_specs = {
        spec.target_key: spec.lock_mode
        for spec in calculate_target_reservation_specs(
            vm_update_other_node.task_value(),
        )
    }
    assert delete_specs[node_1_key] == "exclusive"
    assert same_node_specs[node_1_key] == "shared"
    assert other_node_specs[node_2_key] == "shared"
    assert node_2_key not in delete_specs


def test_network_refresh_reserves_every_current_node_lifecycle_shared() -> None:
    nodes = [SimpleNamespace(name="node-1"), SimpleNamespace(name="node-2")]

    class FakeQuery:
        def __init__(self, entity: object) -> None:
            self.entity = entity

        def filter(self, *_: object) -> "FakeQuery":
            return self

        def all(self) -> list[object]:
            entity_class = getattr(self.entity, "class_", self.entity)
            if (
                getattr(entity_class, "__name__", "") == "NodeModel"
                and getattr(self.entity, "key", None) == "name"
            ):
                return cast(list[object], nodes)
            return []

    class FakeDB:
        @staticmethod
        def query(entity: object, *_: object) -> FakeQuery:
            return FakeQuery(entity)

    definition = ACTIONS["network.refresh"]
    resolved = _validate_action_references(
        _session(FakeDB()),
        context=_context(scopes=["network.refresh"]),
        definition=definition,
        model=EmptyInput(),
        target=ResolvedTarget("network", "network.refresh", None, None),
    )
    reserved = _apply_reservation_contract(definition, resolved)
    lifecycle = {
        item["resourceId"]: item["reservationMode"]
        for item in reserved.related_targets
        if item.get("resourceType") == "node-lifecycle"
    }
    assert lifecycle == {"node-1": "shared", "node-2": "shared"}


def test_dependent_inventory_tasks_form_a_strict_sequence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """dependent taskを兄弟化せず直前taskへ連結する。"""

    commits: list[dict[str, object]] = []
    selectors: list[tuple[str, str, str]] = []

    class FakeTaskManager:
        def __init__(self, _: object) -> None:
            self.created = True

        def select(self, method: str, resource: str, object_name: str) -> None:
            selectors.append((method, resource, object_name))

        def commit(self, **kwargs: object) -> object:
            task_uuid = f"task-{len(commits)}"
            commits.append(dict(kwargs))
            return SimpleNamespace(
                uuid=task_uuid,
                lease_id="lease-1",
                correlation_id="operation-1",
            )

    class FakeDB:
        @staticmethod
        def commit() -> None:
            return None

    monkeypatch.setattr(actions, "TaskManager", FakeTaskManager)
    monkeypatch.setattr(actions, "append_audit_event", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        actions,
        "acquire_target_reservations",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(actions, "consume_mutation", lambda context: None)
    monkeypatch.setattr(
        actions,
        "get_operation",
        lambda *args, **kwargs: {
            "operation_id": "task-0",
            "task_ids": [f"task-{index}" for index in range(5)],
            "normalized_status": "queued",
        },
    )

    context = _context(scopes=["node.create"])
    model = SimpleNamespace(name="node-1", libvirt_role=True)
    result = actions._execute_task_action(
        _session(FakeDB()),
        context=context,
        definition=ACTIONS["node.create"],
        request=ActionRequest(
            input={"name": "node-1"},
            target=ActionTarget(resource_type="node", resource_id="node-1"),
            idempotency_key="node-create-1",
            expected_generation="0",
        ),
        model=model,
        target=_apply_reservation_contract(
            ACTIONS["node.create"],
            ResolvedTarget("node", "node-1", None, "node-1"),
        ),
        correlation_id="operation-1",
        agent_request_hash="a" * 64,
    )

    assert result.operation_id == "task-0"
    assert selectors == [
        ("post", "node", "root"),
        ("patch", "node", "role"),
        ("put", "vm", "list"),
        ("put", "storage", "list"),
        ("put", "network", "list"),
    ]
    assert [commit.get("dep_uuid") for commit in commits] == [
        None,
        "task-0",
        "task-1",
        "task-2",
        "task-3",
    ]


def test_direct_mutations_are_registered_only_as_worker_queue_handlers() -> None:
    expected = {
        f"agent.direct.{definition.action_id}"
        for definition in ACTIONS.values()
        if definition.kind == "direct"
    }
    assert expected <= set(worker_task.task_func)


def test_ssh_key_audit_failure_is_unknown_after_external_effect(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    effect = {"completed": False}

    def adapter(*_: object, **__: object) -> dict[str, bool]:
        effect["completed"] = True
        return {"configured": True}

    monkeypatch.setitem(
        agent_tasks.DIRECT_ADAPTERS,
        "node_ssh_key_write",
        adapter,
    )
    monkeypatch.setattr(agent_tasks, "_validate_public_json", lambda *args: None)
    monkeypatch.setattr(
        agent_tasks,
        "_load_input_model",
        lambda *args: SimpleNamespace(),
    )
    monkeypatch.setattr(
        agent_tasks,
        "_resolved_target",
        lambda *args: ResolvedTarget("node", "ssh-credentials", None, None),
    )
    monkeypatch.setattr(
        agent_tasks,
        "_worker_context",
        lambda *args: _context(scopes=["node.ssh-key.write"]),
    )
    monkeypatch.setattr(
        agent_tasks,
        "_validate_identity_admin_scope",
        lambda *args: None,
    )
    monkeypatch.setattr(
        agent_tasks,
        "append_audit_event",
        lambda *args, **kwargs: (_ for _ in ()).throw(AuditWriteError()),
    )
    task = _task(SimpleNamespace(
        object="node.ssh-key.write",
        uuid="ssh-key-operation",
        correlation_id="ssh-key-correlation",
        result=None,
        message=None,
    ))
    with pytest.raises(AuditWriteError) as caught:
        agent_tasks.execute_direct_action(
            _session(SimpleNamespace()),
            task,
            TaskRequest(path_param={}, body={}),
        )
    assert effect["completed"] is True
    assert caught.value.outcome_unknown is True


def test_catalog_task_selectors_have_explicit_worker_handlers() -> None:
    from domain.tasks import worker_task as domain_tasks
    from images.tasks import worker_task as image_tasks
    from network.tasks import worker_task as network_tasks
    from node.tasks import worker_task as node_tasks
    from project.tasks import worker_task as project_tasks
    from storage.tasks import worker_task as storage_tasks

    registered: set[str] = set()
    for task_base in (
        domain_tasks,
        image_tasks,
        network_tasks,
        node_tasks,
        project_tasks,
        storage_tasks,
    ):
        registered.update(task_base.task_func)
    expected = {
        ".".join(definition.task_selector)
        for definition in ACTIONS.values()
        if definition.kind == "task" and definition.task_selector is not None
    }
    assert expected <= registered


def test_pool_list_read_adapters_return_object_contract(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(adapters, "resolve_generation", lambda *args, **kwargs: "gen")
    monkeypatch.setattr(
        adapters,
        "_allowed_storage_ids",
        lambda *args, **kwargs: {"storage-1"},
    )
    monkeypatch.setattr(
        adapters,
        "_allowed_storage_pool_ids",
        lambda *args, **kwargs: {1},
    )
    monkeypatch.setattr(
        adapters,
        "_allowed_network_ids",
        lambda *args, **kwargs: {"network-1"},
    )
    monkeypatch.setattr(
        adapters,
        "_allowed_network_pool_ids",
        lambda *args, **kwargs: {2},
    )
    storage_pool = SimpleNamespace(
        id=1,
        name="storage-pool",
        storages=[
            SimpleNamespace(storage_uuid="storage-1"),
            SimpleNamespace(storage_uuid="storage-hidden"),
        ],
    )
    network = SimpleNamespace(uuid="network-1")
    hidden_network = SimpleNamespace(uuid="network-hidden")
    network_pool = SimpleNamespace(
        id=2,
        name="network-pool",
        networks=[network, hidden_network],
        ports=[
            SimpleNamespace(
                network_uuid="network-1",
                network=network,
                name="allowed-port",
            ),
            SimpleNamespace(
                network_uuid="network-hidden",
                network=hidden_network,
                name="hidden-port",
            ),
        ],
    )

    class FakeQuery:
        def __init__(self, rows: list[object]) -> None:
            self.rows = rows

        def order_by(self, *_: object) -> "FakeQuery":
            return self

        def filter(self, *_: object) -> "FakeQuery":
            return self

        def all(self) -> list[object]:
            return self.rows

    class FakeDB:
        @staticmethod
        def query(model: object, *_: object) -> FakeQuery:
            name = getattr(model, "__name__", "")
            return FakeQuery(
                [storage_pool] if name == "StoragePoolModel" else [network_pool],
            )

    context = _context(
        scopes=["storage.pool.list", "network.pool.list"],
        nodes=["node-1"],
    )
    db = _session(FakeDB())
    storage_result = adapters.storage_pool_list(db, context, None, None)
    network_result = adapters.network_pool_list(db, context, None, None)
    assert storage_result == {
        "count": 1,
        "data": [{
            "id": 1,
            "name": "storage-pool",
            "storageUuids": ["storage-1"],
            "generation": "gen",
        }],
    }
    assert network_result["count"] == 1
    assert network_result["data"][0]["networkUuids"] == ["network-1"]
    assert network_result["data"][0]["ports"] == [{
        "networkUuid": "network-1",
        "name": "allowed-port",
    }]


def test_task_incomplete_keeps_unknown_and_cancel_requested(
    tmp_path: Path,
) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'incomplete.sqlite'}")
    UserModel.__table__.create(engine)
    TaskModel.__table__.create(engine)
    with Session(engine) as db:
        db.add(UserModel(username="admin", hashed_password="unused"))
        db.add_all([
            TaskModel(
                uuid=f"task-{status}",
                principal_id="admin",
                status=status,
            )
            for status in ("wait", "unknown", "cancel_requested", "finish")
        ])
        db.add(TaskModel(
            uuid="task-archived-unknown",
            principal_id="admin",
            status="unknown",
            archived_at=datetime.now(UTC),
        ))
        db.add(TaskModel(
            uuid="task-other-principal",
            principal_id="other-admin",
            user_id="admin",
            status="wait",
        ))
        db.commit()

        result = adapters.task_incomplete(
            db,
            _context(scopes=["task.incomplete"]),
            SimpleNamespace(admin=False),
            None,
        )

    assert result["count"] == 3
    assert result["uuids"] == [
        "task-cancel_requested",
        "task-unknown",
        "task-wait",
    ]


def test_task_detail_never_uses_global_admin_as_an_ownership_bypass() -> None:
    task = SimpleNamespace(
        uuid="task-other",
        principal_id="other-admin",
        user_id="admin",
    )
    db = _session(SimpleNamespace(get=lambda *_: task))
    with pytest.raises(AuthorizationError, match="別principal"):
        adapters.task_get(
            db,
            _context(scopes=["task.get"]),
            None,
            SimpleNamespace(resource_id=task.uuid),
        )


def test_reconciliation_list_returns_root_operation_and_openapi_schema(
    tmp_path: Path,
) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'reconciliation.sqlite'}")
    UserModel.__table__.create(engine)
    TaskModel.__table__.create(engine)
    now = datetime.now(UTC)
    with Session(engine) as db:
        db.add_all([
            TaskModel(
                uuid="root-task",
                post_time=now,
                update_time=now,
                principal_id="admin",
                lease_id="lease-1",
                correlation_id="correlation-not-root-id",
                status="finish",
                method="post",
                resource="node",
                object="root",
            ),
            TaskModel(
                uuid="dependent-task",
                post_time=now + timedelta(seconds=1),
                update_time=now + timedelta(seconds=1),
                principal_id="admin",
                lease_id="lease-1",
                correlation_id="correlation-not-root-id",
                dependence_uuid="root-task",
                status="unknown",
                method="put",
                resource="vm",
                object="list",
            ),
        ])
        db.commit()

        current_user = _typed(CurrentUser, SimpleNamespace(id="admin"))
        result = list_operation_reconciliations(current_user, db)

    assert len(result) == 1
    assert result[0].operation_id == "root-task"
    assert result[0].task_ids == ["root-task", "dependent-task"]
    assert result[0].action == "node.create"
    assert result[0].status == "unknown"

    application = FastAPI()
    application.include_router(agent_router)
    response_schema = application.openapi()["paths"][
        "/api/agent/v1/operation-reconciliations"
    ]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
    assert response_schema["type"] == "array"
    assert response_schema["items"] == {
        "$ref": "#/components/schemas/OperationResponse",
    }


def test_manual_reconciliation_preserves_or_releases_operation_reservation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'manual-reconcile.sqlite'}")
    UserModel.__table__.create(engine)
    TaskModel.__table__.create(engine)
    TaskTargetReservationModel.__table__.create(engine)
    AuditEventModel.__table__.create(engine)
    now = datetime.now(UTC)

    def add_operation(
        db: Session,
        prefix: str,
        *,
        include_cancel_requested: bool,
    ) -> None:
        root = TaskModel(
            uuid=f"{prefix}-root",
            post_time=now,
            update_time=now,
            principal_id="admin",
            lease_id="lease-1",
            correlation_id=f"{prefix}-correlation",
            status="unknown",
            method="post",
            resource="node",
            object="root",
        )
        db.add(root)
        db.flush()
        rows: list[object] = [
            TaskModel(
                uuid=f"{prefix}-wait",
                post_time=now + timedelta(seconds=1),
                update_time=now + timedelta(seconds=1),
                principal_id="admin",
                lease_id="lease-1",
                correlation_id=f"{prefix}-correlation",
                dependence_uuid=root.uuid,
                status="wait",
                method="put",
                resource="vm",
                object="list",
            ),
            TaskTargetReservationModel(
                reservation_id=(prefix[0] * 64),
                target_key=(prefix[-1] * 64),
                lock_mode="exclusive",
                correlation_id=f"{prefix}-correlation",
                lease_id="lease-1",
                acquired_at=now,
            ),
        ]
        if include_cancel_requested:
            rows.append(TaskModel(
                uuid=f"{prefix}-cancel-requested",
                post_time=now + timedelta(seconds=2),
                update_time=now + timedelta(seconds=2),
                principal_id="admin",
                lease_id="lease-1",
                correlation_id=f"{prefix}-correlation",
                dependence_uuid=f"{prefix}-wait",
                status="cancel_requested",
                method="put",
                resource="storage",
                object="list",
            ))
        db.add_all(rows)

    with Session(engine) as db:
        add_operation(db, "confirmed", include_cancel_requested=False)
        add_operation(db, "absent", include_cancel_requested=True)
        db.commit()
        service = AgentManagementService()
        monkeypatch.setattr(service, "_verify", lambda *args, **kwargs: None)

        confirmed = service.reconcile_operation(
            db,
            admin_id="admin",
            operation_id="confirmed-root",
            resolution="effect_confirmed",
            reason="実機で作成済みを確認",
            challenge_id="challenge",
            credential={},
        )
        db.commit()
        assert confirmed["normalized_status"] == "queued"
        confirmed_root = db.get(TaskModel, "confirmed-root")
        confirmed_wait = db.get(TaskModel, "confirmed-wait")
        assert confirmed_root is not None
        assert confirmed_wait is not None
        assert confirmed_root.status == "finish"
        assert confirmed_wait.status == "wait"
        assert (
            db.query(TaskTargetReservationModel).filter(
                TaskTargetReservationModel.correlation_id
                == "confirmed-correlation",
            ).count()
            == 1
        )

        absent = service.reconcile_operation(
            db,
            admin_id="admin",
            operation_id="absent-root",
            resolution="effect_absent",
            reason="実機に効果なしを確認",
            challenge_id="challenge",
            credential={},
        )
        db.commit()
        assert absent["normalized_status"] == "failed"
        absent_root = db.get(TaskModel, "absent-root")
        absent_wait = db.get(TaskModel, "absent-wait")
        absent_cancel_requested = db.get(TaskModel, "absent-cancel-requested")
        assert absent_root is not None
        assert absent_wait is not None
        assert absent_cancel_requested is not None
        assert absent_root.status == "error"
        assert absent_wait.status == "cancelled"
        assert absent_cancel_requested.status == "cancelled"
        assert (
            db.query(TaskTargetReservationModel).filter(
                TaskTargetReservationModel.correlation_id
                == "absent-correlation",
            ).count()
            == 0
        )


def test_admin_credential_grant_requires_dedicated_identity_scope() -> None:
    class EmptyQuery:
        def filter(self, *args: object) -> "EmptyQuery":
            return self

        @staticmethod
        def first() -> None:
            return None

    db = _session(SimpleNamespace(query=lambda _: EmptyQuery()))
    model = SimpleNamespace(
        username="new-admin",
        scopes=[SimpleNamespace(name="admin")],
    )
    with pytest.raises(AuthorizationError, match="identity.admin"):
        _validate_identity_admin_scope(
            db,
            _context(scopes=["user.create"]),
            ACTIONS["user.create"],
            model,
        )
    _validate_identity_admin_scope(
        db,
        _context(scopes=["user.create", "identity.admin"]),
        ACTIONS["user.create"],
        model,
    )


@pytest.mark.parametrize(
    "action_id",
    [
        "project.create",
        "project.delete",
        "project.resource-grant-candidates.get",
        "project.resource-grants.update",
        "storage.pool.create",
        "storage.pool.update",
        "storage.pool.delete",
        "storage.create",
        "storage.delete",
        "image.delete",
        "network.pool.create",
        "network.pool.update",
        "network.pool.delete",
        "network.create",
        "network.delete",
        "network.ovs.create",
        "network.ovs.delete",
        "flavor.delete",
    ],
)
def test_agent_global_project_and_pool_operations_require_database_admin(
    action_id: str,
) -> None:
    class AdminQuery:
        def __init__(self, is_admin: bool) -> None:
            self.is_admin = is_admin

        def filter(self, *args: object) -> "AdminQuery":
            return self

        def first(self) -> object | None:
            return object() if self.is_admin else None

    non_admin_db = _session(SimpleNamespace(query=lambda _: AdminQuery(False)))
    with pytest.raises(AuthorizationError, match="global admin"):
        _validate_identity_admin_scope(
            non_admin_db,
            _context(scopes=[action_id]),
            ACTIONS[action_id],
            SimpleNamespace(),
        )

    admin_db = _session(SimpleNamespace(query=lambda _: AdminQuery(True)))
    _validate_identity_admin_scope(
        admin_db,
        _context(scopes=[action_id]),
        ACTIONS[action_id],
        SimpleNamespace(),
    )


@pytest.mark.parametrize(
    ("action_id", "guard_name", "params"),
    [
        ("storage.delete", "ensure_storage_deletable", {"uuid": "storage-a"}),
        (
            "image.delete",
            "ensure_image_deletable",
            {"uuid": "storage-a", "name": "image-a.qcow2"},
        ),
        ("network.delete", "ensure_network_deletable", {"uuid": "network-a"}),
        (
            "network.ovs.delete",
            "ensure_network_port_deletable",
            {"uuid": "network-a", "name": "tenant-a"},
        ),
    ],
)
def test_agent_destructive_task_preflight_maps_resource_conflicts(
    monkeypatch: pytest.MonkeyPatch,
    action_id: str,
    guard_name: str,
    params: dict[str, str],
) -> None:
    def deny(*_args: object, **_kwargs: object) -> None:
        raise actions.ResourceDeletionConflictError("resource is in use")

    monkeypatch.setattr(actions, guard_name, deny)
    with pytest.raises(ConflictError, match="resource is in use"):
        _preflight_task_action(
            _session(SimpleNamespace()),
            action_id,
            SimpleNamespace(),
            params,
        )


def test_agent_project_delete_preflight_locks_and_rechecks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, bool]] = []

    def ensure_project(
        _db: Session,
        project_id: str,
        *,
        lock: bool = False,
    ) -> None:
        calls.append((project_id, lock))

    monkeypatch.setattr(actions, "ensure_project_deletable", ensure_project)
    _preflight_task_action(
        _session(SimpleNamespace()),
        "project.delete",
        SimpleNamespace(project_id="aaaaaa"),
        {"project_id": "aaaaaa"},
    )
    assert calls == [("aaaaaa", True)]


def test_agent_project_lease_is_limited_to_admin_memberships() -> None:
    principal = SimpleNamespace(
        scopes=[SimpleNamespace(name="admin")],
        projects=[SimpleNamespace(id="aaaaaa")],
    )

    class FakeDB:
        @staticmethod
        def get(model: object, key: object) -> object | None:
            if getattr(model, "__name__", "") == "UserModel" and key == "admin":
                return principal
            return None

    db = _session(FakeDB())
    AgentIdentityService._validate_project_constraints(
        db,
        principal_id="admin",
        requested_projects=["aaaaaa"],
    )
    with pytest.raises(AuthorizationError, match="所属範囲"):
        AgentIdentityService._validate_project_constraints(
            db,
            principal_id="admin",
            requested_projects=["bbbbbb"],
        )
