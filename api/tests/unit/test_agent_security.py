"""Agent API境界・能力lease・queue契約の副作用なし回帰test。"""

import json
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from typing import TypeVar, cast

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from auth.router import CurrentUser
from agent.actions import (
    _apply_reservation_contract,
    _validate_action_references,
    _validate_identity_admin_scope,
    _validate_public_json,
    _validate_resolved_constraints,
    public_input_schema,
    resolve_action_target,
)
from agent.adapters import ResolvedTarget
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
    validate_worker_dispatch,
)
from agent.schemas import (
    ActionRequest,
    ActionTarget,
    LeaseRequest,
    PairingApproveRequest,
    PairingCreateRequest,
)
from agent.router import AgentAPIRoute, app as agent_router, list_operation_reconciliations
from agent.service import AgentManagementService
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
    assert len(ACTIONS) == 63

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
    assert ACTIONS["user.create"].risk == "R3"
    assert ACTIONS["user.create"].destructive is True
    assert ACTIONS["user.update"].risk == "R3"
    assert ACTIONS["node.create"].network_change is True
    assert ACTIONS["vm.create"].network_change is True


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
    assert response.json()["detail"]["code"] == "validation_error"
    assert secret not in response.text
    assert "input" not in response.text


def test_vm_create_requires_owner_project_in_public_input() -> None:
    payload = {
        "type": "manual",
        "name": "agent-vm",
        "nodeName": "node-1",
        "projectId": "p1",
        "memoryMegaByte": 1024,
        "cpu": 1,
        "disks": [],
        "interface": [],
    }
    _validate_public_json("vm.create", payload)
    model = actions._load_input_model(ACTIONS["vm.create"], payload)
    assert model.project_id == "p1"
    with pytest.raises(AgentError, match="input"):
        _validate_public_json(
            "vm.create",
            {key: value for key, value in payload.items() if key != "projectId"},
        )


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
        @staticmethod
        def filter(*_: object) -> "RootQuery":
            return RootQuery()

        @staticmethod
        def order_by(*_: object) -> "RootQuery":
            return RootQuery()

        @staticmethod
        def all() -> list[object]:
            return [root]

    class FakeDB:
        @staticmethod
        def query(*_: object) -> RootQuery:
            return RootQuery()

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
    lease = _lease(SimpleNamespace(project_ids=["p1"], node_ids=["node-1"]))
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
    project = SimpleNamespace(
        id="p1",
        storage_pools=[],
        network_pools=[],
        flavors=[],
    )
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
            return None

    model = SimpleNamespace(
        project_id="p1",
        node_name="node-1",
        disks=[],
        interface=[],
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
                "storageUuid": "storage-1",
                "path": "/images/base.qcow2",
                "nodeName": "node-1",
                "flavorId": 1,
            },
            target=ActionTarget(
                resource_type="image",
                resource_id="/images/base.qcow2",
                node_id="node-1",
            ),
            expected_generation="generation",
            idempotency_key="idempotency-1",
        ),
        model=SimpleNamespace(
            storage_uuid="storage-1",
            path="/images/base.qcow2",
        ),
    )
    assert target.resource_id == '["storage-1","/images/base.qcow2"]'
    assert target.project_id == "p1"
    assert target.node_id == "node-1"


def test_operation_access_rechecks_current_scope_and_all_targets() -> None:
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
    authorize_operation_access(
        _session(SimpleNamespace()),
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
            _session(SimpleNamespace()),
            context=_context(scopes=["vm.get"], projects=["p1"], nodes=["n1"]),
            definition=ACTIONS["vm.network.update"],
            task=task,
        )
    assert task.resolved_targets is not None
    task.resolved_targets[1]["projectId"] = "p2"
    with pytest.raises(AuthorizationError, match="project"):
        authorize_operation_access(
            _session(SimpleNamespace()),
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
    lease = _lease(SimpleNamespace(project_ids=["p1"], node_ids=["node-1"]))
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


def test_network_provider_requires_every_server_resolved_overlay_node() -> None:
    network_node = SimpleNamespace(name="network-node", roles=[])
    worker_a = SimpleNamespace(
        name="worker-a",
        roles=[SimpleNamespace(role_name="vxlan_overlay")],
    )
    worker_b = SimpleNamespace(
        name="worker-b",
        roles=[SimpleNamespace(role_name="vxlan_overlay")],
    )
    nodes = [network_node, worker_a, worker_b]

    class FakeQuery:
        def __init__(self, entity: object) -> None:
            self.entity = entity

        def filter(self, *_: object) -> "FakeQuery":
            return self

        def order_by(self, *_: object) -> "FakeQuery":
            return self

        def all(self) -> list[object]:
            entity_class = getattr(self.entity, "class_", self.entity)
            entity_name = getattr(entity_class, "__name__", "")
            attribute_name = getattr(self.entity, "key", None)
            if entity_name == "NodeModel" and attribute_name == "name":
                return [SimpleNamespace(name=node.name) for node in nodes]
            if entity_name == "NodeModel":
                return cast(list[object], nodes)
            return []

        def __iter__(self):
            return iter(self.all())

    class FakeDB:
        @staticmethod
        def get(model: object, key: object) -> object | None:
            if getattr(model, "__name__", "") == "NodeModel":
                return next((node for node in nodes if node.name == key), None)
            return None

        @staticmethod
        def query(entity: object, *_: object) -> FakeQuery:
            return FakeQuery(entity)

    definition = ACTIONS["network.provider.create"]
    model = SimpleNamespace(network_node="network-node")
    base_target = ResolvedTarget(
        "network",
        "network.provider.create",
        None,
        "network-node",
    )
    denied_context = _context(
        scopes=["network.provider.create"],
        nodes=["network-node", "worker-a"],
    )
    db = _session(FakeDB())
    denied_target = _validate_action_references(
        db,
        context=denied_context,
        definition=definition,
        model=model,
        target=base_target,
    )
    with pytest.raises(AuthorizationError, match="node"):
        _validate_resolved_constraints(denied_context, denied_target)

    allowed_context = _context(
        scopes=["network.provider.create"],
        nodes=[node.name for node in nodes],
    )
    allowed_target = _validate_action_references(
        db,
        context=allowed_context,
        definition=definition,
        model=model,
        target=base_target,
    )
    _validate_resolved_constraints(allowed_context, allowed_target)
    authorization_nodes = {
        item["nodeId"]
        for item in allowed_target.related_targets
        if item.get("resourceType") == "node"
    }
    assert authorization_nodes == {node.name for node in nodes}

    reserved = _apply_reservation_contract(definition, allowed_target)
    lifecycle_nodes = {
        item["resourceId"]
        for item in reserved.related_targets
        if item.get("resourceType") == "node-lifecycle"
    }
    assert lifecycle_nodes == {node.name for node in nodes}
    assert any(
        item.get("resourceType") == "network"
        and item.get("reservationScope") == "family"
        and item.get("reservationMode") == "exclusive"
        for item in reserved.related_targets
    )


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
        "_allowed_network_ids",
        lambda *args, **kwargs: {"network-1"},
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
