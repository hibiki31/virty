import time
from datetime import timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from auth.router import create_access_token
from flavor.models import FlavorModel
from mixin.database import SessionLocal
from project.models import ProjectModel
from task.models import TaskModel
from user.models import UserModel, UserScopeModel


pytestmark = [pytest.mark.integration, pytest.mark.timeout(60)]


def _headers(username: str) -> dict[str, str]:
    token = create_access_token(
        data={"sub": username, "scopes": ["user", "admin"], "projects": []},
        expires_delta=timedelta(hours=1),
    )
    return {"Authorization": f"Bearer {token}"}


def _wait_for_terminal_task(task_uuid: str, timeout_seconds: float = 10) -> str:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        with SessionLocal() as db:
            task = db.query(TaskModel).filter(TaskModel.uuid == task_uuid).one()
            if task.status in {"finish", "error", "lost"}:
                return task.status
        time.sleep(0.1)
    pytest.fail(f"task {task_uuid} が{timeout_seconds:.0f}秒以内に完了しませんでした")


def test_project_crud_task_status_path_and_validation(
    api_client: TestClient,
) -> None:
    suffix = uuid4().hex
    creator = f"project-creator-{suffix}"
    member = f"project-member-{suffix}"
    added_member = f"project-added-{suffix}"
    project_name = f"project-contract-{suffix}"
    other_project_id = suffix[-6:]
    task_uuids: list[str] = []

    try:
        with SessionLocal.begin() as db:
            db.add_all([
                UserModel(username=username, hashed_password="unused")
                for username in [creator, member, added_member]
            ])
            db.add(UserScopeModel(user_id=creator, name="admin"))

        invalid_create = api_client.post(
            "/api/tasks/projects",
            headers=_headers(creator),
            json={"projectName": project_name},
        )
        assert invalid_create.status_code == 422

        invalid_user_response = api_client.post(
            "/api/tasks/projects",
            headers=_headers(creator),
            json={
                "projectName": f"invalid-{project_name}",
                "userIds": [f"missing-{suffix}"],
            },
        )
        assert invalid_user_response.status_code == 200
        invalid_user_task = invalid_user_response.json()[0]
        task_uuids.append(invalid_user_task["uuid"])
        assert _wait_for_terminal_task(invalid_user_task["uuid"]) == "error"
        with SessionLocal() as db:
            assert (
                db.query(ProjectModel)
                .filter(ProjectModel.name == f"invalid-{project_name}")
                .one_or_none()
                is None
            )

        create_response = api_client.post(
            "/api/tasks/projects",
            headers=_headers(creator),
            json={"projectName": project_name, "userIds": [member]},
        )
        assert create_response.status_code == 200, create_response.text
        create_task = create_response.json()[0]
        task_uuids.append(create_task["uuid"])
        assert create_task["status"] in {"init", "start"}
        assert _wait_for_terminal_task(create_task["uuid"]) == "finish"

        with SessionLocal() as db:
            project = (
                db.query(ProjectModel).filter(ProjectModel.name == project_name).one()
            )
            project_id = project.id
            assert {user.username for user in project.users} == {creator, member}

        list_response = api_client.get(
            "/api/projects",
            headers=_headers(creator),
            params={"admin": "true", "nameLike": project_name},
        )
        assert list_response.status_code == 200, list_response.text
        assert list_response.json()["count"] == 1
        assert list_response.json()["data"][0]["id"] == project_id

        update_response = api_client.put(
            "/api/projects",
            headers=_headers(creator),
            json={"projectId": project_id, "userId": added_member},
        )
        assert update_response.status_code == 200, update_response.text
        with SessionLocal() as db:
            project = db.query(ProjectModel).filter(ProjectModel.id == project_id).one()
            assert {user.username for user in project.users} == {
                creator,
                member,
                added_member,
            }

        invalid_update = api_client.put(
            "/api/projects",
            headers=_headers(creator),
            json={"projectId": project_id, "userId": f"missing-{suffix}"},
        )
        assert invalid_update.status_code == 400

        with SessionLocal.begin() as db:
            db.add(ProjectModel(id=other_project_id, name=f"other-{project_name}"))

        delete_response = api_client.request(
            "DELETE",
            f"/api/tasks/projects/{project_id}",
            headers=_headers(creator),
            json={"projectId": other_project_id},
        )
        assert delete_response.status_code == 200, delete_response.text
        delete_task = delete_response.json()[0]
        task_uuids.append(delete_task["uuid"])
        assert _wait_for_terminal_task(delete_task["uuid"]) == "finish"

        with SessionLocal() as db:
            assert (
                db.query(ProjectModel).filter(ProjectModel.id == project_id).one_or_none()
                is None
            )
            assert (
                db.query(ProjectModel)
                .filter(ProjectModel.id == other_project_id)
                .one_or_none()
                is not None
            )
    finally:
        with SessionLocal.begin() as db:
            db.query(TaskModel).filter(TaskModel.uuid.in_(task_uuids)).delete(
                synchronize_session=False
            )
            db.query(ProjectModel).filter(
                ProjectModel.name.in_([project_name, f"other-{project_name}"])
            ).delete(synchronize_session=False)
            db.query(UserModel).filter(
                UserModel.username.in_([creator, member, added_member])
            ).delete(synchronize_session=False)


def test_flavor_create_list_delete_path_and_validation(
    api_client: TestClient,
) -> None:
    suffix = uuid4().hex
    username = f"flavor-user-{suffix}"
    flavor_name = f"flavor-contract-{suffix}"
    other_flavor_name = f"flavor-other-{suffix}"
    payload = {
        "name": flavor_name,
        "os": "linux",
        "manualUrl": "https://no-network.invalid/manual",
        "icon": "test.svg",
        "cloudInitReady": True,
        "description": "flavor contract integration test",
    }

    try:
        with SessionLocal.begin() as db:
            db.add(UserModel(username=username, hashed_password="unused"))
            db.add(UserScopeModel(user_id=username, name="admin"))

        invalid_create = api_client.post(
            "/api/flavors",
            headers=_headers(username),
            json={key: value for key, value in payload.items() if key != "description"},
        )
        assert invalid_create.status_code == 422

        create_response = api_client.post(
            "/api/flavors",
            headers=_headers(username),
            json=payload,
        )
        assert create_response.status_code == 200, create_response.text
        assert len(create_response.json()) == 1
        flavor_id = create_response.json()[0]["id"]

        duplicate_response = api_client.post(
            "/api/flavors",
            headers=_headers(username),
            json=payload,
        )
        assert duplicate_response.status_code == 400

        list_response = api_client.get(
            "/api/flavors",
            headers=_headers(username),
            params={"nameLike": flavor_name},
        )
        assert list_response.status_code == 200, list_response.text
        assert list_response.json()["count"] == 1
        assert list_response.json()["data"][0]["id"] == flavor_id

        with SessionLocal.begin() as db:
            other_flavor = FlavorModel(
                name=other_flavor_name,
                os="linux",
                manual_url="https://no-network.invalid/other",
                icon="test.svg",
                cloud_init_ready=False,
                description="other flavor",
            )
            db.add(other_flavor)
            db.flush()
            other_flavor_id = other_flavor.id

        delete_response = api_client.request(
            "DELETE",
            f"/api/flavors/{flavor_id}",
            headers=_headers(username),
            json={"id": other_flavor_id},
        )
        assert delete_response.status_code == 200, delete_response.text
        assert delete_response.json()["id"] == flavor_id

        with SessionLocal() as db:
            assert (
                db.query(FlavorModel).filter(FlavorModel.id == flavor_id).one_or_none()
                is None
            )
            assert (
                db.query(FlavorModel)
                .filter(FlavorModel.id == other_flavor_id)
                .one_or_none()
                is not None
            )

        missing_delete = api_client.delete(
            f"/api/flavors/{flavor_id}", headers=_headers(username)
        )
        invalid_path = api_client.delete(
            "/api/flavors/not-an-integer", headers=_headers(username)
        )
        assert missing_delete.status_code == 404
        assert invalid_path.status_code == 422
    finally:
        with SessionLocal.begin() as db:
            db.query(FlavorModel).filter(
                FlavorModel.name.in_([flavor_name, other_flavor_name])
            ).delete(synchronize_session=False)
            db.query(UserModel).filter(UserModel.username == username).delete()
