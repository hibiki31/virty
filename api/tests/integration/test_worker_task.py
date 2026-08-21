import time
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from mixin.database import SessionLocal
from node.models import NodeModel
from task.models import TaskModel
from user.models import UserModel


pytestmark = [pytest.mark.integration, pytest.mark.timeout(60)]


def _wait_for_tasks(
    client: TestClient,
    task_uuids: list[str],
    headers: dict[str, str],
    timeout_seconds: float = 30,
) -> dict[str, dict[str, Any]]:
    deadline = time.monotonic() + timeout_seconds
    last_tasks: dict[str, dict[str, Any]] = {}

    while time.monotonic() < deadline:
        for task_uuid in task_uuids:
            response = client.get(f"/api/tasks/{task_uuid}", headers=headers)
            response.raise_for_status()
            last_tasks[task_uuid] = response.json()
        if all(
            task["status"] in {"finish", "error", "lost"}
            for task in last_tasks.values()
        ):
            return last_tasks
        time.sleep(0.2)

    details = "; ".join(
        f"uuid={task_uuid}, status={task.get('status')}, "
        f"message={task.get('message')}, log={task.get('log')}"
        for task_uuid, task in last_tasks.items()
    )
    pytest.fail(
        f"Worker taskが{timeout_seconds:.0f}秒以内に完了しませんでした: {details}"
    )


def test_api_enqueued_node_and_reload_tasks_finish(api_client: TestClient) -> None:
    suffix = uuid4().hex
    username = f"worker-{suffix}"
    password = "Virty-Test_2026!"
    node_name = f"worker-node-{suffix}"

    try:
        setup = api_client.post(
            "/api/auth/setup",
            json={"username": username, "password": password},
        )
        assert setup.status_code == 201

        login = api_client.post(
            "/api/auth",
            data={"username": username, "password": password},
        )
        assert login.status_code == 200
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        queued = api_client.post(
            "/api/tasks/nodes",
            headers=headers,
            json={
                "name": node_name,
                "description": "fake backend integration test",
                "domain": "no-network.invalid",
                "userName": "fake-user",
                "port": 22,
                "libvirtRole": False,
            },
        )
        assert queued.status_code == 200
        task_uuids = [task["uuid"] for task in queued.json()]
        assert len(task_uuids) == 4

        tasks = _wait_for_tasks(api_client, task_uuids, headers)
        errors = [
            f"uuid={task_uuid}, status={task['status']}, "
            f"message={task.get('message')}, log={task.get('log')}"
            for task_uuid, task in tasks.items()
            if task["status"] != "finish"
        ]
        assert errors == []

        with SessionLocal() as db:
            node = db.query(NodeModel).filter(NodeModel.name == node_name).one()
            assert node.domain == "no-network.invalid"
            assert node.ansible_facts == {"virty_backend": "fake"}
    finally:
        with SessionLocal.begin() as db:
            db.query(NodeModel).filter(NodeModel.name == node_name).delete()
            db.query(TaskModel).filter(TaskModel.user_id == username).delete()
            db.query(UserModel).filter(UserModel.username == username).delete()
