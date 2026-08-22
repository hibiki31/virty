import json
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from auth.router import create_access_token
from mixin.database import SessionLocal
from task.models import TaskModel
from user.models import UserModel, UserScopeModel


pytestmark = [pytest.mark.integration, pytest.mark.timeout(60)]


def _headers(username: str, scopes: list[str]) -> dict[str, str]:
    token = create_access_token(
        data={"sub": username, "scopes": scopes, "projects": []},
        expires_delta=timedelta(hours=1),
    )
    return {"Authorization": f"Bearer {token}"}


def test_get_tasks_respects_user_visibility_and_admin_override(
    api_client: TestClient,
) -> None:
    suffix = uuid4().hex
    regular_user = f"task-list-user-{suffix}"
    other_user = f"task-list-other-{suffix}"
    admin_user = f"task-list-admin-{suffix}"
    usernames = [regular_user, other_user, admin_user]
    resource = f"task-list-resource-{suffix}"
    own_task_uuid = f"task-list-own-{suffix}"
    other_task_uuid = f"task-list-other-{suffix}"
    task_uuids = [own_task_uuid, other_task_uuid]
    own_private = f"OWN_PRIVATE_SENTINEL_{suffix}"
    other_private = f"OTHER_PRIVATE_SENTINEL_{suffix}"
    now = datetime.now(UTC)

    try:
        with SessionLocal.begin() as db:
            db.add_all([
                UserModel(username=username, hashed_password="unused")
                for username in usernames
            ])
            db.add_all([
                UserScopeModel(user_id=regular_user, name="user"),
                UserScopeModel(user_id=other_user, name="user"),
                UserScopeModel(user_id=admin_user, name="admin"),
            ])
            db.flush()
            own_task = TaskModel(
                uuid=own_task_uuid,
                post_time=now,
                user_id=regular_user,
                status="finish",
                resource=resource,
                object="private-test",
                method="get",
                request=json.dumps({"private": own_private}),
                result={"private": own_private},
            )
            own_task.message = own_private
            own_task.log = own_private
            other_task = TaskModel(
                uuid=other_task_uuid,
                post_time=now - timedelta(seconds=1),
                user_id=other_user,
                status="finish",
                resource=resource,
                object="private-test",
                method="get",
                request=json.dumps({"private": other_private}),
                result={"private": other_private},
            )
            other_task.message = other_private
            other_task.log = other_private
            db.add_all([own_task, other_task])

        regular_query = {
            "resource": resource,
            "limit": "10",
            "page": "0",
            "admin": "false",
        }
        regular_response = api_client.get(
            "/api/tasks",
            params=regular_query,
            headers=_headers(regular_user, ["user"]),
        )
        assert regular_response.status_code == 200, regular_response.text
        regular_body = regular_response.json()

        assert regular_body["count"] == 1
        assert [task["uuid"] for task in regular_body["data"]] == [own_task_uuid]
        assert own_private in regular_response.text
        assert other_private not in regular_response.text

        admin_query = {
            "resource": resource,
            "limit": "10",
            "page": "0",
            "admin": "true",
        }
        admin_response = api_client.get(
            "/api/tasks",
            params=admin_query,
            headers=_headers(admin_user, ["admin"]),
        )
        assert admin_response.status_code == 200, admin_response.text
        admin_body = admin_response.json()

        assert admin_body["count"] == 2
        assert {task["uuid"] for task in admin_body["data"]} == set(task_uuids)
        assert own_private in admin_response.text
        assert other_private in admin_response.text
    finally:
        with SessionLocal.begin() as db:
            db.query(TaskModel).filter(TaskModel.uuid.in_(task_uuids)).delete(
                synchronize_session=False
            )
            db.query(UserScopeModel).filter(
                UserScopeModel.user_id.in_(usernames)
            ).delete(synchronize_session=False)
            db.query(UserModel).filter(UserModel.username.in_(usernames)).delete(
                synchronize_session=False
            )
