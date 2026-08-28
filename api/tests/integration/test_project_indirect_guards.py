from datetime import timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from auth.router import create_access_token
from domain.models import DomainDriveModel, DomainModel
from flavor.models import FlavorModel
from mixin.database import SessionLocal
from node.models import NodeModel
from project.models import ProjectModel
from storage.models import (
    AssociationStoragePoolModel,
    ImageModel,
    StorageModel,
    StoragePoolModel,
)
from user.models import UserModel, UserScopeModel


pytestmark = [pytest.mark.integration, pytest.mark.timeout(60)]


def _headers(username: str) -> dict[str, str]:
    token = create_access_token(
        data={"sub": username, "scopes": ["user", "admin"], "projects": []},
        expires_delta=timedelta(hours=1),
    )
    return {"Authorization": f"Bearer {token}"}


def test_indirect_membership_and_grant_removal_paths_are_guarded(
    api_client: TestClient,
) -> None:
    suffix = uuid4().hex
    caller = f"project-guard-admin-{suffix}"
    member = f"project-guard-member-{suffix}"
    project_id = suffix[:6]
    node_name = f"project-guard-node-{suffix}"
    storage_uuid = f"project-guard-storage-{suffix}"
    domain_uuid = str(uuid4())
    drive_path = f"/project-guard/{suffix}/vm.qcow2"
    flavor_name = f"project-guard-flavor-{suffix}"
    pool_name = f"project-guard-pool-{suffix}"
    flavor_id = -1
    pool_id = -1

    try:
        with SessionLocal.begin() as db:
            caller_model = UserModel(username=caller, hashed_password="unused")
            member_model = UserModel(username=member, hashed_password="unused")
            node = NodeModel(
                name=node_name,
                description="Project indirect guard test",
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
            )
            storage = StorageModel(
                uuid=storage_uuid,
                name=f"storage-{suffix}",
                node_name=node_name,
                capacity=1024,
                available=1024,
                path=f"/project-guard/{suffix}",
                active=True,
                auto_start=True,
                status=2,
                update_token=suffix,
            )
            storage_pool = StoragePoolModel(
                name=pool_name,
                storages=[AssociationStoragePoolModel(storage=storage)],
            )
            flavor = FlavorModel(
                name=flavor_name,
                os="linux",
                manual_url="https://no-network.invalid/manual",
                icon="test.svg",
                cloud_init_ready=False,
                description="Project indirect guard test",
            )
            project = ProjectModel(
                id=project_id,
                name=f"project-guard-{suffix}",
                users=[member_model],
                storage_pools=[storage_pool],
                flavors=[flavor],
            )
            drive = DomainDriveModel(
                target="vda",
                device="disk",
                type="file",
                update_token=suffix,
            )
            drive.source = drive_path
            domain = DomainModel(
                uuid=domain_uuid,
                name=f"vm-{suffix}",
                core=1,
                memory=1024,
                status=5,
                update_token=suffix,
                node_name=node_name,
                drives=[drive],
            )
            domain.owner_project_id = project_id
            image = ImageModel(
                name=f"vm-{suffix}.qcow2",
                storage_uuid=storage_uuid,
                capacity=1024,
                allocation=512,
                path=drive_path,
                update_token=suffix,
                flavor=flavor,
            )
            image.domain_uuid = domain_uuid
            db.add_all([
                caller_model,
                member_model,
                UserScopeModel(user_id=caller, name="admin"),
                node,
                project,
                domain,
                image,
            ])
            db.flush()
            flavor_id = flavor.id
            pool_id = storage_pool.id

        sole_member_delete = api_client.delete(
            f"/api/users/{member}",
            headers=_headers(caller),
        )
        assert sole_member_delete.status_code == 409, sole_member_delete.text

        storage_removal = api_client.patch(
            "/api/storages/pools",
            headers=_headers(caller),
            json={"id": pool_id, "storageUuids": []},
        )
        assert storage_removal.status_code == 409, storage_removal.text
        storage_pool_delete = api_client.delete(
            f"/api/storages/pools/{pool_id}",
            headers=_headers(caller),
        )
        assert storage_pool_delete.status_code == 409, storage_pool_delete.text

        flavor_removal = api_client.delete(
            f"/api/flavors/{flavor_id}",
            headers=_headers(caller),
        )
        assert flavor_removal.status_code == 409, flavor_removal.text

        with SessionLocal.begin() as db:
            loaded_project = db.get(ProjectModel, project_id)
            loaded_caller = db.get(UserModel, caller)
            assert loaded_project is not None
            assert loaded_caller is not None
            loaded_project.users.append(loaded_caller)
            db.query(DomainModel).filter(DomainModel.uuid == domain_uuid).delete()

        member_delete = api_client.delete(
            f"/api/users/{member}",
            headers=_headers(caller),
        )
        assert member_delete.status_code == 200, member_delete.text

        storage_pool_delete = api_client.delete(
            f"/api/storages/pools/{pool_id}",
            headers=_headers(caller),
        )
        assert storage_pool_delete.status_code == 200, storage_pool_delete.text
        assert storage_pool_delete.json() == {"deleted": True, "id": pool_id}

        flavor_removal = api_client.delete(
            f"/api/flavors/{flavor_id}",
            headers=_headers(caller),
        )
        assert flavor_removal.status_code == 200, flavor_removal.text
    finally:
        with SessionLocal.begin() as db:
            db.query(DomainModel).filter(DomainModel.uuid == domain_uuid).delete(
                synchronize_session=False,
            )
            db.query(ImageModel).filter(ImageModel.storage_uuid == storage_uuid).delete(
                synchronize_session=False,
            )
            db.query(ProjectModel).filter(ProjectModel.id == project_id).delete(
                synchronize_session=False,
            )
            db.query(StoragePoolModel).filter(StoragePoolModel.name == pool_name).delete(
                synchronize_session=False,
            )
            db.query(StorageModel).filter(StorageModel.uuid == storage_uuid).delete(
                synchronize_session=False,
            )
            db.query(FlavorModel).filter(FlavorModel.name == flavor_name).delete(
                synchronize_session=False,
            )
            db.query(NodeModel).filter(NodeModel.name == node_name).delete(
                synchronize_session=False,
            )
            db.query(UserModel).filter(
                UserModel.username.in_([caller, member]),
            ).delete(synchronize_session=False)
