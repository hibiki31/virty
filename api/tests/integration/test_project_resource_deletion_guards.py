from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from auth.router import create_access_token
from domain.models import DomainDriveModel, DomainInterfaceModel, DomainModel
from images import tasks as image_tasks
from mixin.database import SessionLocal
from network.models import NetworkModel, NetworkPoolModel, NetworkPortgroupModel
from network import tasks as network_tasks
from node.models import NodeModel
from project.models import ProjectModel
from storage.models import (
    AssociationStoragePoolModel,
    ImageModel,
    StorageModel,
    StoragePoolModel,
)
from storage import tasks as storage_tasks
from task.models import TaskModel
from task.schemas import TaskRequest
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


def test_shared_resource_delete_is_rejected_before_task_enqueue(
    api_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    suffix = uuid4().hex
    admin_name = f"resource-delete-admin-{suffix}"
    victim_name = f"resource-delete-victim-{suffix}"
    project_a_id = suffix[:6]
    project_b_id = suffix[6:12]
    node_name = f"resource-delete-node-{suffix}"
    storage_uuid = f"resource-delete-storage-{suffix}"
    network_uuid = str(uuid4())
    port_name = "tenant-a"
    domain_uuid = str(uuid4())
    image_name = f"install-{suffix}.iso"
    image_path = f"/shared/{suffix}/{image_name}"
    storage_pool_name = f"resource-delete-storage-pool-{suffix}"
    network_pool_name = f"resource-delete-network-pool-{suffix}"

    try:
        with SessionLocal.begin() as db:
            admin = UserModel(username=admin_name, hashed_password="unused")
            victim = UserModel(username=victim_name, hashed_password="unused")
            db.add_all([
                admin,
                victim,
                UserScopeModel(user_id=admin_name, name="admin"),
            ])
            node = NodeModel(
                name=node_name,
                description="Project resource deletion guard test",
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
                path=f"/shared/{suffix}",
                active=True,
                auto_start=True,
                status=2,
                update_token=suffix,
            )
            storage_pool = StoragePoolModel(
                name=storage_pool_name,
                storages=[AssociationStoragePoolModel(storage=storage)],
            )
            network = NetworkModel(
                uuid=network_uuid,
                name=f"network-{suffix}",
                node_name=node_name,
                bridge=f"virbr-{suffix[:8]}",
                type="openvswitch",
                active=True,
                auto_start=True,
                update_token=suffix,
            )
            port = NetworkPortgroupModel(
                network=network,
                name=port_name,
                is_default=False,
                update_token=suffix,
            )
            network_pool = NetworkPoolModel(
                name=network_pool_name,
                ports=[port],
            )
            project_a = ProjectModel(
                id=project_a_id,
                name=f"resource-delete-a-{suffix}",
                users=[admin],
                storage_pools=[storage_pool],
                network_pools=[network_pool],
            )
            project_b = ProjectModel(
                id=project_b_id,
                name=f"resource-delete-b-{suffix}",
                users=[victim],
                storage_pools=[storage_pool],
                network_pools=[network_pool],
            )
            disk = DomainDriveModel(
                target="vda",
                device="disk",
                type="file",
                update_token=suffix,
            )
            disk.source = image_path
            cdrom = DomainDriveModel(
                target="hda",
                device="cdrom",
                type="file",
                update_token=suffix,
            )
            cdrom.source = image_path
            interface = DomainInterfaceModel(
                mac="52:54:00:00:00:01",
                type="network",
                update_token=suffix,
            )
            interface.network = network.name
            interface.port = port_name
            domain = DomainModel(
                uuid=domain_uuid,
                name=f"vm-{suffix}",
                core=1,
                memory=1024,
                status=5,
                update_token=suffix,
                node_name=node_name,
                drives=[disk, cdrom],
                interfaces=[interface],
            )
            domain.owner_project_id = project_b_id
            image = ImageModel(
                name=image_name,
                storage=storage,
                capacity=128,
                allocation=128,
                path=image_path,
                update_token=suffix,
            )
            image.domain_uuid = domain_uuid
            db.add_all([node, project_a, project_b, domain, image])

        member_headers = _headers(
            admin_name,
            scopes=["storage.manage", "image.manage", "network.manage"],
            projects=[project_a_id],
        )
        storage_requires_admin = api_client.delete(
            f"/api/tasks/storages/{storage_uuid}",
            headers=member_headers,
        )
        assert storage_requires_admin.status_code == 403

        admin_headers = _headers(
            admin_name,
            scopes=["admin", "storage.manage", "image.manage", "network.manage"],
            projects=[project_a_id],
        )
        with SessionLocal() as db:
            task_count = db.query(TaskModel).filter(
                TaskModel.user_id == admin_name,
            ).count()

        responses = [
            api_client.delete(
                f"/api/tasks/storages/{storage_uuid}/images/{image_name}",
                headers=admin_headers,
            ),
            api_client.delete(
                f"/api/tasks/storages/{storage_uuid}",
                headers=admin_headers,
            ),
            api_client.delete(
                f"/api/tasks/networks/{network_uuid}/ovs/{port_name}",
                headers=admin_headers,
            ),
            api_client.delete(
                f"/api/tasks/networks/{network_uuid}",
                headers=admin_headers,
            ),
        ]
        assert [response.status_code for response in responses] == [409, 409, 409, 409]

        with SessionLocal() as db:
            assert db.query(TaskModel).filter(
                TaskModel.user_id == admin_name,
            ).count() == task_count
            assert db.get(StorageModel, storage_uuid) is not None
            assert db.get(NetworkModel, network_uuid) is not None
            assert db.query(ImageModel).filter(
                ImageModel.storage_uuid == storage_uuid,
                ImageModel.name == image_name,
            ).one_or_none() is not None

        backend_calls: list[str] = []

        def unexpected_backend(**_kwargs: object) -> None:
            backend_calls.append("create_libvirt_backend")
            raise AssertionError("依存検査後にlibvirt backendが呼ばれました")

        monkeypatch.setattr(
            storage_tasks,
            "create_libvirt_backend",
            unexpected_backend,
        )
        monkeypatch.setattr(
            image_tasks,
            "create_libvirt_backend",
            unexpected_backend,
        )
        monkeypatch.setattr(
            network_tasks,
            "create_libvirt_backend",
            unexpected_backend,
        )
        worker_cases = [
            (
                storage_tasks.delete_storage_root,
                "storage",
                "root",
                {"uuid": storage_uuid},
            ),
            (
                image_tasks.delete_image_root,
                "image",
                "root",
                {"uuid": storage_uuid, "name": image_name},
            ),
            (
                network_tasks.delete_network_ovs,
                "network",
                "ovs",
                {"uuid": network_uuid, "name": port_name},
            ),
            (
                network_tasks.delete_network_root,
                "network",
                "root",
                {"uuid": network_uuid},
            ),
        ]
        for handler, resource, object_name, path_param in worker_cases:
            task_request = TaskRequest(path_param=path_param, body={})
            worker_model = TaskModel(
                uuid=str(uuid4()),
                post_time=datetime.now().astimezone(),
                status="start",
                resource=resource,
                object=object_name,
                method="delete",
                request=task_request.model_dump_json(),
            )
            with SessionLocal.begin() as db:
                with pytest.raises(ValueError, match="削除できません"):
                    handler(
                        db,
                        worker_model,
                        task_request,
                    )
        assert backend_calls == []
    finally:
        with SessionLocal.begin() as db:
            db.query(DomainModel).filter(DomainModel.uuid == domain_uuid).delete(
                synchronize_session=False,
            )
            db.query(ImageModel).filter(ImageModel.storage_uuid == storage_uuid).delete(
                synchronize_session=False,
            )
            db.query(ProjectModel).filter(
                ProjectModel.id.in_([project_a_id, project_b_id]),
            ).delete(synchronize_session=False)
            db.query(StoragePoolModel).filter(
                StoragePoolModel.name == storage_pool_name,
            ).delete(synchronize_session=False)
            db.query(NetworkPoolModel).filter(
                NetworkPoolModel.name == network_pool_name,
            ).delete(synchronize_session=False)
            db.query(NetworkPortgroupModel).filter(
                NetworkPortgroupModel.network_uuid == network_uuid,
            ).delete(synchronize_session=False)
            db.query(StorageModel).filter(StorageModel.uuid == storage_uuid).delete(
                synchronize_session=False,
            )
            db.query(NetworkModel).filter(NetworkModel.uuid == network_uuid).delete(
                synchronize_session=False,
            )
            db.query(NodeModel).filter(NodeModel.name == node_name).delete(
                synchronize_session=False,
            )
            db.query(UserModel).filter(
                UserModel.username.in_([admin_name, victim_name]),
            ).delete(synchronize_session=False)
