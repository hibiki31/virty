import base64
import os
import threading
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime
from queue import Queue
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

import pytest
from sqlalchemy import Column, MetaData, String, Table, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateSchema, DropSchema

# TaskModelの外部key解決に必要な既存modelを登録する。
import models  # noqa: F401
from task.functions import (
    TaskManager,
    TaskTargetBusy,
    acquire_target_reservations,
    release_target_reservations_if_terminal,
    task_target_advisory_locks,
)
from task.models import TaskModel, TaskTargetReservationModel

pytestmark = [pytest.mark.integration, pytest.mark.timeout(60)]

TEST_ENCRYPTION_KEY = base64.urlsafe_b64encode(b"p" * 32).decode("ascii")


@dataclass(frozen=True)
class IsolatedPostgres:
    database_url: str
    schema: str

    def create_engine(self, **kwargs: Any) -> Engine:
        return create_engine(
            self.database_url,
            connect_args={"options": f"-csearch_path={self.schema}"},
            **kwargs,
        )


@pytest.fixture(scope="module")
def isolated_postgres() -> Iterator[IsolatedPostgres]:
    """verify workerから分離したschemaへtask safety tableだけを作成する。"""

    database_url = os.environ["SQLALCHEMY_DATABASE_URL"]
    schema = f"agent_task_safety_{uuid4().hex}"
    admin_engine = create_engine(database_url)
    with admin_engine.begin() as connection:
        connection.execute(CreateSchema(schema))

    database = IsolatedPostgres(database_url=database_url, schema=schema)
    test_engine = database.create_engine()
    try:
        metadata = MetaData()
        Table("users", metadata, Column("username", String, primary_key=True))
        TaskModel.__table__.to_metadata(metadata)
        TaskTargetReservationModel.__table__.to_metadata(metadata)
        metadata.create_all(test_engine)
        yield database
    finally:
        test_engine.dispose()
        with admin_engine.begin() as connection:
            connection.execute(DropSchema(schema, cascade=True))
        admin_engine.dispose()


def _task(task_uuid: str, resource_id: str) -> TaskModel:
    return TaskModel(
        uuid=task_uuid,
        principal_id="agent-user",
        idempotency_key=f"idempotency-{task_uuid}",
        correlation_id=f"operation-{task_uuid}",
        lease_id="lease-1",
        resolved_targets=[
            {"resourceType": "vm", "resourceId": resource_id},
        ],
    )


def _required_correlation_id(task: TaskModel) -> str:
    assert task.correlation_id is not None
    return task.correlation_id


def _required_lease_id(task: TaskModel) -> str:
    assert task.lease_id is not None
    return task.lease_id


def _required_resolved_targets(task: TaskModel) -> list[Any]:
    assert task.resolved_targets is not None
    return task.resolved_targets


def _required_task(task: TaskModel | None) -> TaskModel:
    assert task is not None
    return task


def _family_task(task_uuid: str) -> TaskModel:
    task = _task(task_uuid, "collection")
    task.resolved_targets = [
        {
            "resourceType": "vm",
            "resourceId": "collection",
            "reservationScope": "family",
            "reservationMode": "exclusive",
        },
    ]
    return task


def _node_lifecycle_task(
    task_uuid: str,
    node_id: str,
    lock_mode: str,
) -> TaskModel:
    task = _task(task_uuid, task_uuid)
    task.resolved_targets = [
        {
            "resourceType": "node-lifecycle",
            "resourceId": node_id,
            "reservationScope": "global",
            "reservationMode": lock_mode,
        },
    ]
    return task


def test_postgresql_target_lock_supports_family_reader_writer(
    isolated_postgres: IsolatedPostgres,
) -> None:
    engine = isolated_postgres.create_engine(pool_size=6, max_overflow=0)
    factory = sessionmaker(bind=engine)
    first_acquired = threading.Event()
    release_first = threading.Event()
    same_acquired = threading.Event()
    different_acquired = threading.Event()
    family_acquired = threading.Event()
    errors: Queue[BaseException] = Queue()

    def hold_first() -> None:
        try:
            with factory() as db:
                with task_target_advisory_locks(db, _task("first", "vm-1")):
                    first_acquired.set()
                    assert release_first.wait(timeout=5)
        except BaseException as exc:
            errors.put(exc)

    def acquire_same() -> None:
        try:
            with factory() as db:
                with task_target_advisory_locks(db, _task("same", "vm-1")):
                    same_acquired.set()
        except BaseException as exc:
            errors.put(exc)

    def acquire_different() -> None:
        try:
            with factory() as db:
                with task_target_advisory_locks(db, _task("different", "vm-2")):
                    different_acquired.set()
        except BaseException as exc:
            errors.put(exc)

    def acquire_family() -> None:
        try:
            with factory() as db:
                with task_target_advisory_locks(db, _family_task("family")):
                    family_acquired.set()
        except BaseException as exc:
            errors.put(exc)

    first = threading.Thread(target=hold_first, daemon=True)
    same = threading.Thread(target=acquire_same, daemon=True)
    different = threading.Thread(target=acquire_different, daemon=True)
    family = threading.Thread(target=acquire_family, daemon=True)
    try:
        first.start()
        assert first_acquired.wait(timeout=5)
        same.start()
        different.start()

        assert different_acquired.wait(timeout=2)
        assert same_acquired.wait(timeout=0.25) is False
        family.start()
        assert family_acquired.wait(timeout=0.25) is False

        release_first.set()
        assert same_acquired.wait(timeout=5)
        assert family_acquired.wait(timeout=5)
        first.join(timeout=5)
        same.join(timeout=5)
        different.join(timeout=5)
        family.join(timeout=5)
        assert errors.empty(), list(errors.queue)
    finally:
        release_first.set()
        first.join(timeout=5)
        same.join(timeout=5)
        different.join(timeout=5)
        family.join(timeout=5)
        engine.dispose()


def test_postgresql_node_lifecycle_lock_is_node_scoped(
    isolated_postgres: IsolatedPostgres,
) -> None:
    engine = isolated_postgres.create_engine(pool_size=6, max_overflow=0)
    factory = sessionmaker(bind=engine)
    first_acquired = threading.Event()
    release_first = threading.Event()
    same_reader_acquired = threading.Event()
    same_writer_acquired = threading.Event()
    other_writer_acquired = threading.Event()
    errors: Queue[BaseException] = Queue()

    def acquire(
        *,
        task_uuid: str,
        node_id: str,
        lock_mode: str,
        acquired: threading.Event,
        hold: bool = False,
    ) -> None:
        try:
            with factory() as db:
                task = _node_lifecycle_task(task_uuid, node_id, lock_mode)
                with task_target_advisory_locks(db, task):
                    acquired.set()
                    if hold:
                        assert release_first.wait(timeout=5)
        except BaseException as exc:
            errors.put(exc)

    first = threading.Thread(
        target=acquire,
        kwargs={
            "task_uuid": "node-reader-first",
            "node_id": "node-1",
            "lock_mode": "shared",
            "acquired": first_acquired,
            "hold": True,
        },
        daemon=True,
    )
    same_reader = threading.Thread(
        target=acquire,
        kwargs={
            "task_uuid": "node-reader-second",
            "node_id": "node-1",
            "lock_mode": "shared",
            "acquired": same_reader_acquired,
        },
        daemon=True,
    )
    same_writer = threading.Thread(
        target=acquire,
        kwargs={
            "task_uuid": "node-writer-same",
            "node_id": "node-1",
            "lock_mode": "exclusive",
            "acquired": same_writer_acquired,
        },
        daemon=True,
    )
    other_writer = threading.Thread(
        target=acquire,
        kwargs={
            "task_uuid": "node-writer-other",
            "node_id": "node-2",
            "lock_mode": "exclusive",
            "acquired": other_writer_acquired,
        },
        daemon=True,
    )
    threads = (first, same_reader, same_writer, other_writer)
    try:
        first.start()
        assert first_acquired.wait(timeout=5)
        same_reader.start()
        assert same_reader_acquired.wait(timeout=2)
        same_writer.start()
        other_writer.start()
        assert other_writer_acquired.wait(timeout=2)
        assert same_writer_acquired.wait(timeout=0.25) is False

        release_first.set()
        assert same_writer_acquired.wait(timeout=5)
        for thread in threads:
            thread.join(timeout=5)
        assert errors.empty(), list(errors.queue)
    finally:
        release_first.set()
        for thread in threads:
            if thread.ident is not None:
                thread.join(timeout=5)
        engine.dispose()


def test_postgresql_reservations_support_family_reader_writer(
    isolated_postgres: IsolatedPostgres,
) -> None:
    engine = isolated_postgres.create_engine(pool_size=4, max_overflow=0)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    first_target = [{"resourceType": "vm", "resourceId": "pg-vm-a"}]
    second_target = [{"resourceType": "vm", "resourceId": "pg-vm-b"}]
    family_target = _required_resolved_targets(_family_task("pg-family-target"))

    def persisted_task(
        task_uuid: str,
        correlation_id: str,
        lease_id: str,
        targets: list[Any],
    ) -> TaskModel:
        task = _task(task_uuid, task_uuid)
        task.correlation_id = correlation_id
        task.lease_id = lease_id
        task.resolved_targets = targets
        task.post_time = datetime.now().astimezone()
        task.request_hash = "request-hash"
        task.status = "init"
        task.resource = "vm"
        task.object = "root"
        task.method = "post"
        task.request = "{}"
        return task

    operation_ids = (
        "pg-family-reader-first",
        "pg-family-reader-second",
        "pg-family-writer",
    )
    try:
        with factory.begin() as db:
            db.query(TaskTargetReservationModel).filter(
                TaskTargetReservationModel.correlation_id.in_(operation_ids),
            ).delete(synchronize_session=False)
            db.query(TaskModel).filter(
                TaskModel.uuid.in_(operation_ids),
            ).delete(synchronize_session=False)

        with factory.begin() as db:
            first = persisted_task(
                operation_ids[0],
                operation_ids[0],
                "pg-family-lease-1",
                first_target,
            )
            db.add(first)
            acquire_target_reservations(
                db,
                resolved_targets=first_target,
                correlation_id=_required_correlation_id(first),
                lease_id=_required_lease_id(first),
            )

        with factory.begin() as db:
            second = persisted_task(
                operation_ids[1],
                operation_ids[1],
                "pg-family-lease-2",
                second_target,
            )
            db.add(second)
            acquire_target_reservations(
                db,
                resolved_targets=second_target,
                correlation_id=_required_correlation_id(second),
                lease_id=_required_lease_id(second),
            )

        with factory() as db:
            writer = persisted_task(
                operation_ids[2],
                operation_ids[2],
                "pg-family-lease-3",
                family_target,
            )
            db.add(writer)
            db.flush()
            with pytest.raises(TaskTargetBusy):
                acquire_target_reservations(
                    db,
                    resolved_targets=family_target,
                    correlation_id=_required_correlation_id(writer),
                    lease_id=_required_lease_id(writer),
                )
            db.rollback()

        with factory.begin() as db:
            for task_uuid in operation_ids[:2]:
                task = _required_task(db.get(TaskModel, task_uuid))
                task.status = "finish"
                assert release_target_reservations_if_terminal(
                    db,
                    _required_correlation_id(task),
                )

        with factory.begin() as db:
            writer = persisted_task(
                operation_ids[2],
                operation_ids[2],
                "pg-family-lease-3",
                family_target,
            )
            db.add(writer)
            acquire_target_reservations(
                db,
                resolved_targets=family_target,
                correlation_id=_required_correlation_id(writer),
                lease_id=_required_lease_id(writer),
            )
            writer.status = "finish"
            assert release_target_reservations_if_terminal(
                db,
                _required_correlation_id(writer),
            )
    finally:
        with factory.begin() as db:
            db.query(TaskTargetReservationModel).filter(
                TaskTargetReservationModel.correlation_id.in_(operation_ids),
            ).delete(synchronize_session=False)
            db.query(TaskModel).filter(
                TaskModel.uuid.in_(operation_ids),
            ).delete(synchronize_session=False)
        engine.dispose()


def test_postgresql_reservation_unique_race_is_fail_closed(
    isolated_postgres: IsolatedPostgres,
) -> None:
    engine = isolated_postgres.create_engine(pool_size=4, max_overflow=0)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    target = [{"resourceType": "vm", "resourceId": "pg-race-vm"}]
    first_reserved = threading.Event()
    commit_first = threading.Event()
    second_started = threading.Event()
    second_finished = threading.Event()
    errors: Queue[BaseException] = Queue()
    results: Queue[str] = Queue()

    def task(task_uuid: str, correlation_id: str, lease_id: str) -> TaskModel:
        return TaskModel(
            uuid=task_uuid,
            post_time=datetime.now().astimezone(),
            principal_id="pg-agent",
            idempotency_key=f"idempotency-{task_uuid}",
            request_hash="request-hash",
            correlation_id=correlation_id,
            lease_id=lease_id,
            resolved_targets=target,
            status="init",
            resource="vm",
            object="root",
            method="post",
            request="{}",
        )

    def reserve_first() -> None:
        try:
            with factory() as db:
                db.add(task("pg-race-first", "pg-operation-first", "pg-lease-1"))
                db.flush()
                acquire_target_reservations(
                    db,
                    resolved_targets=target,
                    correlation_id="pg-operation-first",
                    lease_id="pg-lease-1",
                )
                first_reserved.set()
                assert commit_first.wait(timeout=5)
                db.commit()
        except BaseException as exc:
            errors.put(exc)

    def reserve_second() -> None:
        try:
            with factory() as db:
                db.add(task("pg-race-second", "pg-operation-second", "pg-lease-2"))
                db.flush()
                second_started.set()
                try:
                    acquire_target_reservations(
                        db,
                        resolved_targets=target,
                        correlation_id="pg-operation-second",
                        lease_id="pg-lease-2",
                    )
                except TaskTargetBusy:
                    results.put("busy")
                else:
                    results.put("acquired")
                finally:
                    db.rollback()
        except BaseException as exc:
            errors.put(exc)
        finally:
            second_finished.set()

    first = threading.Thread(target=reserve_first, daemon=True)
    second = threading.Thread(target=reserve_second, daemon=True)
    try:
        with factory.begin() as db:
            db.query(TaskTargetReservationModel).filter(
                TaskTargetReservationModel.correlation_id.in_(
                    ("pg-operation-first", "pg-operation-second"),
                ),
            ).delete(synchronize_session=False)
            db.query(TaskModel).filter(
                TaskModel.uuid.in_(("pg-race-first", "pg-race-second")),
            ).delete(synchronize_session=False)

        first.start()
        if not first_reserved.wait(timeout=5):
            pytest.fail(f"最初のreservation取得に失敗しました: {list(errors.queue)!r}")
        second.start()
        assert second_started.wait(timeout=5)
        assert second_finished.wait(timeout=0.25) is False

        commit_first.set()
        assert second_finished.wait(timeout=5)
        first.join(timeout=5)
        second.join(timeout=5)
        assert errors.empty(), list(errors.queue)
        assert results.get_nowait() == "busy"

        with factory.begin() as db:
            winner = _required_task(db.get(TaskModel, "pg-race-first"))
            winner.status = "finish"
            assert release_target_reservations_if_terminal(
                db,
                _required_correlation_id(winner),
            ) is True
            db.delete(winner)
    finally:
        commit_first.set()
        first.join(timeout=5)
        if second.ident is not None:
            second.join(timeout=5)
        engine.dispose()


def test_postgresql_idempotency_race_returns_single_agent_task(
    monkeypatch: pytest.MonkeyPatch,
    isolated_postgres: IsolatedPostgres,
) -> None:
    monkeypatch.setenv("AGENT_TASK_ENCRYPTION_KEY", TEST_ENCRYPTION_KEY)

    engine = isolated_postgres.create_engine(pool_size=4, max_overflow=0)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    users = Table("users", MetaData(), autoload_with=engine)
    principal_id = "pg-idempotency-agent"
    idempotency_key = "pg-simultaneous-agent-retry"
    barrier = threading.Barrier(2)
    errors: Queue[BaseException] = Queue()
    results: Queue[tuple[str, bool]] = Queue()

    def submit() -> None:
        try:
            with factory() as db:
                manager = TaskManager(db)
                manager.select("post", "vm", "root")
                original_find = manager._find_idempotent_task
                calls = 0

                def synchronize_first_lookup(
                    *,
                    principal_id: str,
                    idempotency_key: str,
                ) -> TaskModel | None:
                    nonlocal calls
                    calls += 1
                    if calls == 1:
                        barrier.wait(timeout=5)
                        return None
                    return original_find(
                        principal_id=principal_id,
                        idempotency_key=idempotency_key,
                    )

                monkeypatch.setattr(
                    manager,
                    "_find_idempotent_task",
                    synchronize_first_lookup,
                )
                task = manager.commit(
                    SimpleNamespace(id=principal_id),
                    body={"secret": "not-stored-in-plaintext"},
                    idempotency_key=idempotency_key,
                    agent_request_hash="a" * 64,
                    lease_id="pg-idempotency-lease",
                    resolved_targets=[
                        {"resourceType": "vm", "resourceId": "pg-idempotency-vm"},
                    ],
                )
                results.put((task.uuid, manager.created))
        except BaseException as exc:
            errors.put(exc)

    threads = [threading.Thread(target=submit, daemon=True) for _ in range(2)]
    try:
        with factory.begin() as db:
            db.query(TaskModel).filter(
                TaskModel.principal_id == principal_id,
                TaskModel.idempotency_key == idempotency_key,
            ).delete(synchronize_session=False)
            db.execute(users.delete().where(users.c.username == principal_id))
            db.execute(users.insert().values(username=principal_id))

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)
        assert all(not thread.is_alive() for thread in threads)
        assert errors.empty(), list(errors.queue)
        submitted = [results.get_nowait() for _ in range(2)]
        assert len({task_uuid for task_uuid, _ in submitted}) == 1
        assert sorted(created for _, created in submitted) == [False, True]

        with factory() as db:
            rows = db.query(TaskModel).filter(
                TaskModel.principal_id == principal_id,
                TaskModel.idempotency_key == idempotency_key,
            ).all()
            assert len(rows) == 1
            assert "not-stored-in-plaintext" not in str(rows[0].request)
    finally:
        with factory.begin() as db:
            db.query(TaskModel).filter(
                TaskModel.principal_id == principal_id,
                TaskModel.idempotency_key == idempotency_key,
            ).delete(synchronize_session=False)
            db.execute(users.delete().where(users.c.username == principal_id))
        engine.dispose()


def test_postgresql_user_delete_preserves_agent_idempotency_ledger(
    monkeypatch: pytest.MonkeyPatch,
    isolated_postgres: IsolatedPostgres,
) -> None:
    monkeypatch.setenv("AGENT_TASK_ENCRYPTION_KEY", TEST_ENCRYPTION_KEY)

    engine = isolated_postgres.create_engine()
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    users = Table("users", MetaData(), autoload_with=engine)
    principal_id = "pg-deleted-agent-principal"
    idempotency_key = "pg-preserved-agent-ledger"
    try:
        with factory.begin() as db:
            db.query(TaskModel).filter(
                TaskModel.principal_id == principal_id,
                TaskModel.idempotency_key == idempotency_key,
            ).delete(synchronize_session=False)
            db.execute(users.delete().where(users.c.username == principal_id))
            db.execute(users.insert().values(username=principal_id))

        with factory() as db:
            manager = TaskManager(db)
            manager.select("post", "vm", "root")
            task = manager.commit(
                SimpleNamespace(id=principal_id),
                body={"name": "ledger-preserved"},
                idempotency_key=idempotency_key,
                agent_request_hash="b" * 64,
                lease_id="pg-deleted-agent-lease",
                resolved_targets=[
                    {"resourceType": "vm", "resourceId": "pg-deleted-agent-vm"},
                ],
            )
            task_uuid = task.uuid

        with factory.begin() as db:
            db.execute(users.delete().where(users.c.username == principal_id))

        with factory() as db:
            preserved = _required_task(db.get(TaskModel, task_uuid))
            assert preserved is not None
            assert preserved.user_id is None
            assert preserved.principal_id == principal_id
            assert preserved.idempotency_key == idempotency_key
            assert preserved.agent_request_hash == "b" * 64

            replay = TaskManager(db)
            replay.select("post", "vm", "root")
            existing = replay.commit(
                SimpleNamespace(id=principal_id),
                body={"name": "ledger-preserved"},
                idempotency_key=idempotency_key,
                agent_request_hash="b" * 64,
                lease_id="pg-deleted-agent-lease",
                resolved_targets=[
                    {"resourceType": "vm", "resourceId": "pg-deleted-agent-vm"},
                ],
            )
            assert existing.uuid == task_uuid
            assert replay.created is False
    finally:
        with factory.begin() as db:
            db.query(TaskModel).filter(
                TaskModel.principal_id == principal_id,
                TaskModel.idempotency_key == idempotency_key,
            ).delete(synchronize_session=False)
            db.execute(users.delete().where(users.c.username == principal_id))
        engine.dispose()
