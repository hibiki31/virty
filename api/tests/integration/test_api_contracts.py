import time
from datetime import timedelta
from typing import cast
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.routing import iter_route_contexts
from fastapi.testclient import TestClient

from auth.router import create_access_token, get_current_user
from domain.models import DomainModel
from mixin.database import SessionLocal
from mixin.exception import ApiErrorCode, FieldErrorCode
from node.models import NodeModel
from project.models import ProjectModel
from task.models import TaskModel
from user.models import UserModel, UserScopeModel


pytestmark = [pytest.mark.integration, pytest.mark.timeout(60)]

REQUIRED_BODY_OPERATIONS = [
    ("post", "/api/tasks/vms", "/api/tasks/vms"),
    ("patch", "/api/tasks/vms/missing/power", "/api/tasks/vms/{uuid}/power"),
    ("patch", "/api/tasks/vms/missing/network", "/api/tasks/vms/{uuid}/network"),
    ("post", "/api/tasks/networks", "/api/tasks/networks"),
    ("post", "/api/tasks/networks/missing/ovs", "/api/tasks/networks/{uuid}/ovs"),
    ("post", "/api/tasks/networks/providers", "/api/tasks/networks/providers"),
    ("post", "/api/tasks/nodes", "/api/tasks/nodes"),
    ("post", "/api/tasks/storages", "/api/tasks/storages"),
    ("patch", "/api/storages", "/api/storages"),
]


def _headers(
    username: str,
    scopes: list[str] | None = None,
    projects: list[str] | None = None,
) -> dict[str, str]:
    token = create_access_token(
        data={
            "sub": username,
            "scopes": scopes if scopes is not None else ["admin"],
            "projects": projects if projects is not None else [],
        },
        expires_delta=timedelta(hours=1),
    )
    return {"Authorization": f"Bearer {token}"}


def _wait_for_terminal_task(task_uuid: str, timeout_seconds: float = 10) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        with SessionLocal() as db:
            task = db.query(TaskModel).filter(TaskModel.uuid == task_uuid).one()
            if task.status in {"finish", "error", "lost"}:
                return
        time.sleep(0.1)
    pytest.fail(f"task {task_uuid} が{timeout_seconds:.0f}秒以内に完了しませんでした")


@pytest.mark.parametrize(("method", "request_path", "schema_path"), REQUIRED_BODY_OPERATIONS)
def test_mutation_request_bodies_are_required(
    api_client: TestClient,
    method: str,
    request_path: str,
    schema_path: str,
) -> None:
    username = f"body-contract-{uuid4().hex}"
    try:
        with SessionLocal.begin() as db:
            db.add(UserModel(username=username, hashed_password="unused"))
            db.add(UserScopeModel(user_id=username, name="admin"))

        response = api_client.request(
            method.upper(),
            request_path,
            headers=_headers(username),
        )
        assert response.status_code == 422, response.text

        operation = api_client.get("/api/openapi.json").json()["paths"][schema_path][method]
        assert operation["requestBody"]["required"] is True
    finally:
        with SessionLocal.begin() as db:
            db.query(UserModel).filter(UserModel.username == username).delete()


def test_openapi_operation_ids_remain_route_names(api_client: TestClient) -> None:
    schema = api_client.get("/api/openapi.json").json()
    application = cast(FastAPI, api_client.app)
    operation_ids = [
        operation["operationId"]
        for path_item in schema["paths"].values()
        for operation in path_item.values()
        if isinstance(operation, dict) and "operationId" in operation
    ]
    route_names = {
        route.name
        for route in iter_route_contexts(application.routes)
        if route.include_in_schema
    }

    assert len(operation_ids) == len(set(operation_ids))
    assert set(operation_ids) == route_names


def test_openapi_publishes_common_error_contract(api_client: TestClient) -> None:
    schema = api_client.get("/api/openapi.json").json()
    schemas = schema["components"]["schemas"]

    api_codes = set(schemas["ApiErrorCode"]["enum"])
    field_codes = set(schemas["FieldErrorCode"]["enum"])
    assert api_codes == {code.value for code in ApiErrorCode}
    assert field_codes == {code.value for code in FieldErrorCode}
    assert "HTTPValidationError" not in schemas
    assert "ValidationError" not in schemas

    detail_schema = schemas["ApiErrorDetail"]
    field_schema = schemas["ApiFieldError"]
    assert "params" not in detail_schema.get("required", [])
    assert "errors" not in detail_schema.get("required", [])
    assert detail_schema["properties"]["params"]["type"] == "object"
    assert detail_schema["properties"]["errors"]["type"] == "array"
    assert "params" not in field_schema.get("required", [])
    assert field_schema["properties"]["params"]["type"] == "object"

    responses = schema["paths"]["/api/auth"]["post"]["responses"]
    for status_code in ("default", "422"):
        response_schema = responses[status_code]["content"]["application/json"][
            "schema"
        ]
        assert response_schema == {
            "$ref": "#/components/schemas/ApiErrorResponse"
        }

    metrics_responses = schema["paths"]["/api/metrics"]["get"]["responses"]
    for status_code in ("default", "422"):
        content = metrics_responses[status_code]["content"]
        assert set(content) == {"application/json"}
        assert content["application/json"][
            "schema"
        ] == {"$ref": "#/components/schemas/ApiErrorResponse"}


def test_runtime_errors_use_common_safe_envelope(api_client: TestClient) -> None:
    unauthenticated = api_client.get("/api/tasks")
    assert unauthenticated.status_code == 401
    assert unauthenticated.json() == {
        "detail": {
            "code": "authentication_required",
            "message": "Authentication is required.",
        }
    }
    assert unauthenticated.headers["www-authenticate"] == "Bearer"

    missing_route = api_client.get("/api/route-that-does-not-exist")
    assert missing_route.status_code == 404
    assert missing_route.json() == {
        "detail": {
            "code": "resource_not_found",
            "message": "The requested resource was not found.",
        }
    }

    invalid_credentials = api_client.post(
        "/api/auth",
        data={"username": "missing-user", "password": "wrong-password"},
    )
    assert invalid_credentials.status_code == 401
    assert invalid_credentials.json() == {
        "detail": {
            "code": "invalid_credentials",
            "message": "The username or password is incorrect.",
        }
    }

    missing_form_field = api_client.post(
        "/api/auth",
        data={"username": "missing-password"},
    )
    assert missing_form_field.status_code == 422
    assert missing_form_field.json() == {
        "detail": {
            "code": "validation_error",
            "message": "Request validation failed.",
            "errors": [
                {"field": "body.password", "code": "required"},
            ],
        }
    }

    secret = "scope.DoNotReturnThisSecret"
    invalid_body = api_client.post(
        "/api/agent/v1/pairings",
        json={
            "deviceName": "",
            "publicKeyJwk": {
                "kty": "EC",
                "crv": "P-256",
                "x": "A" * 43,
                "y": "A" * 43,
            },
            "requestedScopes": [secret, secret],
        },
    )
    assert invalid_body.status_code == 422
    assert invalid_body.json()["detail"] == {
        "code": "validation_error",
        "message": "Request validation failed.",
        "errors": [
            {
                "field": "body.deviceName",
                "code": "too_short",
                "params": {"minimum": 1},
            },
            {"field": "body.requestedScopes", "code": "invalid_value"},
        ],
    }
    assert secret not in invalid_body.text
    assert "input" not in invalid_body.text
    assert "ctx" not in invalid_body.text
    assert invalid_body.headers["cache-control"] == "no-store"

    missing_pairing = api_client.get(
        "/api/agent/v1/pairings/missing-pairing",
        headers={"X-Pairing-Code": "not-a-secret-code"},
    )
    assert missing_pairing.status_code == 404
    assert missing_pairing.json() == {
        "detail": {
            "code": "pairing_not_found",
            "message": "The requested resource was not found.",
        }
    }
    assert missing_pairing.headers["cache-control"] == "no-store"


def test_rejected_agent_cors_preflight_uses_common_safe_envelope(
    api_client: TestClient,
) -> None:
    response = api_client.options(
        "/api/agent/v1/devices",
        headers={
            "Origin": "https://cors-contract.invalid",
            # allow_methods=["*"]が展開する標準method外を指定して必ず拒否させる。
            "Access-Control-Request-Method": "BREW",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": {
            "code": "bad_request",
            "message": "The CORS preflight request was rejected.",
        }
    }
    assert response.headers["content-type"] == "application/json"
    assert response.headers["cache-control"] == "no-store"


def test_unexpected_runtime_error_uses_safe_common_envelope(
    api_client: TestClient,
) -> None:
    application = cast(FastAPI, api_client.app)
    secret = "DoNotReturnThisInternalFailure"

    def fail_authentication() -> None:
        raise RuntimeError(secret)

    application.dependency_overrides[get_current_user] = fail_authentication
    client = TestClient(application, raise_server_exceptions=False)
    try:
        response = client.get("/api/tasks")
    finally:
        client.close()
        application.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 500
    assert response.json() == {
        "detail": {
            "code": "internal_server_error",
            "message": "An internal server error occurred.",
        }
    }
    assert secret not in response.text


def test_forbidden_and_conflict_use_common_runtime_contract(
    api_client: TestClient,
) -> None:
    suffix = uuid4().hex
    limited_username = f"error-contract-limited-{suffix}"
    admin_username = f"error-contract-admin-{suffix}"
    usernames = [limited_username, admin_username]

    try:
        with SessionLocal.begin() as db:
            db.add_all([
                UserModel(username=limited_username, hashed_password="unused"),
                UserModel(username=admin_username, hashed_password="unused"),
            ])
            db.add_all([
                UserScopeModel(user_id=limited_username, name="vm.read"),
                UserScopeModel(user_id=admin_username, name="admin"),
            ])

        forbidden = api_client.get(
            "/api/dashboard",
            headers=_headers(limited_username, scopes=["vm.read"]),
        )
        assert forbidden.status_code == 403
        assert forbidden.json() == {
            "detail": {
                "code": "scope_denied",
                "message": "The required permission is missing.",
            }
        }

        conflict = api_client.delete(
            f"/api/users/{admin_username}",
            headers=_headers(admin_username),
        )
        assert conflict.status_code == 409
        assert conflict.json() == {
            "detail": {
                "code": "self_delete_denied",
                "message": "The current administrator cannot delete its own account.",
            }
        }
    finally:
        with SessionLocal.begin() as db:
            db.query(UserScopeModel).filter(
                UserScopeModel.user_id.in_(usernames),
            ).delete(synchronize_session=False)
            db.query(UserModel).filter(UserModel.username.in_(usernames)).delete(
                synchronize_session=False,
            )


def test_prometheus_uses_templated_route_name(api_client: TestClient) -> None:
    username = f"metrics-contract-{uuid4().hex}"
    try:
        with SessionLocal.begin() as db:
            db.add(UserModel(username=username, hashed_password="unused"))
            db.add(UserScopeModel(user_id=username, name="metrics.read"))

        response = api_client.get("/api/version")
        assert response.status_code == 200, response.text

        unauthenticated = api_client.get("/api/metrics-fastapi")
        assert unauthenticated.status_code == 401

        metrics = api_client.get(
            "/api/metrics-fastapi",
            headers=_headers(username, ["metrics.read"]),
        )
        assert metrics.status_code == 200, metrics.text
        assert 'handler="/api/version"' in metrics.text
    finally:
        with SessionLocal.begin() as db:
            db.query(UserModel).filter(UserModel.username == username).delete()


def test_node_role_returns_one_task_and_storage_reload_depends_on_create(
    api_client: TestClient,
) -> None:
    suffix = uuid4().hex
    username = f"task-contract-{suffix}"
    task_uuids: list[str] = []

    try:
        with SessionLocal.begin() as db:
            db.add(UserModel(username=username, hashed_password="unused"))
            db.add(UserScopeModel(user_id=username, name="admin"))

        role_response = api_client.patch(
            "/api/tasks/nodes/roles",
            headers=_headers(username),
            json={"nodeName": f"missing-node-{suffix}", "roleName": "libvirt"},
        )
        assert role_response.status_code == 200, role_response.text
        role_task = role_response.json()
        assert isinstance(role_task, dict)
        assert role_task["resource"] == "node"
        assert role_task["object"] == "role"
        task_uuids.append(role_task["uuid"])

        storage_response = api_client.post(
            "/api/tasks/storages",
            headers=_headers(username),
            json={
                "name": f"storage-{suffix}",
                "nodeName": f"missing-node-{suffix}",
                "path": f"/tmp/storage-{suffix}",
            },
        )
        assert storage_response.status_code == 200, storage_response.text
        storage_tasks = storage_response.json()
        assert len(storage_tasks) == 2
        assert storage_tasks[1]["dependenceUuid"] == storage_tasks[0]["uuid"]
        task_uuids.extend(task["uuid"] for task in storage_tasks)

        for task_uuid in task_uuids:
            _wait_for_terminal_task(task_uuid)
    finally:
        with SessionLocal.begin() as db:
            db.query(TaskModel).filter(TaskModel.uuid.in_(task_uuids)).delete(
                synchronize_session=False
            )
            db.query(UserModel).filter(UserModel.username == username).delete()


def test_network_create_accepts_isolated_and_rejects_obsolete_typo(
    api_client: TestClient,
) -> None:
    suffix = uuid4().hex
    username = f"network-contract-{suffix}"
    task_uuids: list[str] = []
    payload = {
        "name": f"isolated-network-{suffix}",
        "nodeName": f"missing-node-{suffix}",
        "forwardMode": "isolated",
    }

    try:
        with SessionLocal.begin() as db:
            db.add(UserModel(username=username, hashed_password="unused"))
            db.add(UserScopeModel(user_id=username, name="admin"))

        valid_response = api_client.post(
            "/api/tasks/networks",
            headers=_headers(username),
            json=payload,
        )
        assert valid_response.status_code == 200, valid_response.text
        task_uuids = [task["uuid"] for task in valid_response.json()]

        invalid_response = api_client.post(
            "/api/tasks/networks",
            headers=_headers(username),
            json={**payload, "forwardMode": "isorated"},
        )
        assert invalid_response.status_code == 422

        schema = api_client.get("/api/openapi.json").json()
        allowed_modes = schema["components"]["schemas"]["NetworkForCreate"][
            "properties"
        ]["forwardMode"]["enum"]
        assert "isolated" in allowed_modes
        assert "isorated" not in allowed_modes

        for task_uuid in task_uuids:
            _wait_for_terminal_task(task_uuid)
    finally:
        with SessionLocal.begin() as db:
            db.query(TaskModel).filter(TaskModel.uuid.in_(task_uuids)).delete(
                synchronize_session=False
            )
            db.query(UserModel).filter(UserModel.username == username).delete()


def test_vm_project_update_uses_path_uuid(api_client: TestClient) -> None:
    suffix = uuid4().hex
    username = f"vm-project-user-{suffix}"
    node_name = f"vm-project-node-{suffix}"
    target_uuid = str(uuid4())
    other_uuid = str(uuid4())
    project_id = suffix[:6]

    try:
        with SessionLocal.begin() as db:
            db.add(UserModel(username=username, hashed_password="unused"))
            db.add(UserScopeModel(user_id=username, name="admin"))
            db.add(ProjectModel(
                id=project_id,
                name=f"vm-project-{suffix}",
                is_admin=False,
                core=8,
                memory_g=16,
                storage_capacity_g=128,
                user_installable=True,
            ))
            db.add(NodeModel(
                name=node_name,
                description="VM project contract test",
                domain="no-network.invalid",
                user_name="fake-user",
                port=22,
                core=4,
                memory=8192,
                cpu_gen="fake-cpu",
                os_like="debian",
                os_name="Fake Linux",
                os_version="1",
                status=10,
                ansible_facts={},
            ))
            db.flush()
            db.add_all([
                DomainModel(
                    uuid=target_uuid,
                    name=f"vm-project-target-{suffix}",
                    core=2,
                    memory=2048,
                    status=5,
                    node_name=node_name,
                    update_token=suffix,
                ),
                DomainModel(
                    uuid=other_uuid,
                    name=f"vm-project-other-{suffix}",
                    core=2,
                    memory=2048,
                    status=5,
                    node_name=node_name,
                    update_token=suffix,
                ),
            ])

        response = api_client.patch(
            f"/api/tasks/vms/{target_uuid}/project",
            headers=_headers(username),
            json={"projectId": project_id},
        )
        assert response.status_code == 200, response.text

        with SessionLocal() as db:
            target = db.query(DomainModel).filter(DomainModel.uuid == target_uuid).one()
            other = db.query(DomainModel).filter(DomainModel.uuid == other_uuid).one()
            assert target.owner_project_id == project_id
            assert other.owner_project_id is None

        schema = api_client.get("/api/openapi.json").json()
        body_schema = schema["components"]["schemas"]["DomainProjectForUpdate"]
        assert set(body_schema["properties"]) == {"projectId"}
        assert body_schema["required"] == ["projectId"]
    finally:
        with SessionLocal.begin() as db:
            db.query(DomainModel).filter(
                DomainModel.uuid.in_([target_uuid, other_uuid])
            ).delete(synchronize_session=False)
            db.query(ProjectModel).filter(ProjectModel.id == project_id).delete()
            db.query(NodeModel).filter(NodeModel.name == node_name).delete()
            db.query(UserModel).filter(UserModel.username == username).delete()
