from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from threading import Event
from typing import Any, Callable
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from domain import tasks as domain_tasks
from domain.authorization import (
    DomainTaskAuthorizationError,
    domain_task_path_param,
)
from domain.models import DomainDriveModel, DomainModel
from domain.service import (
    DomainProjectMoveConflictError,
    lock_domain_owner_context,
    move_domain_to_project,
)
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
from user.models import UserModel


pytestmark = [pytest.mark.integration, pytest.mark.timeout(60)]


def _node(name: str) -> NodeModel:
    return NodeModel(
        name=name,
        description="VM Project move locking test",
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


def _rest_task(
    *,
    username: str,
    object_name: str,
    method: str,
    request: TaskRequest,
) -> TaskModel:
    return TaskModel(
        uuid=str(uuid4()),
        post_time=datetime.now().astimezone(),
        user_id=username,
        status="start",
        resource="vm",
        object=object_name,
        method=method,
        request=request.model_dump_json(),
    )


@pytest.mark.parametrize(
    ("handler", "object_name", "method", "body"),
    [
        (domain_tasks.delete_vm_root, "root", "delete", {}),
        (domain_tasks.patch_vm_root, "power", "patch", {"status": "on"}),
        (
            domain_tasks.patch_vm_cdrom,
            "cdrom",
            "patch",
            {"target": "sda", "path": None},
        ),
        (
            domain_tasks.patch_vm_network,
            "network",
            "patch",
            {
                "mac": "52:54:00:00:00:01",
                "networkUuid": "not-used-after-owner-check",
                "port": None,
            },
        ),
    ],
)
def test_queued_rest_vm_mutation_rejects_owner_changed_by_move(
    monkeypatch: pytest.MonkeyPatch,
    handler: Callable[[Session, TaskModel, TaskRequest], Any],
    object_name: str,
    method: str,
    body: dict[str, Any],
) -> None:
    suffix = uuid4().hex
    username = f"queued-move-user-{suffix}"
    source_project_id = suffix[:6]
    destination_project_id = suffix[6:12]
    node_name = f"queued-move-node-{suffix}"
    domain_uuid = str(uuid4())
    backend_calls: list[str] = []

    def unexpected_backend(**_kwargs: object) -> None:
        backend_calls.append("create_libvirt_backend")
        raise AssertionError("owner再認可より先にbackendが呼ばれました")

    monkeypatch.setattr(
        domain_tasks,
        "create_libvirt_backend",
        unexpected_backend,
    )

    try:
        with SessionLocal.begin() as db:
            user = UserModel(username=username, hashed_password="unused")
            source = ProjectModel(
                id=source_project_id,
                name=f"queued-move-source-{suffix}",
                users=[user],
            )
            destination = ProjectModel(
                id=destination_project_id,
                name=f"queued-move-destination-{suffix}",
                users=[user],
            )
            node = _node(node_name)
            domain = DomainModel(
                uuid=domain_uuid,
                name=f"queued-move-vm-{suffix}",
                core=1,
                memory=1024,
                status=5,
                node=node,
                owner_project=source,
                update_token=suffix,
            )
            db.add_all([source, destination, node, domain])
            db.flush()
            path_param = domain_task_path_param(domain, username)

        with SessionLocal.begin() as db:
            move_domain_to_project(
                db,
                domain_uuid=domain_uuid,
                destination_project_id=destination_project_id,
            )

        request = TaskRequest(path_param=path_param, body=body)
        task = _rest_task(
            username=username,
            object_name=object_name,
            method=method,
            request=request,
        )
        with SessionLocal.begin() as db:
            with pytest.raises(
                DomainTaskAuthorizationError,
                match="VM ownerがtask受付時から変更",
            ):
                handler(db, task, request)

        assert backend_calls == []
    finally:
        with SessionLocal.begin() as db:
            db.query(DomainModel).filter(DomainModel.uuid == domain_uuid).delete()
            db.query(ProjectModel).filter(ProjectModel.id.in_([
                source_project_id,
                destination_project_id,
            ])).delete(synchronize_session=False)
            db.query(NodeModel).filter(NodeModel.name == node_name).delete()
            db.query(UserModel).filter(UserModel.username == username).delete()


def test_queued_rest_vm_mutation_rechecks_membership_and_personal_owner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    suffix = uuid4().hex
    username = f"queued-auth-user-{suffix}"
    replacement_username = f"queued-auth-replacement-{suffix}"
    project_id = suffix[:6]
    node_name = f"queued-auth-node-{suffix}"
    project_domain_uuid = str(uuid4())
    personal_domain_uuid = str(uuid4())
    backend_calls: list[str] = []

    def unexpected_backend(**_kwargs: object) -> None:
        backend_calls.append("create_libvirt_backend")
        raise AssertionError("owner再認可より先にbackendが呼ばれました")

    monkeypatch.setattr(
        domain_tasks,
        "create_libvirt_backend",
        unexpected_backend,
    )

    try:
        with SessionLocal.begin() as db:
            user = UserModel(username=username, hashed_password="unused")
            replacement = UserModel(
                username=replacement_username,
                hashed_password="unused",
            )
            project = ProjectModel(
                id=project_id,
                name=f"queued-auth-project-{suffix}",
                users=[user, replacement],
            )
            node = _node(node_name)
            project_domain = DomainModel(
                uuid=project_domain_uuid,
                name=f"queued-auth-project-vm-{suffix}",
                core=1,
                memory=1024,
                status=5,
                node=node,
                owner_project=project,
                update_token=suffix,
            )
            personal_domain = DomainModel(
                uuid=personal_domain_uuid,
                name=f"queued-auth-personal-vm-{suffix}",
                core=1,
                memory=1024,
                status=5,
                node=node,
                owner_user=user,
                update_token=suffix,
            )
            db.add_all([project, node, project_domain, personal_domain])
            db.flush()
            project_path = domain_task_path_param(project_domain, username)
            personal_path = domain_task_path_param(personal_domain, username)

        with SessionLocal.begin() as db:
            persisted_project = db.get(ProjectModel, project_id)
            persisted_user = db.get(UserModel, username)
            assert persisted_project is not None and persisted_user is not None
            persisted_project.users.remove(persisted_user)
            personal = db.get(DomainModel, personal_domain_uuid)
            assert personal is not None
            personal.owner_user_id = replacement_username

        for path_param, expected_message in [
            (project_path, "membershipが失効"),
            (personal_path, "VM ownerがtask受付時から変更"),
        ]:
            request = TaskRequest(
                path_param=path_param,
                body={"status": "on"},
            )
            task = _rest_task(
                username=username,
                object_name="power",
                method="patch",
                request=request,
            )
            with SessionLocal.begin() as db:
                with pytest.raises(
                    DomainTaskAuthorizationError,
                    match=expected_message,
                ):
                    domain_tasks.patch_vm_root(db, task, request)

        assert backend_calls == []
    finally:
        with SessionLocal.begin() as db:
            db.query(DomainModel).filter(DomainModel.uuid.in_([
                project_domain_uuid,
                personal_domain_uuid,
            ])).delete(synchronize_session=False)
            db.query(ProjectModel).filter(ProjectModel.id == project_id).delete()
            db.query(NodeModel).filter(NodeModel.name == node_name).delete()
            db.query(UserModel).filter(UserModel.username.in_([
                username,
                replacement_username,
            ])).delete(synchronize_session=False)


def test_resource_change_reloads_project_after_concurrent_vm_move() -> None:
    suffix = uuid4().hex
    username = f"move-lock-user-{suffix}"
    source_project_id = suffix[:6]
    destination_project_id = suffix[6:12]
    node_name = f"move-lock-node-{suffix}"
    domain_uuid = str(uuid4())
    move_locked = Event()
    release_move = Event()
    resource_locked = Event()
    observed_project_id: list[str | None] = []

    try:
        with SessionLocal.begin() as db:
            user = UserModel(username=username, hashed_password="unused")
            source = ProjectModel(
                id=source_project_id,
                name=f"move-lock-source-{suffix}",
                users=[user],
            )
            destination = ProjectModel(
                id=destination_project_id,
                name=f"move-lock-destination-{suffix}",
                users=[user],
            )
            node = _node(node_name)
            db.add_all([source, destination, node])
            db.flush()
            db.add(DomainModel(
                uuid=domain_uuid,
                name=f"move-lock-vm-{suffix}",
                core=1,
                memory=1024,
                status=5,
                node=node,
                owner_project=source,
                update_token=suffix,
            ))

        def move_vm() -> None:
            with SessionLocal.begin() as db:
                def hold_move(_: DomainModel, __: ProjectModel) -> bool:
                    move_locked.set()
                    return release_move.wait(10)

                move_domain_to_project(
                    db,
                    domain_uuid=domain_uuid,
                    destination_project_id=destination_project_id,
                    authorize_locked=hold_move,
                )

        def lock_for_resource_change() -> None:
            with SessionLocal.begin() as db:
                domain = lock_domain_owner_context(db, domain_uuid)
                observed_project_id.append(domain.owner_project_id)
                resource_locked.set()

        with ThreadPoolExecutor(max_workers=2) as executor:
            move_future = executor.submit(move_vm)
            assert move_locked.wait(5), "VM moveがDomain/Project lockを取得しませんでした"
            resource_future = executor.submit(lock_for_resource_change)
            try:
                assert not resource_locked.wait(0.25), (
                    "resource変更が移動中のDomain lockを迂回しました"
                )
            finally:
                release_move.set()
            move_future.result(timeout=10)
            resource_future.result(timeout=10)

        assert observed_project_id == [destination_project_id]
    finally:
        release_move.set()
        with SessionLocal.begin() as db:
            db.query(DomainModel).filter(DomainModel.uuid == domain_uuid).delete()
            db.query(ProjectModel).filter(ProjectModel.id.in_([
                source_project_id,
                destination_project_id,
            ])).delete(synchronize_session=False)
            db.query(NodeModel).filter(NodeModel.name == node_name).delete()
            db.query(UserModel).filter(UserModel.username == username).delete()


def test_vm_move_rechecks_registered_image_flavor_grant() -> None:
    suffix = uuid4().hex
    username = f"move-flavor-user-{suffix}"
    source_project_id = suffix[:6]
    destination_project_id = suffix[6:12]
    node_name = f"move-flavor-node-{suffix}"
    domain_uuid = str(uuid4())
    storage_uuid = f"move-flavor-storage-{suffix}"
    image_name = f"move-flavor-{suffix}.qcow2"
    image_path = f"/tmp/move-flavor-{suffix}/{image_name}"

    try:
        with SessionLocal.begin() as db:
            user = UserModel(username=username, hashed_password="unused")
            node = _node(node_name)
            storage = StorageModel(
                uuid=storage_uuid,
                name=f"move-flavor-storage-{suffix}",
                node_name=node_name,
                capacity=1024,
                available=1024,
                path=f"/tmp/move-flavor-{suffix}",
                active=True,
                auto_start=True,
                status=10,
                update_token=suffix,
            )
            storage_pool = StoragePoolModel(
                name=f"move-flavor-pool-{suffix}",
                storages=[AssociationStoragePoolModel(storage=storage)],
            )
            flavor = _flavor(f"move-flavor-{suffix}")
            source = ProjectModel(
                id=source_project_id,
                name=f"move-flavor-source-{suffix}",
                users=[user],
                storage_pools=[storage_pool],
                flavors=[flavor],
            )
            destination = ProjectModel(
                id=destination_project_id,
                name=f"move-flavor-destination-{suffix}",
                users=[user],
                storage_pools=[storage_pool],
            )
            domain = DomainModel(
                uuid=domain_uuid,
                name=f"move-flavor-vm-{suffix}",
                core=1,
                memory=1024,
                status=5,
                node=node,
                owner_project=source,
                update_token=suffix,
            )
            drive = DomainDriveModel(
                target="vda",
                device="disk",
                type="file",
                update_token=suffix,
            )
            drive.source = image_path
            domain.drives = [drive]
            db.add_all([source, destination, node, domain])
            db.flush()
            image = ImageModel(
                name=image_name,
                storage=storage,
                capacity=64,
                allocation=8,
                path=image_path,
                update_token=suffix,
                flavor=flavor,
            )
            image.domain_uuid = domain_uuid
            db.add(image)
            db.flush()
            flavor_id = flavor.id

        with SessionLocal.begin() as db:
            with pytest.raises(DomainProjectMoveConflictError) as caught:
                move_domain_to_project(
                    db,
                    domain_uuid=domain_uuid,
                    destination_project_id=destination_project_id,
                )
            assert caught.value.conflicts == [f"flavor:{flavor_id}"]

        with SessionLocal() as db:
            persisted_domain = db.get(DomainModel, domain_uuid)
            assert persisted_domain is not None
            assert persisted_domain.owner_project_id == source_project_id
    finally:
        with SessionLocal.begin() as db:
            db.query(DomainModel).filter(DomainModel.uuid == domain_uuid).delete()
            db.query(ImageModel).filter(ImageModel.storage_uuid == storage_uuid).delete()
            db.query(ProjectModel).filter(ProjectModel.id.in_([
                source_project_id,
                destination_project_id,
            ])).delete(synchronize_session=False)
            db.query(StoragePoolModel).filter(
                StoragePoolModel.name == f"move-flavor-pool-{suffix}",
            ).delete()
            db.query(StorageModel).filter(StorageModel.uuid == storage_uuid).delete()
            db.query(FlavorModel).filter(
                FlavorModel.name == f"move-flavor-{suffix}",
            ).delete()
            db.query(NodeModel).filter(NodeModel.name == node_name).delete()
            db.query(UserModel).filter(UserModel.username == username).delete()
