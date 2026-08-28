from queue import Queue
from threading import Event, Thread
from uuid import uuid4

import pytest

from mixin.database import SessionLocal
from project.models import ProjectModel
from project.schemas import ProjectResourceGrantsUpdate
from project.service import (
    ProjectConflictError,
    lock_project,
    remove_project_member,
    replace_project_resource_grants,
)
from storage.models import StoragePoolModel
from user.models import UserModel


pytestmark = [pytest.mark.integration, pytest.mark.timeout(60)]


def _join(thread: Thread) -> None:
    thread.join(timeout=10)
    assert not thread.is_alive(), "Project row lockの待機が完了しませんでした"


def test_project_lock_refreshes_members_and_grants_before_mutation() -> None:
    suffix = uuid4().hex
    project_id = suffix[:6]
    usernames = [f"project-race-{index}-{suffix}" for index in range(2)]
    pool_names = [f"project-race-pool-{index}-{suffix}" for index in range(3)]
    pool_ids: list[int] = []

    try:
        with SessionLocal.begin() as db:
            users = [
                UserModel(username=username, hashed_password="unused")
                for username in usernames
            ]
            pools = [StoragePoolModel(name=name) for name in pool_names]
            project = ProjectModel(
                id=project_id,
                name=f"project-race-{suffix}",
                users=users,
                storage_pools=[pools[0]],
            )
            db.add_all([project, *pools[1:]])
            db.flush()
            pool_ids = [pool.id for pool in pools]

        # 両transactionが2名を読んだ後でも、後発はlock取得後の1名を見て
        # 最後のmember削除を拒否しなければならない。
        member_ready = Event()
        member_result: Queue[str] = Queue()

        with SessionLocal() as first_db:
            first_project = first_db.get(ProjectModel, project_id)
            assert first_project is not None
            assert len(first_project.users) == 2
            first_project = lock_project(first_db, project_id)

            def remove_second_member() -> None:
                with SessionLocal() as second_db:
                    stale_project = second_db.get(ProjectModel, project_id)
                    assert stale_project is not None
                    assert len(stale_project.users) == 2
                    member_ready.set()
                    current_project = lock_project(second_db, project_id)
                    try:
                        remove_project_member(current_project, usernames[1])
                    except ProjectConflictError:
                        second_db.rollback()
                        member_result.put("conflict")
                    else:
                        second_db.commit()
                        member_result.put("deleted")

            member_thread = Thread(target=remove_second_member)
            member_thread.start()
            assert member_ready.wait(timeout=5)
            remove_project_member(first_project, usernames[0])
            first_db.commit()
            _join(member_thread)

        assert member_result.get(timeout=1) == "conflict"
        with SessionLocal() as db:
            membership_project = db.get(ProjectModel, project_id)
            assert membership_project is not None
            assert {user.username for user in membership_project.users} == {
                usernames[1]
            }

        # 後発の完全置換は、lock待機前に読んだ旧pool集合ではなく、先発が
        # commitした集合を再読込してから差分を作る。
        grant_ready = Event()
        grant_result: Queue[str] = Queue()
        with SessionLocal() as first_db:
            first_project = first_db.get(ProjectModel, project_id)
            assert first_project is not None
            assert {pool.id for pool in first_project.storage_pools} == {pool_ids[0]}
            first_project = lock_project(first_db, project_id)

            def replace_grants_again() -> None:
                with SessionLocal() as second_db:
                    stale_project = second_db.get(ProjectModel, project_id)
                    assert stale_project is not None
                    assert {pool.id for pool in stale_project.storage_pools} == {
                        pool_ids[0]
                    }
                    grant_ready.set()
                    current_project = lock_project(second_db, project_id)
                    replace_project_resource_grants(
                        second_db,
                        current_project,
                        ProjectResourceGrantsUpdate(
                            storage_pool_ids=[pool_ids[2]],
                            network_pool_ids=[],
                            flavor_ids=[],
                        ),
                    )
                    second_db.commit()
                    grant_result.put("replaced")

            grant_thread = Thread(target=replace_grants_again)
            grant_thread.start()
            assert grant_ready.wait(timeout=5)
            replace_project_resource_grants(
                first_db,
                first_project,
                ProjectResourceGrantsUpdate(
                    storage_pool_ids=[pool_ids[1]],
                    network_pool_ids=[],
                    flavor_ids=[],
                ),
            )
            first_db.commit()
            _join(grant_thread)

        assert grant_result.get(timeout=1) == "replaced"
        with SessionLocal() as db:
            grant_project = db.get(ProjectModel, project_id)
            assert grant_project is not None
            assert {pool.id for pool in grant_project.storage_pools} == {pool_ids[2]}
    finally:
        with SessionLocal.begin() as db:
            db.query(ProjectModel).filter(ProjectModel.id == project_id).delete(
                synchronize_session=False,
            )
            db.query(StoragePoolModel).filter(
                StoragePoolModel.name.in_(pool_names),
            ).delete(synchronize_session=False)
            db.query(UserModel).filter(
                UserModel.username.in_(usernames),
            ).delete(synchronize_session=False)
