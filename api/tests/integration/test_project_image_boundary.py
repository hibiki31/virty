from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from auth.router import create_access_token
from domain import tasks as domain_tasks
from domain.models import DomainModel
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
from task.models import TaskModel
from task.schemas import TaskRequest
from user.models import UserModel, UserScopeModel


pytestmark = [pytest.mark.integration, pytest.mark.timeout(60)]


def _headers(username: str, project_ids: list[str]) -> dict[str, str]:
    token = create_access_token(
        data={
            "sub": username,
            "scopes": [
                "user",
                "image.read",
                "image.manage",
                "vm.create",
                "vm.attach",
            ],
            "projects": project_ids,
        },
        expires_delta=timedelta(hours=1),
    )
    return {"Authorization": f"Bearer {token}"}


def _flavor(name: str) -> FlavorModel:
    return FlavorModel(
        name=name,
        os="linux",
        manual_url="https://no-network.invalid/manual",
        icon="test.svg",
        cloud_init_ready=False,
        cloud_init_user="cloud-user",
        description=name,
    )


def test_image_list_update_and_vm_copy_use_one_project_boundary(
    api_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    suffix = uuid4().hex
    username = f"image-project-user-{suffix}"
    project_a_id = suffix[:6]
    project_b_id = suffix[6:12]
    node_name = f"image-project-node-{suffix}"
    storage_uuid = f"image-project-storage-{suffix}"
    allowed_name = f"allowed-{suffix}.qcow2"
    generic_name = f"generic-{suffix}.qcow2"
    cross_name = f"cross-{suffix}.qcow2"
    domain_uuid = f"image-project-vm-{suffix}"

    try:
        with SessionLocal.begin() as db:
            user = UserModel(username=username, hashed_password="unused")
            db.add(user)
            db.add_all([
                UserScopeModel(user_id=username, name="user"),
                UserScopeModel(user_id=username, name="image.read"),
                UserScopeModel(user_id=username, name="image.manage"),
                UserScopeModel(user_id=username, name="vm.create"),
                UserScopeModel(user_id=username, name="vm.attach"),
            ])
            node = NodeModel(
                name=node_name,
                description="Project image boundary test",
                domain="no-network.invalid",
                user_name="unused",
                port=22,
                core=4,
                memory=8192,
                cpu_gen="test",
                os_like="linux",
                os_name="test",
                os_version="1",
                status=10,
                ansible_facts={},
            )
            storage = StorageModel(
                uuid=storage_uuid,
                name=f"image-project-storage-{suffix}",
                node_name=node_name,
                capacity=1024,
                available=1024,
                path=f"/tmp/image-project-{suffix}",
                active=True,
                auto_start=True,
                status=10,
                update_token=suffix,
            )
            storage_pool = StoragePoolModel(
                name=f"image-project-pool-{suffix}",
                storages=[AssociationStoragePoolModel(storage=storage)],
            )
            flavor_a = _flavor(f"image-project-flavor-a-{suffix}")
            flavor_b = _flavor(f"image-project-flavor-b-{suffix}")
            project_a = ProjectModel(
                id=project_a_id,
                name=f"image-project-a-{suffix}",
                users=[user],
                storage_pools=[storage_pool],
                flavors=[flavor_a],
            )
            project_b = ProjectModel(
                id=project_b_id,
                name=f"image-project-b-{suffix}",
                users=[user],
                flavors=[flavor_b],
            )
            db.add_all([node, project_a, project_b])
            db.flush()
            db.add(
                DomainModel(
                    uuid=domain_uuid,
                    name=f"image-project-vm-{suffix}",
                    core=1,
                    memory=1024,
                    status=5,
                    node=node,
                    owner_project=project_a,
                    update_token=suffix,
                )
            )
            images = [
                ImageModel(
                    name=allowed_name,
                    storage=storage,
                    capacity=64,
                    allocation=8,
                    path=f"{storage.path}/{allowed_name}",
                    update_token=suffix,
                    flavor=flavor_a,
                ),
                ImageModel(
                    name=generic_name,
                    storage=storage,
                    capacity=64,
                    allocation=8,
                    path=f"{storage.path}/{generic_name}",
                    update_token=suffix,
                    flavor=None,
                ),
                ImageModel(
                    name=cross_name,
                    storage=storage,
                    capacity=64,
                    allocation=8,
                    path=f"{storage.path}/{cross_name}",
                    update_token=suffix,
                    flavor=flavor_b,
                ),
            ]
            db.add_all(images)
            db.flush()
            flavor_a_id = flavor_a.id
            flavor_b_id = flavor_b.id
            generic_path = images[1].path
            cross_path = images[2].path

        headers = _headers(username, [project_a_id, project_b_id])
        listed = api_client.get(
            "/api/images",
            headers=headers,
            params={"projectId": project_a_id, "limit": 100},
        )
        assert listed.status_code == 200, listed.text
        assert {image["name"] for image in listed.json()["data"]} == {
            allowed_name,
            generic_name,
        }

        all_projects = api_client.get(
            "/api/images",
            headers=headers,
            params={"limit": 100},
        )
        assert all_projects.status_code == 200, all_projects.text
        assert {image["name"] for image in all_projects.json()["data"]} == {
            allowed_name,
            generic_name,
        }

        dashboard = api_client.get("/api/dashboard", headers=headers)
        assert dashboard.status_code == 200, dashboard.text
        assert dashboard.json()["images"] == {"count": 2}

        cross_update = api_client.patch(
            "/api/images",
            headers=headers,
            json={
                "projectId": project_a_id,
                "storageUuid": storage_uuid,
                "path": generic_path,
                "nodeName": node_name,
                "flavorId": flavor_b_id,
            },
        )
        assert cross_update.status_code == 404

        missing_project = api_client.patch(
            "/api/images",
            headers=headers,
            json={
                "storageUuid": storage_uuid,
                "path": generic_path,
                "nodeName": node_name,
                "flavorId": flavor_a_id,
            },
        )
        assert missing_project.status_code == 422

        updated = api_client.patch(
            "/api/images",
            headers=headers,
            json={
                "projectId": project_a_id,
                "storageUuid": storage_uuid,
                "path": generic_path,
                "nodeName": node_name,
                "flavorId": flavor_a_id,
            },
        )
        assert updated.status_code == 200, updated.text
        assert updated.json()["flavor"]["id"] == flavor_a_id

        denied_copy = api_client.post(
            "/api/tasks/vms",
            headers=headers,
            json={
                "type": "manual",
                "name": f"denied-copy-{suffix}",
                "nodeName": node_name,
                "projectId": project_a_id,
                "memoryMegaByte": 1024,
                "cpu": 1,
                "disks": [{
                    "type": "copy",
                    "savePoolUuid": storage_uuid,
                    "originalPoolUuid": storage_uuid,
                    "originalName": cross_name,
                    "sizeGigaByte": 64,
                }],
                "interface": [],
            },
        )
        assert denied_copy.status_code == 404

        denied_cdrom = api_client.patch(
            f"/api/tasks/vms/{domain_uuid}/cdrom",
            headers=headers,
            json={"target": "sda", "path": cross_path},
        )
        assert denied_cdrom.status_code == 404

        backend_calls: list[str] = []

        def unexpected_backend(**_kwargs: object) -> None:
            backend_calls.append("create_libvirt_backend")
            raise AssertionError("Project境界検査後にlibvirt backendが呼ばれました")

        monkeypatch.setattr(
            domain_tasks,
            "create_libvirt_backend",
            unexpected_backend,
        )
        task_request = TaskRequest(
            path_param={
                "uuid": domain_uuid,
                "ownerBinding": {
                    "principalId": username,
                    "ownerUserId": None,
                    "ownerProjectId": project_a_id,
                },
            },
            body={"target": "sda", "path": cross_path},
        )
        worker_model = TaskModel(
            uuid=str(uuid4()),
            post_time=datetime.now().astimezone(),
            user_id=username,
            status="start",
            resource="vm",
            object="cdrom",
            method="patch",
            request=task_request.model_dump_json(),
        )
        with SessionLocal.begin() as db:
            with pytest.raises(ValueError, match="outside the VM project grants"):
                domain_tasks.patch_vm_cdrom(db, worker_model, task_request)
        assert backend_calls == []

        schema = api_client.get("/api/openapi.json").json()
        update_schema = schema["components"]["schemas"][
            "ImageForUpdateImageFlavor"
        ]
        assert "projectId" in update_schema["required"]
        assert schema["paths"]["/api/images"]["patch"]["responses"]["200"][
            "content"
        ]["application/json"]["schema"] == {
            "$ref": "#/components/schemas/Image",
        }
    finally:
        with SessionLocal.begin() as db:
            db.query(DomainModel).filter(DomainModel.uuid == domain_uuid).delete(
                synchronize_session=False,
            )
            db.query(ImageModel).filter(
                ImageModel.storage_uuid == storage_uuid,
            ).delete(synchronize_session=False)
            db.query(ProjectModel).filter(
                ProjectModel.id.in_([project_a_id, project_b_id]),
            ).delete(synchronize_session=False)
            db.query(StoragePoolModel).filter(
                StoragePoolModel.name == f"image-project-pool-{suffix}",
            ).delete(synchronize_session=False)
            db.query(StorageModel).filter(
                StorageModel.uuid == storage_uuid,
            ).delete(synchronize_session=False)
            db.query(FlavorModel).filter(
                FlavorModel.name.in_([
                    f"image-project-flavor-a-{suffix}",
                    f"image-project-flavor-b-{suffix}",
                ]),
            ).delete(synchronize_session=False)
            db.query(NodeModel).filter(NodeModel.name == node_name).delete(
                synchronize_session=False,
            )
            db.query(UserModel).filter(UserModel.username == username).delete(
                synchronize_session=False,
            )
