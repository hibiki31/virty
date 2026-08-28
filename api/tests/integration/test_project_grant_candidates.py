from datetime import timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from auth.router import create_access_token
from flavor.models import FlavorModel
from mixin.database import SessionLocal
from network.models import NetworkPoolModel
from project.models import ProjectModel
from storage.models import StoragePoolModel
from user.models import UserModel, UserScopeModel


pytestmark = [pytest.mark.integration, pytest.mark.timeout(60)]


def _headers(
    username: str,
    *,
    scopes: list[str],
    projects: list[str],
) -> dict[str, str]:
    token = create_access_token(
        data={"sub": username, "scopes": scopes, "projects": projects},
        expires_delta=timedelta(hours=1),
    )
    return {"Authorization": f"Bearer {token}"}


def test_resource_grant_candidates_are_admin_only_and_include_ungranted_resources(
    api_client: TestClient,
) -> None:
    suffix = uuid4().hex
    admin = f"grant-admin-{suffix}"
    manager = f"grant-manager-{suffix}"
    project_id = suffix[:6]
    storage_name = f"candidate-storage-{suffix}"
    network_name = f"candidate-network-{suffix}"
    flavor_name = f"candidate-flavor-{suffix}"

    try:
        with SessionLocal.begin() as db:
            admin_user = UserModel(username=admin, hashed_password="unused")
            manager_user = UserModel(username=manager, hashed_password="unused")
            db.add_all([admin_user, manager_user])
            db.add_all([
                UserScopeModel(user_id=admin, name="admin"),
                UserScopeModel(user_id=manager, name="project.manage"),
            ])
            db.add(ProjectModel(
                id=project_id,
                name=f"grant-candidates-{suffix}",
                users=[admin_user, manager_user],
            ))
            db.add(StoragePoolModel(name=storage_name))
            db.add(NetworkPoolModel(name=network_name))
            db.add(FlavorModel(
                name=flavor_name,
                os="linux",
                manual_url="https://no-network.invalid/manual",
                icon="test.svg",
                cloud_init_ready=True,
                description="Project grant candidate",
            ))

        admin_headers = _headers(
            admin,
            scopes=["admin", "project.manage"],
            projects=[project_id],
        )
        response = api_client.get(
            f"/api/projects/{project_id}/resource-grant-candidates",
            headers=admin_headers,
        )
        assert response.status_code == 200, response.text
        payload = response.json()
        assert any(item["name"] == storage_name for item in payload["storagePools"])
        assert any(item["name"] == network_name for item in payload["networkPools"])
        assert any(item["name"] == flavor_name for item in payload["flavors"])

        denied = api_client.get(
            f"/api/projects/{project_id}/resource-grant-candidates",
            headers=_headers(
                manager,
                scopes=["project.manage"],
                projects=[project_id],
            ),
        )
        assert denied.status_code == 403

        missing = api_client.get(
            "/api/projects/ffffff/resource-grant-candidates",
            headers=admin_headers,
        )
        assert missing.status_code == 404
        assert missing.json()["detail"]["code"] == "project_not_found"
    finally:
        with SessionLocal.begin() as db:
            db.query(ProjectModel).filter(ProjectModel.id == project_id).delete(
                synchronize_session=False,
            )
            db.query(StoragePoolModel).filter(
                StoragePoolModel.name == storage_name,
            ).delete(synchronize_session=False)
            db.query(NetworkPoolModel).filter(
                NetworkPoolModel.name == network_name,
            ).delete(synchronize_session=False)
            db.query(FlavorModel).filter(FlavorModel.name == flavor_name).delete(
                synchronize_session=False,
            )
            db.query(UserModel).filter(
                UserModel.username.in_([admin, manager]),
            ).delete(synchronize_session=False)
