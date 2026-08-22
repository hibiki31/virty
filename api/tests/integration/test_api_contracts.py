import time
from datetime import timedelta
from typing import cast
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.routing import iter_route_contexts
from fastapi.testclient import TestClient

from auth.router import create_access_token
from domain.models import DomainModel
from mixin.database import SessionLocal
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
