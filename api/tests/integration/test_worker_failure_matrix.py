from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
from time import monotonic
from typing import Any, Literal, Never
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from domain import tasks as domain_tasks
from domain.models import DomainModel
from images import tasks as image_tasks
from mixin.database import SessionLocal
from module.ansiblelib import AnsibleRunResult
from module.backends import (
    FakeAnsibleBackend,
    FakeDownloadMetadataBackend,
    FakeLibvirtBackend,
    FakeSSHBackend,
)
from network.models import NetworkModel
from node import tasks as node_tasks
from node.models import AssociationNodeToRoleModel, NodeModel
from storage.models import ImageModel, StorageModel
from task.functions import TaskBase
from task.models import TaskModel
from task.schemas import TaskRequest
from user.models import UserModel
import worker as worker_module
from worker import exec_task, run_scheduler


pytestmark = [pytest.mark.integration, pytest.mark.timeout(30)]
FaultName = Literal[
    "ssh-timeout",
    "ansible-nonzero",
    "libvirt-exception",
    "download-metadata",
]


@dataclass(frozen=True)
class FaultSetup:
    task_manager: TaskBase
    request: TaskRequest
    resource: str
    object_name: str
    method: str
    expected_exception: str
    expected_message: str
    fault_calls: list[str]
    follow_up_calls: list[str]
    node_name: str
    domain_uuid: str
    storage_uuid: str


def _unexpected_call(
    call_name: str,
    calls: list[str],
) -> Callable[..., Never]:
    def unexpected(*_args: object, **_kwargs: object) -> Never:
        calls.append(call_name)
        raise AssertionError(f"障害後に{call_name}が呼ばれました")

    return unexpected


def _base_node(node_name: str) -> NodeModel:
    node = NodeModel(
        name=node_name,
        description="worker fault integration test",
        domain="no-network.invalid",
        user_name="fake-user",
        port=22,
        core=4,
        memory=8,
        cpu_gen="Virty Fake CPU",
        os_like="debian",
        os_name="Virty Fake Linux",
        os_version="1",
        status=10,
        ansible_facts={"virty_backend": "fake"},
    )
    node.qemu_version = None
    node.libvirt_version = None
    return node


def _prepare_fault(
    db: Session,
    monkeypatch: pytest.MonkeyPatch,
    fault_name: FaultName,
    suffix: str,
    private_marker: str,
) -> FaultSetup:
    node_name = f"fault-node-{suffix}"
    domain_uuid = str(uuid4())
    storage_uuid = str(uuid4())
    fault_calls: list[str] = []
    follow_up_calls: list[str] = []
    request_url = f"https://api.invalid/tasks?token={private_marker}"

    if fault_name == "ssh-timeout":
        ssh_backend = FakeSSHBackend(
            failures={"get_node_cpu_core": TimeoutError("SSH operation timed out")}
        )
        original_get_cpu_core = ssh_backend.get_node_cpu_core

        def fail_get_cpu_core() -> str:
            fault_calls.append("get_node_cpu_core")
            return original_get_cpu_core()

        monkeypatch.setattr(ssh_backend, "get_node_cpu_core", fail_get_cpu_core)
        for operation in (
            "get_node_mem",
            "get_node_cpu_name",
            "get_node_os_release",
        ):
            monkeypatch.setattr(
                ssh_backend,
                operation,
                _unexpected_call(operation, follow_up_calls),
            )
        monkeypatch.setattr(
            node_tasks,
            "create_ssh_backend",
            lambda **_kwargs: ssh_backend,
        )
        monkeypatch.setattr(
            node_tasks,
            "create_ansible_backend",
            lambda **_kwargs: FakeAnsibleBackend(),
        )
        request = TaskRequest(
            url=request_url,
            path_param={},
            body={
                "name": node_name,
                "description": private_marker,
                "domain": "no-network.invalid",
                "userName": "fake-user",
                "port": 22,
                "libvirtRole": False,
            },
        )
        return FaultSetup(
            task_manager=node_tasks.worker_task,
            request=request,
            resource="node",
            object_name="root",
            method="post",
            expected_exception="TimeoutError",
            expected_message="SSH operation timed out",
            fault_calls=fault_calls,
            follow_up_calls=follow_up_calls,
            node_name=node_name,
            domain_uuid=domain_uuid,
            storage_uuid=storage_uuid,
        )

    db.add(_base_node(node_name))

    if fault_name == "ansible-nonzero":
        ansible_backend = FakeAnsibleBackend(
            failures={"run": RuntimeError("Ansible returned nonzero rc=2")}
        )
        original_run = ansible_backend.run

        def fail_ansible_run(
            playbook_name: str,
            extravars: Mapping[str, Any] | None = None,
            timeout: int = 900,
        ) -> AnsibleRunResult:
            fault_calls.append("run")
            return original_run(playbook_name, extravars, timeout)

        monkeypatch.setattr(ansible_backend, "run", fail_ansible_run)
        monkeypatch.setattr(
            node_tasks,
            "create_ansible_backend",
            lambda **_kwargs: ansible_backend,
        )
        monkeypatch.setattr(
            node_tasks,
            "create_ssh_backend",
            _unexpected_call("create_ssh_backend", follow_up_calls),
        )
        monkeypatch.setattr(
            node_tasks,
            "create_storage",
            _unexpected_call("create_storage", follow_up_calls),
        )
        monkeypatch.setattr(
            node_tasks,
            "create_network",
            _unexpected_call("create_network", follow_up_calls),
        )
        request = TaskRequest(
            url=request_url,
            path_param={},
            body={
                "nodeName": node_name,
                "roleName": "libvirt",
                "extraJson": {"private": private_marker},
            },
        )
        return FaultSetup(
            task_manager=node_tasks.worker_task,
            request=request,
            resource="node",
            object_name="role",
            method="patch",
            expected_exception="RuntimeError",
            expected_message="Ansible returned nonzero rc=2",
            fault_calls=fault_calls,
            follow_up_calls=follow_up_calls,
            node_name=node_name,
            domain_uuid=domain_uuid,
            storage_uuid=storage_uuid,
        )

    if fault_name == "libvirt-exception":
        domain = DomainModel(
            uuid=domain_uuid,
            name=f"fault-vm-{suffix}",
            core=2,
            memory=2048,
            status=5,
            update_token="before-libvirt-failure",
            node_name=node_name,
        )
        domain.description = private_marker
        domain.owner_user_id = None
        domain.owner_project_id = None
        db.add(domain)
        libvirt_backend = FakeLibvirtBackend(
            failures={"domain_poweron": RuntimeError("libvirt operation failed")}
        )
        original_poweron = libvirt_backend.domain_poweron

        def fail_domain_poweron(uuid: str) -> None:
            fault_calls.append("domain_poweron")
            original_poweron(uuid)

        monkeypatch.setattr(libvirt_backend, "domain_poweron", fail_domain_poweron)
        monkeypatch.setattr(
            domain_tasks,
            "create_libvirt_backend",
            lambda **_kwargs: libvirt_backend,
        )
        request = TaskRequest(
            url=request_url,
            path_param={"uuid": domain_uuid},
            body={"status": "on"},
        )
        return FaultSetup(
            task_manager=domain_tasks.worker_task,
            request=request,
            resource="vm",
            object_name="power",
            method="patch",
            expected_exception="RuntimeError",
            expected_message="libvirt operation failed",
            fault_calls=fault_calls,
            follow_up_calls=follow_up_calls,
            node_name=node_name,
            domain_uuid=domain_uuid,
            storage_uuid=storage_uuid,
        )

    db.add(
        StorageModel(
            uuid=storage_uuid,
            name=f"fault-storage-{suffix}",
            node_name=node_name,
            capacity=1024,
            available=1024,
            path=f"/var/virty/fault-{suffix}",
            active=True,
            auto_start=True,
            status=1,
            update_token="before-download-failure",
        )
    )
    metadata_backend = FakeDownloadMetadataBackend(
        failures={"body_size": RuntimeError("download metadata failed")}
    )
    original_body_size = metadata_backend.body_size

    def fail_body_size(url: str, force_range: bool = False) -> int | None:
        fault_calls.append("body_size")
        return original_body_size(url, force_range)

    ansible_backend = FakeAnsibleBackend()
    monkeypatch.setattr(metadata_backend, "body_size", fail_body_size)
    monkeypatch.setattr(
        ansible_backend,
        "run",
        _unexpected_call("ansible.run", follow_up_calls),
    )
    monkeypatch.setattr(
        image_tasks,
        "create_download_metadata_backend",
        lambda: metadata_backend,
    )
    monkeypatch.setattr(
        image_tasks,
        "create_ansible_backend",
        lambda **_kwargs: ansible_backend,
    )
    monkeypatch.setattr(
        image_tasks,
        "storage_rescan",
        _unexpected_call("storage_rescan", follow_up_calls),
    )
    request = TaskRequest(
        url=request_url,
        path_param={},
        body={
            "storageUuid": storage_uuid,
            "imageUrl": f"https://no-network.invalid/{suffix}.qcow2",
        },
    )
    return FaultSetup(
        task_manager=image_tasks.worker_task,
        request=request,
        resource="image",
        object_name="download",
        method="post",
        expected_exception="RuntimeError",
        expected_message="download metadata failed",
        fault_calls=fault_calls,
        follow_up_calls=follow_up_calls,
        node_name=node_name,
        domain_uuid=domain_uuid,
        storage_uuid=storage_uuid,
    )


def _assert_no_product_mutation(
    db: Session,
    fault_name: FaultName,
    setup: FaultSetup,
) -> None:
    if fault_name == "ssh-timeout":
        assert (
            db.query(NodeModel).filter(NodeModel.name == setup.node_name).one_or_none()
            is None
        )
        return

    node = db.query(NodeModel).filter(NodeModel.name == setup.node_name).one()
    if fault_name == "ansible-nonzero":
        assert node.qemu_version is None
        assert node.libvirt_version is None
        assert (
            db.query(AssociationNodeToRoleModel)
            .filter(
                AssociationNodeToRoleModel.node_name == setup.node_name,
                AssociationNodeToRoleModel.role_name == "libvirt",
            )
            .one_or_none()
            is None
        )
        assert (
            db.query(StorageModel)
            .filter(StorageModel.node_name == setup.node_name)
            .count()
            == 0
        )
        assert (
            db.query(NetworkModel)
            .filter(NetworkModel.node_name == setup.node_name)
            .count()
            == 0
        )
        return

    if fault_name == "libvirt-exception":
        domain = (
            db.query(DomainModel)
            .filter(DomainModel.uuid == setup.domain_uuid)
            .one()
        )
        assert domain.status == 5
        assert domain.update_token == "before-libvirt-failure"
        return

    assert (
        db.query(ImageModel)
        .filter(ImageModel.storage_uuid == setup.storage_uuid)
        .count()
        == 0
    )


@pytest.mark.parametrize(
    "fault_name",
    [
        "ssh-timeout",
        "ansible-nonzero",
        "libvirt-exception",
        "download-metadata",
    ],
)
def test_production_worker_handlers_record_fault_and_block_dependency(
    monkeypatch: pytest.MonkeyPatch,
    fault_name: FaultName,
) -> None:
    suffix = uuid4().hex
    username = f"fault-matrix-{suffix}"
    private_marker = f"private-{suffix}"
    parent_uuid = str(uuid4())
    dependent_uuid = str(uuid4())
    sentinel_calls: list[str] = []
    setup: FaultSetup | None = None

    try:
        # Composeの別processで動くworkerには拾わせず、このprocessだけでfaultを注入する。
        monkeypatch.setattr(
            worker_module,
            "QUEUED_STATUSES",
            frozenset({*worker_module.QUEUED_STATUSES, "test"}),
        )
        with SessionLocal.begin() as db:
            db.add(UserModel(username=username, hashed_password="test-only"))
            db.flush()
            setup = _prepare_fault(
                db=db,
                monkeypatch=monkeypatch,
                fault_name=fault_name,
                suffix=suffix,
                private_marker=private_marker,
            )
            db.add(
                TaskModel(
                    uuid=parent_uuid,
                    post_time=datetime.now().astimezone(),
                    user_id=username,
                    status="test",
                    resource=setup.resource,
                    object=setup.object_name,
                    method=setup.method,
                    request=setup.request.model_dump_json(),
                )
            )

        task_manager = TaskBase()
        task_manager.include_task(setup.task_manager)
        sentinel_key = f"post.sentinel.{fault_name}"

        @task_manager(key=sentinel_key)
        def dependent_sentinel(
            db: Session,
            model: TaskModel,
            req: TaskRequest,
        ) -> None:
            del db, model, req
            sentinel_calls.append(dependent_uuid)

        started_at = monotonic()
        exec_task(task_manager=task_manager, task_uuid=parent_uuid)
        assert monotonic() - started_at < 30

        with SessionLocal.begin() as db:
            parent = db.query(TaskModel).filter(TaskModel.uuid == parent_uuid).one()
            assert parent.status == "error"
            assert parent.message == setup.expected_message
            assert parent.log is not None
            assert setup.expected_exception in parent.log
            assert setup.expected_message in parent.log
            assert private_marker not in parent.message
            assert private_marker not in parent.log
            _assert_no_product_mutation(db, fault_name, setup)

            dependent = TaskModel(
                uuid=dependent_uuid,
                post_time=datetime.now().astimezone(),
                user_id=username,
                status="wait",
                resource="sentinel",
                object=fault_name,
                method="post",
                request=TaskRequest(path_param={}, body={}).model_dump_json(),
            )
            dependent.dependence_uuid = parent_uuid
            db.add(dependent)

        run_scheduler(task_manager=task_manager)

        with SessionLocal() as db:
            dependent = (
                db.query(TaskModel)
                .filter(TaskModel.uuid == dependent_uuid)
                .one()
            )
            assert dependent.status == "error"
            assert dependent.message == "依存先taskが失敗しました"
            _assert_no_product_mutation(db, fault_name, setup)

        assert setup.fault_calls == [
            {
                "ssh-timeout": "get_node_cpu_core",
                "ansible-nonzero": "run",
                "libvirt-exception": "domain_poweron",
                "download-metadata": "body_size",
            }[fault_name]
        ]
        assert setup.follow_up_calls == []
        assert sentinel_calls == []
    finally:
        with SessionLocal.begin() as db:
            db.query(TaskModel).filter(TaskModel.user_id == username).delete(
                synchronize_session=False
            )
            if setup is not None:
                db.query(ImageModel).filter(
                    ImageModel.storage_uuid == setup.storage_uuid
                ).delete(synchronize_session=False)
                db.query(DomainModel).filter(
                    DomainModel.uuid == setup.domain_uuid
                ).delete(synchronize_session=False)
                db.query(StorageModel).filter(
                    StorageModel.uuid == setup.storage_uuid
                ).delete(synchronize_session=False)
                db.query(NetworkModel).filter(
                    NetworkModel.node_name == setup.node_name
                ).delete(synchronize_session=False)
                db.query(AssociationNodeToRoleModel).filter(
                    AssociationNodeToRoleModel.node_name == setup.node_name
                ).delete(synchronize_session=False)
                db.query(NodeModel).filter(
                    NodeModel.name == setup.node_name
                ).delete(synchronize_session=False)
            db.query(UserModel).filter(UserModel.username == username).delete(
                synchronize_session=False
            )
