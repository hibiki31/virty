from collections.abc import Iterator
from copy import deepcopy
from dataclasses import dataclass
from datetime import timedelta
from typing import Any
from unittest.mock import Mock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from auth.router import create_access_token
from domain import tasks as domain_tasks
from domain.models import DomainModel
from flavor.models import FlavorModel
from mixin.database import SessionLocal
from module.backends import FakeAnsibleBackend, FakeLibvirtBackend
from network.models import NetworkModel
from node.models import NodeModel
from storage.models import ImageModel, StorageModel
from task.functions import TaskManager
from task.models import TaskModel
from task.schemas import TaskRequest
from user.models import UserModel, UserScopeModel


pytestmark = [pytest.mark.integration, pytest.mark.timeout(60)]


@dataclass
class AdminVM:
    username: str
    body: dict[str, Any]
    other_storage: str
    other_network: str
    ansible: Mock
    libvirt: Mock

    def headers(self, scopes: list[str] | None = None) -> dict[str, str]:
        token = create_access_token(
            {"sub": self.username, "scopes": scopes or ["admin"], "projects": []},
            timedelta(minutes=5),
        )
        return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_vm(monkeypatch: pytest.MonkeyPatch) -> Iterator[AdminVM]:
    suffix = uuid4().hex
    username = f"admin-create-{suffix}"
    nodes = [f"admin-node-{suffix}-{index}" for index in range(2)]
    storages = [str(uuid4()) for _ in nodes]
    networks = [str(uuid4()) for _ in nodes]
    ansible = Mock(wraps=FakeAnsibleBackend())
    libvirt = Mock(wraps=FakeLibvirtBackend())
    monkeypatch.setattr(domain_tasks, "create_ansible_backend", lambda **_kwargs: ansible)
    monkeypatch.setattr(domain_tasks, "create_libvirt_backend", lambda **_kwargs: libvirt)
    original_commit = TaskManager.commit

    def hold_task(manager: TaskManager, *args: Any, **kwargs: Any) -> TaskModel:
        # 常駐verify workerとの競合を避け、登録済みhandlerをtest内で実行する。
        kwargs["commit_transaction"] = False
        task = original_commit(manager, *args, **kwargs)
        task.status = "test-held"
        manager.db.commit()
        return task

    monkeypatch.setattr(TaskManager, "commit", hold_task)
    try:
        with SessionLocal.begin() as db:
            db.add(UserModel(username=username, hashed_password="unused"))
            db.add(UserScopeModel(user_id=username, name="admin"))
            flavor = FlavorModel(
                name=username, os="linux", description="未grantのimage flavor",
                icon="linux", manual_url="https://unused.invalid", cloud_init_ready=False,
                cloud_init_user="unused",
            )
            db.add(flavor)
            for index, node_name in enumerate(nodes):
                db.add(NodeModel(
                    name=node_name, description="管理者用VM作成試験", domain="unused.invalid",
                    user_name="unused", port=22, core=4, memory=8192, cpu_gen="test",
                    os_like="debian", os_name="test", os_version="1", status=10, ansible_facts={},
                ))
                db.flush()
                db.add(StorageModel(
                    uuid=storages[index], name=node_name, node_name=node_name,
                    capacity=100, available=80, path=f"/images/{node_name}",
                    active=True, auto_start=True, status=2, update_token=suffix,
                ))
                db.add(NetworkModel(
                    uuid=networks[index], name=node_name, node_name=node_name,
                    type="bridge", bridge=f"br-{index}", active=True,
                    auto_start=True, update_token=suffix,
                ))
                db.flush()
                db.add(ImageModel(
                    name="source.qcow2", storage_uuid=storages[index],
                    path=f"/images/{node_name}/source.qcow2", capacity=4,
                    allocation=1, flavor=flavor, update_token=suffix,
                ))
        yield AdminVM(
            username=username,
            body={
                "type": "manual", "name": username, "nodeName": nodes[0],
                "memoryMegaByte": 2048, "cpu": 2,
                "disks": [{"type": "empty", "savePoolUuid": storages[0], "sizeGigaByte": 8}],
                "interface": [{"type": "network", "networkUuid": networks[0]}],
            },
            other_storage=storages[1], other_network=networks[1],
            ansible=ansible, libvirt=libvirt,
        )
    finally:
        with SessionLocal.begin() as db:
            db.query(TaskModel).filter(TaskModel.user_id == username).delete(synchronize_session=False)
            db.query(DomainModel).filter(DomainModel.node_name.in_(nodes)).delete(synchronize_session=False)
            db.query(ImageModel).filter(ImageModel.storage_uuid.in_(storages)).delete(synchronize_session=False)
            db.query(StorageModel).filter(StorageModel.uuid.in_(storages)).delete(synchronize_session=False)
            db.query(NetworkModel).filter(NetworkModel.uuid.in_(networks)).delete(synchronize_session=False)
            db.query(NodeModel).filter(NodeModel.name.in_(nodes)).delete(synchronize_session=False)
            db.query(FlavorModel).filter(FlavorModel.name == username).delete(synchronize_session=False)
            db.query(UserModel).filter(UserModel.username == username).delete(synchronize_session=False)


@pytest.mark.parametrize("disk_type", ["empty", "copy"])
def test_admin_create_without_project_runs_registered_worker_and_preserves_owner(
    api_client: TestClient, admin_vm: AdminVM, disk_type: str,
) -> None:
    body = deepcopy(admin_vm.body)
    if disk_type == "copy":
        body["disks"][0].update({
            "type": "copy", "originalPoolUuid": body["disks"][0]["savePoolUuid"],
            "originalName": "source.qcow2",
        })
    response = api_client.post("/api/tasks/vms/admin", headers=admin_vm.headers(), json=body)
    assert response.status_code == 200, response.text
    tasks = response.json()
    assert len(tasks) == 3
    assert tasks[0]["object"] == "admin"
    # 返却順の互換性を保ち、VM集計だけはdisk inventoryの確定後に実行する。
    assert tasks[1]["resource"] == "vm"
    assert tasks[2]["resource"] == "storage"
    assert tasks[2]["dependenceUuid"] == tasks[0]["uuid"]
    assert tasks[1]["dependenceUuid"] == tasks[2]["uuid"]
    domain_tasks.worker_task.run("post.vm.admin", tasks[0]["uuid"])
    with SessionLocal() as db:
        domain = db.query(DomainModel).filter(DomainModel.name == body["name"]).one()
        assert domain.owner_user_id == admin_vm.username
        assert domain.owner_project_id is None
    admin_vm.libvirt.domain_define.assert_called_once()
    expected = "commom/copy_node_internal" if disk_type == "copy" else "vms/qemu_image_create"
    assert admin_vm.ansible.run.call_args_list[0].kwargs["playbook_name"] == expected


def test_admin_create_keeps_token_database_and_project_boundaries(
    api_client: TestClient, admin_vm: AdminVM,
) -> None:
    body = admin_vm.body
    path = "/api/tasks/vms/admin"
    assert api_client.post(path, json=body).status_code == 401
    assert api_client.post(path, headers=admin_vm.headers(["vm.create"]), json=body).status_code == 403
    with SessionLocal.begin() as db:
        db.query(UserScopeModel).filter(UserScopeModel.user_id == admin_vm.username).update({"name": "vm.create"})
    assert api_client.post(path, headers=admin_vm.headers(), json=body).status_code == 403
    with SessionLocal.begin() as db:
        db.query(UserScopeModel).filter(UserScopeModel.user_id == admin_vm.username).update({"name": "admin"})
    assert api_client.post(path, headers=admin_vm.headers(), json={**body, "projectId": "a1b2c3"}).status_code == 422
    assert api_client.post("/api/tasks/vms", headers=admin_vm.headers(), json=body).status_code == 422
    assert api_client.post("/api/tasks/vms", headers=admin_vm.headers(), json={**body, "projectId": "a1b2c3"}).status_code == 404
    with SessionLocal() as db:
        assert db.query(TaskModel).filter(TaskModel.user_id == admin_vm.username).count() == 0


@pytest.mark.parametrize("invalid", ["node", "storage", "network", "source", "missing-source"])
def test_admin_create_validates_resources_before_queueing(
    api_client: TestClient, admin_vm: AdminVM, invalid: str,
) -> None:
    body = deepcopy(admin_vm.body)
    if invalid == "node":
        body["nodeName"] = "missing-node"
    elif invalid == "storage":
        body["disks"][0]["savePoolUuid"] = admin_vm.other_storage
    elif invalid == "network":
        body["interface"][0]["networkUuid"] = admin_vm.other_network
    else:
        body["disks"][0].update({"type": "copy", "originalPoolUuid": admin_vm.other_storage})
        if invalid == "source":
            body["disks"][0]["originalName"] = "source.qcow2"
    response = api_client.post("/api/tasks/vms/admin", headers=admin_vm.headers(), json=body)
    assert response.status_code in {400, 404}, response.text
    with SessionLocal() as db:
        assert db.query(TaskModel).filter(TaskModel.user_id == admin_vm.username).count() == 0


@pytest.mark.parametrize("change", ["revoke", "network-node", "storage-node", "source-node"])
def test_admin_worker_rechecks_authorization_and_resources_before_side_effects(
    api_client: TestClient, admin_vm: AdminVM, change: str,
) -> None:
    body = deepcopy(admin_vm.body)
    if change == "source-node":
        body["disks"][0].update({
            "type": "copy", "originalPoolUuid": body["disks"][0]["savePoolUuid"],
            "originalName": "source.qcow2",
        })
    response = api_client.post("/api/tasks/vms/admin", headers=admin_vm.headers(), json=body)
    assert response.status_code == 200, response.text
    task_id = response.json()[0]["uuid"]
    with SessionLocal.begin() as db:
        if change == "revoke":
            db.query(UserScopeModel).filter(UserScopeModel.user_id == admin_vm.username).delete()
        elif change == "network-node":
            db.query(NetworkModel).filter(NetworkModel.uuid == body["interface"][0]["networkUuid"]).update({"node_name": None})
        elif change == "storage-node":
            db.query(StorageModel).filter(StorageModel.uuid == body["disks"][0]["savePoolUuid"]).update({"node_name": None})
        else:
            db.query(ImageModel).filter(ImageModel.storage_uuid == body["disks"][0]["savePoolUuid"]).update({"storage_uuid": admin_vm.other_storage, "name": "moved.qcow2"})
    with pytest.raises(ValueError):
        domain_tasks.worker_task.run("post.vm.admin", task_id)
    admin_vm.ansible.run.assert_not_called()
    admin_vm.libvirt.domain_define.assert_not_called()


def test_admin_worker_rejects_agent_tasks(admin_vm: AdminVM) -> None:
    with SessionLocal() as db, pytest.raises(ValueError, match="Agent task"):
        domain_tasks.post_vm_admin(
            db, TaskModel(user_id=admin_vm.username, idempotency_key="agent-task"),
            TaskRequest(path_param={}, body=admin_vm.body),
        )
    admin_vm.ansible.run.assert_not_called()
