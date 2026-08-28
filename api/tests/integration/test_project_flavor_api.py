import time
from datetime import timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from auth.router import create_access_token
from domain.models import DomainModel
from flavor.models import FlavorModel
from mixin.database import SessionLocal
from node.models import NodeModel
from project.models import ProjectModel
from task.models import TaskModel
from user.models import UserModel, UserScopeModel


pytestmark = [pytest.mark.integration, pytest.mark.timeout(60)]


def _headers(
    username: str,
    *,
    scopes: list[str] | None = None,
    projects: list[str] | None = None,
) -> dict[str, str]:
    token = create_access_token(
        data={
            "sub": username,
            "scopes": scopes or ["user", "admin"],
            "projects": projects or [],
        },
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
    outsider = f"project-outsider-{suffix}"
    project_name = f"project-contract-{suffix}"
    renamed_project = f"project-renamed-{suffix}"
    node_name = f"project-node-{suffix}"
    domain_uuid = str(uuid4())
    task_uuids: list[str] = []

    try:
        with SessionLocal.begin() as db:
            db.add_all([
                UserModel(username=username, hashed_password="unused")
                for username in [creator, member, added_member, outsider]
            ])
            db.add_all([
                UserScopeModel(user_id=creator, name="admin"),
                UserScopeModel(user_id=member, name="project.read"),
                UserScopeModel(user_id=member, name="project.manage"),
            ])

        invalid_create = api_client.post(
            "/api/tasks/projects",
            headers=_headers(creator),
            json={"name": project_name},
        )
        assert invalid_create.status_code == 422

        invalid_user_response = api_client.post(
            "/api/tasks/projects",
            headers=_headers(creator),
            json={
                "name": f"invalid-{project_name}",
                "memberIds": [f"missing-{suffix}"],
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
            json={"name": project_name, "memberIds": [member]},
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
            assert {user.username for user in project.users} == {member}

        member_headers = _headers(
            member,
            scopes=["project.read", "project.manage"],
            projects=[project_id],
        )
        admin_list_response = api_client.get(
            "/api/projects",
            headers=_headers(creator),
            params={"admin": "true", "nameLike": project_name},
        )
        assert admin_list_response.status_code == 200
        assert admin_list_response.json()["count"] == 0
        assert api_client.get(
            f"/api/projects/{project_id}",
            headers=_headers(creator),
        ).status_code == 404

        list_response = api_client.get(
            "/api/projects",
            headers=member_headers,
            params={"nameLike": project_name},
        )
        assert list_response.status_code == 200, list_response.text
        assert list_response.json()["count"] == 1
        assert list_response.json()["data"][0]["id"] == project_id
        assert list_response.json()["data"][0]["memberCount"] == 1

        creator_cannot_rename = api_client.patch(
            f"/api/projects/{project_id}",
            headers=_headers(creator),
            json={"name": renamed_project},
        )
        assert creator_cannot_rename.status_code == 404

        rename_response = api_client.patch(
            f"/api/projects/{project_id}",
            headers=member_headers,
            json={"name": f"  {renamed_project}  "},
        )
        assert rename_response.status_code == 200, rename_response.text
        assert rename_response.json()["name"] == renamed_project
        assert rename_response.json()["limits"]["enforced"] is False

        update_response = api_client.put(
            f"/api/projects/{project_id}/members/{added_member}",
            headers=member_headers,
        )
        assert update_response.status_code == 200, update_response.text
        idempotent_update = api_client.put(
            f"/api/projects/{project_id}/members/{added_member}",
            headers=member_headers,
        )
        assert idempotent_update.status_code == 200
        with SessionLocal() as db:
            project = db.query(ProjectModel).filter(ProjectModel.id == project_id).one()
            assert {user.username for user in project.users} == {member, added_member}

        candidates = api_client.get(
            f"/api/projects/{project_id}/member-candidates",
            headers=member_headers,
            params={"nameLike": outsider},
        )
        assert candidates.status_code == 200, candidates.text
        assert candidates.json() == {
            "count": 1,
            "data": [{"username": outsider}],
        }

        grants = api_client.put(
            f"/api/projects/{project_id}/resource-grants",
            headers=_headers(creator),
            json={"storagePoolIds": [], "networkPoolIds": [], "flavorIds": []},
        )
        assert grants.status_code == 200, grants.text
        assert grants.json()["resourceGrants"] == {
            "storagePoolIds": [],
            "networkPoolIds": [],
            "flavorIds": [],
        }

        remove_response = api_client.delete(
            f"/api/projects/{project_id}/members/{added_member}",
            headers=member_headers,
        )
        assert remove_response.status_code == 200
        idempotent_remove = api_client.delete(
            f"/api/projects/{project_id}/members/{added_member}",
            headers=member_headers,
        )
        assert idempotent_remove.status_code == 200
        last_member = api_client.delete(
            f"/api/projects/{project_id}/members/{member}",
            headers=member_headers,
        )
        assert last_member.status_code == 409

        with SessionLocal.begin() as db:
            db.add(NodeModel(
                name=node_name,
                description="Project delete guard test",
                domain="no-network.invalid",
                user_name="unused",
                port=22,
                core=1,
                memory=1024,
                cpu_gen="test",
                os_like="linux",
                os_name="test",
                os_version="1",
                status=10,
                ansible_facts={},
            ))
            db.flush()
            domain = DomainModel(
                uuid=domain_uuid,
                name=f"project-vm-{suffix}",
                core=1,
                memory=1024,
                status=5,
                update_token=suffix,
                node_name=node_name,
            )
            domain.owner_project_id = project_id
            db.add(domain)

        guarded_delete = api_client.delete(
            f"/api/tasks/projects/{project_id}",
            headers=_headers(creator),
        )
        assert guarded_delete.status_code == 409

        with SessionLocal.begin() as db:
            db.query(DomainModel).filter(DomainModel.uuid == domain_uuid).delete()

        delete_response = api_client.delete(
            f"/api/tasks/projects/{project_id}",
            headers=_headers(creator),
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
    finally:
        with SessionLocal.begin() as db:
            db.query(TaskModel).filter(TaskModel.uuid.in_(task_uuids)).delete(
                synchronize_session=False
            )
            db.query(DomainModel).filter(DomainModel.uuid == domain_uuid).delete(
                synchronize_session=False
            )
            db.query(ProjectModel).filter(
                ProjectModel.name.in_([project_name, renamed_project])
            ).delete(synchronize_session=False)
            db.query(NodeModel).filter(NodeModel.name == node_name).delete(
                synchronize_session=False
            )
            db.query(UserModel).filter(
                UserModel.username.in_([creator, member, added_member, outsider])
            ).delete(synchronize_session=False)


def test_project_membership_add_requires_new_token_and_remove_is_immediate(
    api_client: TestClient,
) -> None:
    suffix = uuid4().hex
    manager = f"project-manager-{suffix}"
    candidate = f"project-candidate-{suffix}"
    project_id = suffix[:6]

    try:
        with SessionLocal.begin() as db:
            manager_user = UserModel(username=manager, hashed_password="unused")
            candidate_user = UserModel(username=candidate, hashed_password="unused")
            db.add_all([manager_user, candidate_user])
            db.add_all([
                UserScopeModel(user_id=manager, name="project.read"),
                UserScopeModel(user_id=manager, name="project.manage"),
                UserScopeModel(user_id=candidate, name="project.read"),
            ])
            db.add(ProjectModel(
                id=project_id,
                name=f"token-boundary-{suffix}",
                users=[manager_user],
            ))

        manager_headers = _headers(
            manager,
            scopes=["project.read", "project.manage"],
            projects=[project_id],
        )
        stale_candidate_headers = _headers(
            candidate,
            scopes=["project.read"],
            projects=[],
        )
        added = api_client.put(
            f"/api/projects/{project_id}/members/{candidate}",
            headers=manager_headers,
        )
        assert added.status_code == 200, added.text

        stale_read = api_client.get(
            f"/api/projects/{project_id}",
            headers=stale_candidate_headers,
        )
        assert stale_read.status_code == 404

        refreshed_candidate_headers = _headers(
            candidate,
            scopes=["project.read"],
            projects=[project_id],
        )
        refreshed_read = api_client.get(
            f"/api/projects/{project_id}",
            headers=refreshed_candidate_headers,
        )
        assert refreshed_read.status_code == 200, refreshed_read.text

        removed = api_client.delete(
            f"/api/projects/{project_id}/members/{candidate}",
            headers=manager_headers,
        )
        assert removed.status_code == 200, removed.text
        removed_read = api_client.get(
            f"/api/projects/{project_id}",
            headers=refreshed_candidate_headers,
        )
        assert removed_read.status_code == 404
    finally:
        with SessionLocal.begin() as db:
            db.query(ProjectModel).filter(ProjectModel.id == project_id).delete(
                synchronize_session=False
            )
            db.query(UserModel).filter(
                UserModel.username.in_([manager, candidate])
            ).delete(synchronize_session=False)


def test_flavor_create_list_delete_path_and_validation(
    api_client: TestClient,
) -> None:
    suffix = uuid4().hex
    username = f"flavor-user-{suffix}"
    flavor_name = f"flavor-contract-{suffix}"
    other_flavor_name = f"flavor-other-{suffix}"
    project_id = suffix[:6]
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

        with SessionLocal.begin() as db:
            user = db.get(UserModel, username)
            flavor = db.get(FlavorModel, flavor_id)
            assert user is not None
            assert flavor is not None
            db.add(ProjectModel(
                id=project_id,
                name=f"flavor-project-{suffix}",
                users=[user],
                flavors=[flavor],
            ))

        duplicate_response = api_client.post(
            "/api/flavors",
            headers=_headers(username),
            json=payload,
        )
        assert duplicate_response.status_code == 400

        list_response = api_client.get(
            "/api/flavors",
            headers=_headers(username, projects=[project_id]),
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
            db.query(ProjectModel).filter(ProjectModel.id == project_id).delete(
                synchronize_session=False,
            )
            db.query(FlavorModel).filter(
                FlavorModel.name.in_([flavor_name, other_flavor_name])
            ).delete(synchronize_session=False)
            db.query(UserModel).filter(UserModel.username == username).delete()
