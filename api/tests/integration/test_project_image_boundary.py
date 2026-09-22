from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from auth.router import CurrentUser, create_access_token
from domain import tasks as domain_tasks
from domain import router_task as domain_router_task
from domain.authorization import DomainTaskAuthorizationError
from domain.models import DomainDriveModel, DomainModel
from domain.schemas import CdromForUpdateDomain
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


def _headers(
    username: str,
    project_ids: list[str],
    *,
    admin: bool = False,
) -> dict[str, str]:
    token = create_access_token(
        data={
            "sub": username,
            "scopes": [
                "user",
                "image.read",
                "image.manage",
                "vm.create",
                "vm.attach",
            ] + (["admin"] if admin else []),
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
            db.add(
                DomainDriveModel(
                    domain_uuid=domain_uuid,
                    target="sda",
                    device="cdrom",
                    type="file",
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
        assert denied_copy.json()["detail"]["code"] == "image_not_found"

        denied_cdrom = api_client.patch(
            f"/api/tasks/vms/{domain_uuid}/cdrom",
            headers=headers,
            json={"target": "sda", "path": cross_path},
        )
        assert denied_cdrom.status_code == 404
        assert denied_cdrom.json()["detail"]["code"] == "cdrom_image_not_found"

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

        denied_admin = api_client.patch(
            f"/api/tasks/vms/{domain_uuid}/cdrom",
            headers=headers,
            params={"admin": "true"},
            json={"target": "sda", "path": cross_path},
        )
        assert denied_admin.status_code == 403

        with SessionLocal.begin() as db:
            db.add(UserScopeModel(user_id=username, name="admin"))
        admin_headers = _headers(username, [project_a_id, project_b_id], admin=True)
        admin_images = api_client.get(
            "/api/images",
            headers=admin_headers,
            params={"admin": "true", "nodeName": node_name, "limit": 100},
        )
        assert admin_images.status_code == 200, admin_images.text
        assert cross_name in {image["name"] for image in admin_images.json()["data"]}

        captured_tasks: list[TaskModel] = []

        class CapturedTaskManager:
            def __init__(self, db: Session) -> None:
                self.method = ""
                self.resource = ""
                self.object = ""
                self._model: TaskModel | None = None

            @property
            def model(self) -> TaskModel:
                assert self._model is not None
                return self._model

            def select(self, method: str, resource: str, object: str) -> None:
                self.method = method
                self.resource = resource
                self.object = object

            def commit(
                self,
                user: CurrentUser,
                req: object,
                body: CdromForUpdateDomain,
                param: dict[str, Any] | None = None,
                dep_uuid: str | None = None,
            ) -> TaskModel:
                request = TaskRequest(
                    path_param=param or {},
                    body=body.model_dump(mode="json", by_alias=True),
                )
                self._model = TaskModel(
                    uuid=str(uuid4()),
                    post_time=datetime.now().astimezone(),
                    user_id=user.id,
                    status="wait",
                    resource=self.resource,
                    object=self.object,
                    method=self.method,
                    request=request.model_dump_json(),
                    dependence_uuid=dep_uuid,
                )
                captured_tasks.append(self._model)
                return self._model

        monkeypatch.setattr(domain_router_task, "TaskManager", CapturedTaskManager)
        admin_cdrom = api_client.patch(
            f"/api/tasks/vms/{domain_uuid}/cdrom",
            headers=admin_headers,
            params={"admin": "true"},
            json={"target": "sda", "path": cross_path},
        )
        assert admin_cdrom.status_code == 200, admin_cdrom.text
        admin_task = captured_tasks[0]
        assert admin_task.uuid == admin_cdrom.json()[0]["uuid"]
        admin_request = TaskRequest.model_validate_json(admin_task.request)
        assert admin_request.path_param["ownerBinding"]["admin"] is True

        class CdromBackend:
            def domain_cdrom(self, uuid: str, target: str, path: str | None = None) -> None:
                backend_calls.append(f"{uuid}:{target}:{path}")

        monkeypatch.setattr(
            domain_tasks,
            "create_libvirt_backend",
            lambda node_model: CdromBackend(),
        )
        with SessionLocal.begin() as db:
            db.query(UserScopeModel).filter(
                UserScopeModel.user_id == username,
                UserScopeModel.name == "admin",
            ).delete(synchronize_session=False)
        with SessionLocal.begin() as db:
            with pytest.raises(DomainTaskAuthorizationError, match="管理者権限"):
                domain_tasks.patch_vm_cdrom(db, admin_task, admin_request)
        assert backend_calls == []

        with SessionLocal.begin() as db:
            db.add(UserScopeModel(user_id=username, name="admin"))
        with SessionLocal.begin() as db:
            domain_tasks.patch_vm_cdrom(db, admin_task, admin_request)
        assert backend_calls == [f"{domain_uuid}:sda:{cross_path}"]

        # 旧VMのowner未設定を再現し、受付からworkerまで管理用操作を検証する。
        with SessionLocal.begin() as db:
            domain = db.get(DomainModel, domain_uuid)
            assert domain is not None
            domain.owner_project_id = None
        for path in (cross_path, None):
            backend_calls.clear()
            for request_headers, params, status in (
                (admin_headers, {}, 404),
                (headers, {"admin": "true"}, 403),
            ):
                denied = api_client.patch(
                    f"/api/tasks/vms/{domain_uuid}/cdrom",
                    headers=request_headers,
                    params=params,
                    json={"target": "sda", "path": path},
                )
                assert denied.status_code == status, denied.text

            captured_tasks.clear()
            accepted = api_client.patch(
                f"/api/tasks/vms/{domain_uuid}/cdrom",
                headers=admin_headers,
                params={"admin": "true"},
                json={"target": "sda", "path": path},
            )
            assert accepted.status_code == 200, accepted.text
            ownerless_task = captured_tasks[0]
            ownerless_request = TaskRequest.model_validate_json(ownerless_task.request)
            assert ownerless_request.path_param["ownerBinding"] == {
                "principalId": username,
                "ownerUserId": None,
                "ownerProjectId": None,
                "admin": True,
            }

            # 受付後のowner割り当ては、個人・Projectのどちらも副作用前に拒否する。
            for owner_field, owner_id in (
                ("owner_user_id", username),
                ("owner_project_id", project_a_id),
            ):
                with SessionLocal.begin() as db:
                    domain = db.get(DomainModel, domain_uuid)
                    assert domain is not None
                    setattr(domain, owner_field, owner_id)
                with SessionLocal.begin() as db:
                    with pytest.raises(DomainTaskAuthorizationError, match="VM ownerがtask受付時から変更"):
                        domain_tasks.patch_vm_cdrom(db, ownerless_task, ownerless_request)
                assert backend_calls == []
                with SessionLocal.begin() as db:
                    domain = db.get(DomainModel, domain_uuid)
                    assert domain is not None
                    setattr(domain, owner_field, None)

            with SessionLocal.begin() as db:
                db.query(UserScopeModel).filter(
                    UserScopeModel.user_id == username,
                    UserScopeModel.name == "admin",
                ).delete(synchronize_session=False)
            with SessionLocal.begin() as db:
                with pytest.raises(DomainTaskAuthorizationError, match="管理者権限"):
                    domain_tasks.patch_vm_cdrom(db, ownerless_task, ownerless_request)
            assert backend_calls == []
            with SessionLocal.begin() as db:
                db.add(UserScopeModel(user_id=username, name="admin"))
            with SessionLocal.begin() as db:
                domain_tasks.patch_vm_cdrom(db, ownerless_task, ownerless_request)
            assert backend_calls == [f"{domain_uuid}:sda:{path}"]

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
