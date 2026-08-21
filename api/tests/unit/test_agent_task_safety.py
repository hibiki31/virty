import base64
import json
from contextlib import contextmanager
from types import SimpleNamespace
from typing import Any, Iterator

import pytest
from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# TaskModelの外部key解決に必要な既存modelを登録する。
import models  # noqa: F401
from task import functions as task_functions
from task.crypto import (
    TaskRequestEncryptionConfigurationError,
    decrypt_task_request,
    is_encrypted_task_request,
)
from task.functions import (
    TaskBase,
    TaskCancellationRequested,
    TaskDispatchRejected,
    TaskIdempotencyConflict,
    TaskManager,
    TaskOwnershipError,
    TaskPolicyUnavailable,
    TaskTargetBusy,
    acquire_target_reservations,
    archive_terminal_tasks,
    calculate_task_request_hash,
    calculate_target_reservation_keys,
    evaluate_dispatch_policy,
    get_operation,
    release_target_reservations_if_terminal,
    request_cancel_operation,
    validate_target_reservations,
)
from task.models import TaskModel, TaskTargetReservationModel
from task.schemas import Task

pytestmark = [pytest.mark.unit, pytest.mark.timeout(30)]

TEST_ENCRYPTION_KEY = base64.urlsafe_b64encode(b"t" * 32).decode("ascii")
AGENT_TARGET = [{"resourceType": "vm", "resourceId": "vm-1"}]


@pytest.fixture(autouse=True)
def agent_task_encryption_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGENT_TASK_ENCRYPTION_KEY", TEST_ENCRYPTION_KEY)


@pytest.fixture()
def db_factory() -> Iterator[sessionmaker[Session]]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    metadata = MetaData()
    Table("users", metadata, Column("username", String, primary_key=True))
    Table("transaction_markers", metadata, Column("id", Integer, primary_key=True))
    TaskModel.__table__.to_metadata(metadata)
    TaskTargetReservationModel.__table__.to_metadata(metadata)
    metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    yield factory
    engine.dispose()


def _manager(db: Session, *, method: str = "post") -> TaskManager:
    manager = TaskManager(db)
    manager.select(method, "vm", "root")
    return manager


def _user(name: str = "agent-user") -> SimpleNamespace:
    return SimpleNamespace(id=name)


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


def test_request_hash_is_canonical() -> None:
    left = calculate_task_request_hash(
        method="post",
        resource="vm",
        object_name="root",
        path_param={"b": 2, "a": 1},
        body={"memory": 4, "tags": ["a", "b"]},
        expected_generation="7",
    )
    right = calculate_task_request_hash(
        method="post",
        resource="vm",
        object_name="root",
        path_param={"a": 1, "b": 2},
        body={"tags": ["a", "b"], "memory": 4},
        expected_generation="7",
    )
    assert left == right
    assert len(left) == 64


def test_task_owner_fk_preserves_agent_ledger_after_user_deletion() -> None:
    foreign_key = next(iter(TaskModel.__table__.c.user_id.foreign_keys))
    assert foreign_key.ondelete == "SET NULL"


def test_target_reservation_keys_are_stable_sorted_and_deduplicated() -> None:
    targets = [
        {"resourceType": "vm", "resourceId": "vm-2"},
        {"resource_type": "node", "resource_id": "node-1"},
        {"resourceType": "vm", "resourceId": "vm-2"},
    ]
    keys = calculate_target_reservation_keys(targets)

    assert keys == tuple(sorted(keys))
    # resourceごとのexclusiveとfamily単位のsharedへ展開される。
    assert len(keys) == 4
    assert keys == calculate_target_reservation_keys(list(reversed(targets)))


def test_target_reservation_is_reentrant_and_rejects_active_operation(
    db_factory: sessionmaker[Session],
) -> None:
    with db_factory() as db:
        first = _manager(db).commit(
            _user(),
            body={"name": "vm-1"},
            idempotency_key="reservation-first",
            correlation_id="operation-first",
            lease_id="lease-1",
            resolved_targets=AGENT_TARGET,
        )
        keys = acquire_target_reservations(
            db,
            resolved_targets=AGENT_TARGET,
            correlation_id=_required_correlation_id(first),
            lease_id=_required_lease_id(first),
        )
        db.commit()

        assert acquire_target_reservations(
            db,
            resolved_targets=AGENT_TARGET,
            correlation_id=_required_correlation_id(first),
            lease_id=_required_lease_id(first),
        ) == keys
        with pytest.raises(TaskDispatchRejected) as lease_error:
            acquire_target_reservations(
                db,
                resolved_targets=AGENT_TARGET,
                correlation_id=_required_correlation_id(first),
                lease_id="different-lease",
            )
        assert (
            lease_error.value.error_code == "TASK_RESERVATION_LEASE_MISMATCH"
        )

        second = _manager(db).commit(
            _user(),
            body={"name": "vm-1"},
            idempotency_key="reservation-second",
            correlation_id="operation-second",
            lease_id="lease-2",
            resolved_targets=AGENT_TARGET,
        )
        with pytest.raises(TaskTargetBusy) as busy_error:
            acquire_target_reservations(
                db,
                resolved_targets=AGENT_TARGET,
                correlation_id=_required_correlation_id(second),
                lease_id=_required_lease_id(second),
            )
        assert busy_error.value.error_code == "TARGET_BUSY"
        assert busy_error.value.retryable is True


def test_target_reservation_rolls_back_partial_multi_target_acquisition(
    db_factory: sessionmaker[Session],
) -> None:
    candidates = [
        {"resourceType": "vm", "resourceId": "vm-a"},
        {"resourceType": "vm", "resourceId": "vm-b"},
    ]
    candidates.sort(key=lambda target: calculate_target_reservation_keys([target]))
    free_target, busy_target = candidates

    with db_factory() as db:
        blocker = _manager(db).commit(
            _user(),
            body={"name": "blocker"},
            idempotency_key="reservation-blocker",
            correlation_id="operation-blocker",
            lease_id="lease-blocker",
            resolved_targets=[busy_target],
        )
        acquire_target_reservations(
            db,
            resolved_targets=[busy_target],
            correlation_id=_required_correlation_id(blocker),
            lease_id=_required_lease_id(blocker),
        )
        db.commit()

        with pytest.raises(TaskTargetBusy):
            acquire_target_reservations(
                db,
                resolved_targets=[free_target, busy_target],
                correlation_id="operation-requester",
                lease_id="lease-requester",
            )

        requester_rows = db.query(TaskTargetReservationModel).filter(
            TaskTargetReservationModel.correlation_id == "operation-requester",
        ).count()
        assert requester_rows == 0


def test_family_reader_writer_reservations_allow_distinct_resources(
    db_factory: sessionmaker[Session],
) -> None:
    first_target = [{"resourceType": "vm", "resourceId": "vm-a"}]
    second_target = [{"resourceType": "vm", "resourceId": "vm-b"}]
    family_target = [
        {
            "resourceType": "vm",
            "resourceId": "collection",
            "reservationScope": "family",
            "reservationMode": "exclusive",
        },
    ]

    with db_factory() as db:
        first = _manager(db).commit(
            _user(),
            body={"name": "vm-a"},
            idempotency_key="family-reader-first",
            correlation_id="family-reader-first-operation",
            lease_id="lease-1",
            resolved_targets=first_target,
        )
        second = _manager(db).commit(
            _user(),
            body={"name": "vm-b"},
            idempotency_key="family-reader-second",
            correlation_id="family-reader-second-operation",
            lease_id="lease-2",
            resolved_targets=second_target,
        )
        acquire_target_reservations(
            db,
            resolved_targets=first_target,
            correlation_id=_required_correlation_id(first),
            lease_id=_required_lease_id(first),
        )
        acquire_target_reservations(
            db,
            resolved_targets=second_target,
            correlation_id=_required_correlation_id(second),
            lease_id=_required_lease_id(second),
        )
        assert db.query(TaskTargetReservationModel).count() == 4

        refresh = _manager(db).commit(
            _user(),
            body={"refresh": True},
            idempotency_key="family-writer",
            correlation_id="family-writer-operation",
            lease_id="lease-3",
            resolved_targets=family_target,
        )
        with pytest.raises(TaskTargetBusy):
            acquire_target_reservations(
                db,
                resolved_targets=family_target,
                correlation_id=_required_correlation_id(refresh),
                lease_id=_required_lease_id(refresh),
            )

        first.status = "finish"
        second.status = "finish"
        db.flush()
        assert release_target_reservations_if_terminal(db, _required_correlation_id(first))
        assert release_target_reservations_if_terminal(db, _required_correlation_id(second))

        acquire_target_reservations(
            db,
            resolved_targets=family_target,
            correlation_id=_required_correlation_id(refresh),
            lease_id=_required_lease_id(refresh),
        )
        third = _manager(db).commit(
            _user(),
            body={"name": "vm-c"},
            idempotency_key="family-reader-third",
            correlation_id="family-reader-third-operation",
            lease_id="lease-4",
            resolved_targets=[{"resourceType": "vm", "resourceId": "vm-c"}],
        )
        with pytest.raises(TaskTargetBusy):
            acquire_target_reservations(
                db,
                resolved_targets=_required_resolved_targets(third),
                correlation_id=_required_correlation_id(third),
                lease_id=_required_lease_id(third),
            )


def test_global_reader_writer_reservations_protect_ssh_credentials(
    db_factory: sessionmaker[Session],
) -> None:
    shared_target = [
        {
            "resourceType": "ssh-credentials",
            "resourceId": "global",
            "reservationScope": "global",
            "reservationMode": "shared",
        },
    ]
    exclusive_target = [
        {
            **shared_target[0],
            "reservationMode": "exclusive",
        },
    ]

    with db_factory() as db:
        readers = []
        for suffix in ("first", "second"):
            reader = _manager(db).commit(
                _user(),
                body={"operation": suffix},
                idempotency_key=f"ssh-reader-{suffix}",
                correlation_id=f"ssh-reader-{suffix}-operation",
                lease_id=f"lease-{suffix}",
                resolved_targets=shared_target,
            )
            acquire_target_reservations(
                db,
                resolved_targets=shared_target,
                correlation_id=_required_correlation_id(reader),
                lease_id=_required_lease_id(reader),
            )
            readers.append(reader)
        assert db.query(TaskTargetReservationModel).count() == 2

        writer = _manager(db).commit(
            _user(),
            body={"write": True},
            idempotency_key="ssh-writer",
            correlation_id="ssh-writer-operation",
            lease_id="lease-writer",
            resolved_targets=exclusive_target,
        )
        with pytest.raises(TaskTargetBusy):
            acquire_target_reservations(
                db,
                resolved_targets=exclusive_target,
                correlation_id=_required_correlation_id(writer),
                lease_id=_required_lease_id(writer),
            )

        for reader in readers:
            reader.status = "finish"
            db.flush()
            assert release_target_reservations_if_terminal(
                db,
                _required_correlation_id(reader),
            )
        acquire_target_reservations(
            db,
            resolved_targets=exclusive_target,
            correlation_id=_required_correlation_id(writer),
            lease_id=_required_lease_id(writer),
        )

        blocked_reader = _manager(db).commit(
            _user(),
            body={"operation": "blocked"},
            idempotency_key="ssh-reader-blocked",
            correlation_id="ssh-reader-blocked-operation",
            lease_id="lease-blocked",
            resolved_targets=shared_target,
        )
        with pytest.raises(TaskTargetBusy):
            acquire_target_reservations(
                db,
                resolved_targets=shared_target,
                correlation_id=_required_correlation_id(blocked_reader),
                lease_id=_required_lease_id(blocked_reader),
            )


def test_node_lifecycle_writer_conflicts_only_on_same_node(
    db_factory: sessionmaker[Session],
) -> None:
    def lifecycle_target(node_id: str, mode: str) -> list[dict[str, str]]:
        return [
            {
                "resourceType": "node-lifecycle",
                "resourceId": node_id,
                "reservationScope": "global",
                "reservationMode": mode,
            },
        ]

    with db_factory() as db:
        same_node_readers = []
        for suffix in ("first", "second"):
            target = lifecycle_target("node-1", "shared")
            reader = _manager(db).commit(
                _user(),
                body={"operation": suffix},
                idempotency_key=f"node-lifecycle-reader-{suffix}",
                correlation_id=f"node-lifecycle-reader-{suffix}-operation",
                lease_id=f"node-lifecycle-lease-{suffix}",
                resolved_targets=target,
            )
            acquire_target_reservations(
                db,
                resolved_targets=target,
                correlation_id=_required_correlation_id(reader),
                lease_id=_required_lease_id(reader),
            )
            same_node_readers.append(reader)

        other_node_target = lifecycle_target("node-2", "exclusive")
        other_node_writer = _manager(db).commit(
            _user(),
            body={"operation": "other-node"},
            idempotency_key="node-lifecycle-other-writer",
            correlation_id="node-lifecycle-other-writer-operation",
            lease_id="node-lifecycle-other-lease",
            resolved_targets=other_node_target,
        )
        acquire_target_reservations(
            db,
            resolved_targets=other_node_target,
            correlation_id=_required_correlation_id(other_node_writer),
            lease_id=_required_lease_id(other_node_writer),
        )

        same_node_writer_target = lifecycle_target("node-1", "exclusive")
        same_node_writer = _manager(db).commit(
            _user(),
            body={"operation": "same-node"},
            idempotency_key="node-lifecycle-same-writer",
            correlation_id="node-lifecycle-same-writer-operation",
            lease_id="node-lifecycle-same-lease",
            resolved_targets=same_node_writer_target,
        )
        with pytest.raises(TaskTargetBusy):
            acquire_target_reservations(
                db,
                resolved_targets=same_node_writer_target,
                correlation_id=_required_correlation_id(same_node_writer),
                lease_id=_required_lease_id(same_node_writer),
            )

        assert len(same_node_readers) == 2
        assert db.query(TaskTargetReservationModel).count() == 3


def test_terminal_reservation_can_be_taken_over_but_orphan_cannot(
    db_factory: sessionmaker[Session],
) -> None:
    orphan_target = [
        {
            "resourceType": "orphan-scope",
            "resourceId": "global",
            "reservationScope": "global",
            "reservationMode": "exclusive",
        },
    ]
    orphan_key = calculate_target_reservation_keys(orphan_target)[0]
    with db_factory() as db:
        first = _manager(db).commit(
            _user(),
            body={"name": "vm-1"},
            idempotency_key="reservation-terminal-first",
            correlation_id="operation-terminal-first",
            lease_id="lease-1",
            resolved_targets=AGENT_TARGET,
        )
        acquire_target_reservations(
            db,
            resolved_targets=AGENT_TARGET,
            correlation_id=_required_correlation_id(first),
            lease_id=_required_lease_id(first),
        )
        first.status = "finish"
        db.add(
            TaskTargetReservationModel(
                reservation_id="orphan-reservation",
                target_key=orphan_key,
                lock_mode="exclusive",
                correlation_id="operation-orphan",
                lease_id="lease-orphan",
                acquired_at=first.post_time,
            ),
        )
        db.commit()

        second = _manager(db).commit(
            _user(),
            body={"name": "vm-1"},
            idempotency_key="reservation-terminal-second",
            correlation_id="operation-terminal-second",
            lease_id="lease-2",
            resolved_targets=AGENT_TARGET,
        )
        acquire_target_reservations(
            db,
            resolved_targets=AGENT_TARGET,
            correlation_id=_required_correlation_id(second),
            lease_id=_required_lease_id(second),
        )
        db.commit()
        reservation = (
            db.query(TaskTargetReservationModel)
            .filter(
                TaskTargetReservationModel.target_key
                == calculate_target_reservation_keys(AGENT_TARGET)[0],
            )
            .one()
        )
        assert reservation.correlation_id == _required_correlation_id(second)

        with pytest.raises(TaskTargetBusy):
            acquire_target_reservations(
                db,
                resolved_targets=orphan_target,
                correlation_id="operation-new",
                lease_id="lease-new",
            )


def test_unknown_operation_keeps_reservation_until_reconciled(
    db_factory: sessionmaker[Session],
) -> None:
    with db_factory() as db:
        uncertain = _manager(db).commit(
            _user(),
            body={"name": "vm-1"},
            idempotency_key="reservation-unknown",
            correlation_id="operation-unknown",
            lease_id="lease-1",
            resolved_targets=AGENT_TARGET,
        )
        acquire_target_reservations(
            db,
            resolved_targets=AGENT_TARGET,
            correlation_id=_required_correlation_id(uncertain),
            lease_id=_required_lease_id(uncertain),
        )
        uncertain.status = "unknown"
        db.commit()

        assert (
            release_target_reservations_if_terminal(
                db,
                _required_correlation_id(uncertain),
            )
            is False
        )
        with pytest.raises(TaskTargetBusy):
            acquire_target_reservations(
                db,
                resolved_targets=AGENT_TARGET,
                correlation_id="operation-after-unknown",
                lease_id="lease-2",
            )
        assert db.query(TaskTargetReservationModel).count() == 2

        # WebAuthn管理reconcileが実状態を確定した後の状態遷移を模擬する。
        uncertain.status = "finish"
        db.flush()
        assert (
            release_target_reservations_if_terminal(
                db,
                _required_correlation_id(uncertain),
            )
            is True
        )
        assert db.query(TaskTargetReservationModel).count() == 0


def test_target_reservation_releases_only_after_entire_chain_is_terminal(
    db_factory: sessionmaker[Session],
) -> None:
    with db_factory() as db:
        root = _manager(db).commit(
            _user(),
            body={"name": "vm-1"},
            idempotency_key="reservation-chain",
            lease_id="lease-1",
            resolved_targets=AGENT_TARGET,
        )
        child = _manager(db, method="put").commit(
            _user(),
            dep_uuid=root.uuid,
            lease_id="lease-1",
        )
        acquire_target_reservations(
            db,
            resolved_targets=_required_resolved_targets(root),
            correlation_id=_required_correlation_id(root),
            lease_id=_required_lease_id(root),
        )
        root.status = "finish"
        db.flush()

        assert release_target_reservations_if_terminal(db, _required_correlation_id(root)) is False
        assert db.query(TaskTargetReservationModel).count() == 2

        child.status = "cancelled"
        db.flush()
        assert release_target_reservations_if_terminal(db, _required_correlation_id(root)) is True
        assert db.query(TaskTargetReservationModel).count() == 0


def test_soft_archive_preserves_agent_ledger_and_active_reservations(
    db_factory: sessionmaker[Session],
) -> None:
    assert task_functions.ARCHIVABLE_STATUSES == frozenset(
        {"finish", "error", "lost", "cancelled"},
    )
    with db_factory() as db:
        legacy_terminal = _manager(db).commit(
            _user("legacy-user"),
            body={"name": "legacy"},
        )
        legacy_terminal.status = "finish"
        agent_terminal = _manager(db).commit(
            _user(),
            body={"name": "agent-terminal"},
            idempotency_key="archive-agent-terminal",
            correlation_id="archive-agent-terminal-operation",
            lease_id="archive-lease-terminal",
            resolved_targets=AGENT_TARGET,
        )
        acquire_target_reservations(
            db,
            resolved_targets=_required_resolved_targets(agent_terminal),
            correlation_id=_required_correlation_id(agent_terminal),
            lease_id=_required_lease_id(agent_terminal),
        )
        agent_terminal.status = "error"
        agent_unknown = _manager(db).commit(
            _user(),
            body={"name": "agent-unknown"},
            idempotency_key="archive-agent-unknown",
            correlation_id="archive-agent-unknown-operation",
            lease_id="archive-lease-unknown",
            resolved_targets=[{"resourceType": "vm", "resourceId": "vm-unknown"}],
        )
        agent_unknown.status = "unknown"
        legacy_active = _manager(db).commit(
            _user("legacy-active-user"),
            body={"name": "legacy-active"},
        )
        db.flush()

        archived = archive_terminal_tasks(db)

        assert {task.uuid for task in archived} == {
            legacy_terminal.uuid,
            agent_terminal.uuid,
        }
        assert agent_terminal.archived_at is not None
        assert legacy_terminal.archived_at is not None
        assert agent_unknown.archived_at is None
        assert legacy_active.archived_at is None
        ledger = (
            db.query(TaskModel)
            .filter(
                TaskModel.principal_id == "agent-user",
                TaskModel.idempotency_key == "archive-agent-terminal",
            )
            .one()
        )
        assert ledger.uuid == agent_terminal.uuid
        assert db.query(TaskModel).count() == 4
        # archiveはreservationを解放・削除するreconcile操作ではない。
        assert db.query(TaskTargetReservationModel).count() == 2


def test_dispatch_rejects_missing_or_mismatched_target_reservation(
    db_factory: sessionmaker[Session],
) -> None:
    with db_factory() as db:
        task = _manager(db).commit(
            _user(),
            body={"name": "vm-1"},
            idempotency_key="reservation-validation",
            lease_id="lease-1",
            resolved_targets=AGENT_TARGET,
        )
        with pytest.raises(TaskDispatchRejected) as missing_error:
            validate_target_reservations(db, task)
        assert missing_error.value.error_code == "TASK_TARGET_RESERVATION_MISSING"

        db.add(
            TaskTargetReservationModel(
                reservation_id="mismatched-reservation",
                target_key=calculate_target_reservation_keys(AGENT_TARGET)[0],
                lock_mode="exclusive",
                correlation_id=_required_correlation_id(task),
                lease_id="different-lease",
                acquired_at=task.post_time,
            ),
        )
        db.flush()
        with pytest.raises(TaskDispatchRejected) as mismatch_error:
            validate_target_reservations(db, task)
        assert mismatch_error.value.error_code == "TASK_TARGET_RESERVATION_MISMATCH"


def test_commit_replays_same_request_and_rejects_different_request(
    db_factory: sessionmaker[Session],
) -> None:
    with db_factory() as db:
        first_manager = _manager(db)
        first = first_manager.commit(
            _user(),
            body={"name": "vm-1"},
            idempotency_key="request-0001",
            lease_id="lease-1",
            risk="R2",
            expected_generation="3",
            resolved_targets=AGENT_TARGET,
        )
        assert first_manager.created is True
        assert first.idempotency_replayed is False

        replay_manager = _manager(db)
        replay = replay_manager.commit(
            _user(),
            body={"name": "vm-1"},
            idempotency_key="request-0001",
            lease_id="lease-2",
            risk="R2",
            expected_generation="3",
            resolved_targets=AGENT_TARGET,
        )
        assert replay.uuid == first.uuid
        assert replay_manager.created is False
        assert replay.idempotency_replayed is True

        with pytest.raises(TaskIdempotencyConflict) as exc_info:
            _manager(db).commit(
                _user(),
                body={"name": "vm-2"},
                idempotency_key="request-0001",
                lease_id="lease-2",
                risk="R2",
                expected_generation="3",
                resolved_targets=AGENT_TARGET,
            )
        assert exc_info.value.error_code == "IDEMPOTENCY_KEY_CONFLICT"


def test_agent_request_hash_allows_pre_resolution_replay_and_is_inherited(
    db_factory: sessionmaker[Session],
) -> None:
    request_hash = "a" * 64
    with db_factory() as db:
        first_manager = _manager(db)
        first = first_manager.commit(
            _user(),
            body={"name": "vm-before-delete"},
            idempotency_key="agent-request-hash",
            agent_request_hash=request_hash,
            lease_id="lease-1",
            resolved_targets=AGENT_TARGET,
        )
        assert first.agent_request_hash == request_hash

        replay_manager = _manager(db)
        replay = replay_manager.commit(
            _user(),
            body={"name": "resource-already-deleted"},
            idempotency_key="agent-request-hash",
            agent_request_hash=request_hash,
            lease_id="lease-2",
            resolved_targets=[{"resourceType": "vm", "resourceId": "missing"}],
        )
        assert replay.uuid == first.uuid
        assert replay_manager.idempotency_replayed is True

        with pytest.raises(TaskIdempotencyConflict):
            _manager(db).commit(
                _user(),
                body={"name": "different-request"},
                idempotency_key="agent-request-hash",
                agent_request_hash="b" * 64,
                lease_id="lease-2",
                resolved_targets=AGENT_TARGET,
            )

        child = _manager(db, method="put").commit(
            _user(),
            dep_uuid=first.uuid,
            lease_id="lease-1",
        )
        assert child.agent_request_hash == request_hash

        with pytest.raises(TaskIdempotencyConflict) as invalid_error:
            _manager(db).commit(
                _user(),
                body={"name": "invalid-hash"},
                idempotency_key="invalid-agent-request-hash",
                agent_request_hash="not-a-sha256",
            )
        assert invalid_error.value.error_code == "AGENT_REQUEST_HASH_INVALID"


def test_request_hash_assertion_and_principal_uniqueness(
    db_factory: sessionmaker[Session],
) -> None:
    with db_factory() as db:
        with pytest.raises(TaskIdempotencyConflict) as exc_info:
            _manager(db).commit(
                _user(),
                body={"name": "vm-1"},
                idempotency_key="request-0002",
                request_hash="0" * 64,
            )
        assert exc_info.value.error_code == "REQUEST_HASH_MISMATCH"

        first = _manager(db).commit(
            _user("user-a"),
            body={"name": "vm-1"},
            idempotency_key="request-0003",
        )
        second = _manager(db).commit(
            _user("user-b"),
            body={"name": "vm-1"},
            idempotency_key="request-0003",
        )
        assert first.uuid != second.uuid

        duplicate = TaskModel(
            uuid="duplicate",
            user_id="user-a",
            principal_id="user-a",
            idempotency_key="request-0003",
            request_hash=first.request_hash,
            correlation_id="duplicate",
            status="init",
            resource="vm",
            object="root",
            method="post",
            request='{"path_param": {}, "body": null}',
        )
        db.add(duplicate)
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()


def test_concurrent_idempotency_conflict_returns_committed_task(
    db_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with db_factory() as db:
        first = _manager(db).commit(
            _user(),
            body={"name": "vm-1"},
            idempotency_key="request-race",
        )

        racing_manager = _manager(db)
        original_find = racing_manager._find_idempotent_task
        calls = 0

        def simulate_race(
            *,
            principal_id: str,
            idempotency_key: str,
        ) -> TaskModel | None:
            nonlocal calls
            calls += 1
            if calls == 1:
                return None
            return original_find(
                principal_id=principal_id,
                idempotency_key=idempotency_key,
            )

        monkeypatch.setattr(
            racing_manager,
            "_find_idempotent_task",
            simulate_race,
        )
        db.execute(text("INSERT INTO transaction_markers (id) VALUES (1)"))
        replay = racing_manager.commit(
            _user(),
            body={"name": "vm-1"},
            idempotency_key="request-race",
        )

        assert replay.uuid == first.uuid
        assert racing_manager.idempotency_replayed is True
        marker_count = db.execute(
            text("SELECT count(*) FROM transaction_markers"),
        ).scalar_one()
        assert marker_count == 1


def test_agent_operation_batch_can_commit_atomically(
    db_factory: sessionmaker[Session],
) -> None:
    with db_factory() as db:
        # SQLiteは遅延BEGINのため、savepointより前に外側transactionを明示する。
        db.execute(text("BEGIN"))
        root = _manager(db).commit(
            _user(),
            body={"name": "vm-1"},
            idempotency_key="atomic-operation",
            lease_id="lease-1",
            resolved_targets=AGENT_TARGET,
            commit_transaction=False,
        )
        _manager(db, method="put").commit(
            _user(),
            dep_uuid=root.uuid,
            lease_id="lease-1",
            commit_transaction=False,
        )
        assert db.query(TaskModel).count() == 2
        db.rollback()
        assert db.query(TaskModel).count() == 0


def test_idempotency_replay_can_leave_outer_transaction_uncommitted(
    db_factory: sessionmaker[Session],
) -> None:
    with db_factory() as db:
        original = _manager(db).commit(
            _user(),
            body={"name": "vm-1"},
            idempotency_key="atomic-replay",
        )
        db.execute(text("INSERT INTO transaction_markers (id) VALUES (2)"))
        replay_manager = _manager(db)
        replay = replay_manager.commit(
            _user(),
            body={"name": "vm-1"},
            idempotency_key="atomic-replay",
            commit_transaction=False,
        )
        assert replay.uuid == original.uuid
        db.rollback()
        marker_count = db.execute(
            text("SELECT count(*) FROM transaction_markers"),
        ).scalar_one()
        assert marker_count == 0


def test_operation_aggregates_dependency_chain_and_status(
    db_factory: sessionmaker[Session],
) -> None:
    with db_factory() as db:
        root = _manager(db).commit(_user(), body={"name": "vm-1"})
        child_manager = _manager(db, method="put")
        child = child_manager.commit(_user(), dep_uuid=root.uuid)

        root.status = "finish"
        child.status = "reconciling"
        db.commit()
        operation = get_operation(db, root.uuid)
        assert operation["operation_id"] == root.uuid
        assert operation["task_ids"] == [root.uuid, child.uuid]
        assert operation["normalized_status"] == "running"

        child.status = "unknown"
        child.error_code = "RESULT_UNKNOWN"
        child.retryable = True
        db.commit()
        operation = get_operation(db, root.uuid)
        assert operation["normalized_status"] == "unknown"
        assert operation["error_code"] == "RESULT_UNKNOWN"
        assert operation["retryable"] is False

        child.status = "error"
        child.retryable = True
        db.commit()
        operation = get_operation(db, root.uuid)
        assert operation["normalized_status"] == "failed"
        assert operation["retryable"] is True


def test_operation_cancellation_checks_principal_and_cancels_queue(
    db_factory: sessionmaker[Session],
) -> None:
    with db_factory() as db:
        root = _manager(db).commit(_user(), body={"name": "vm-1"})
        child = _manager(db, method="put").commit(_user(), dep_uuid=root.uuid)

        with pytest.raises(TaskOwnershipError):
            request_cancel_operation(db, root.uuid, "different-user")
        assert root.status == "init"
        assert child.status == "wait"

        operation = request_cancel_operation(db, root.uuid, "agent-user")
        assert operation["normalized_status"] == "cancelled"
        assert {root.status, child.status} == {"cancelled"}


def test_operation_cancellation_marks_running_task_as_requested(
    db_factory: sessionmaker[Session],
) -> None:
    with db_factory() as db:
        root = _manager(db).commit(_user(), body={"name": "vm-1"})
        root.status = "start"
        db.commit()

        operation = request_cancel_operation(db, root.uuid, "agent-user")
        assert operation["normalized_status"] == "cancel_requested"
        assert root.status == "cancel_requested"
        assert root.error_code == "TASK_CANCEL_REQUESTED"


def test_operation_cancellation_can_share_outer_audit_transaction(
    db_factory: sessionmaker[Session],
) -> None:
    with db_factory() as db:
        root = _manager(db).commit(_user(), body={"name": "vm-1"})
        db.execute(text("INSERT INTO transaction_markers (id) VALUES (10)"))

        operation = request_cancel_operation(
            db,
            root.uuid,
            "agent-user",
            commit_transaction=False,
        )
        assert operation["normalized_status"] == "cancelled"
        db.rollback()

        persisted = _required_task(db.get(TaskModel, root.uuid))
        assert persisted.status == "init"
        marker_count = db.execute(
            text("SELECT count(*) FROM transaction_markers WHERE id = 10"),
        ).scalar_one()
        assert marker_count == 0


def test_operation_cancellation_releases_agent_target_reservation(
    db_factory: sessionmaker[Session],
) -> None:
    with db_factory() as db:
        root = _manager(db).commit(
            _user(),
            body={"name": "vm-1"},
            idempotency_key="cancel-reservation",
            lease_id="lease-1",
            resolved_targets=AGENT_TARGET,
        )
        _manager(db, method="put").commit(
            _user(),
            dep_uuid=root.uuid,
            lease_id="lease-1",
        )
        acquire_target_reservations(
            db,
            resolved_targets=_required_resolved_targets(root),
            correlation_id=_required_correlation_id(root),
            lease_id=_required_lease_id(root),
        )
        db.commit()

        operation = request_cancel_operation(db, root.uuid, "agent-user")

        assert operation["normalized_status"] == "cancelled"
        assert db.query(TaskTargetReservationModel).count() == 0


def test_agent_policy_is_fail_closed_when_validator_is_missing(
    db_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(task_functions, "_load_agent_policy_function", lambda _: None)
    with db_factory() as db:
        legacy = _manager(db).commit(_user(), body={"name": "legacy"})
        evaluate_dispatch_policy(db, legacy)

        agent = _manager(db).commit(
            _user(),
            body={"name": "agent"},
            idempotency_key="request-0004",
            lease_id="lease-1",
            resolved_targets=AGENT_TARGET,
        )
        acquire_target_reservations(
            db,
            resolved_targets=_required_resolved_targets(agent),
            correlation_id=_required_correlation_id(agent),
            lease_id=_required_lease_id(agent),
        )
        with pytest.raises(TaskPolicyUnavailable):
            evaluate_dispatch_policy(db, agent)


def test_agent_policy_rejects_task_without_lease(
    db_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        task_functions,
        "_load_agent_policy_function",
        lambda _: lambda _db, _task: None,
    )
    with db_factory() as db:
        agent = _manager(db).commit(
            _user(),
            body={"name": "agent"},
            idempotency_key="request-without-lease",
        )
        with pytest.raises(TaskDispatchRejected) as exc_info:
            evaluate_dispatch_policy(db, agent)
        assert exc_info.value.error_code == "TASK_LEASE_REQUIRED"


def test_agent_request_is_encrypted_at_rest_and_redacted_from_response(
    db_factory: sessionmaker[Session],
) -> None:
    secret = "#cloud-config\npassword: DoNotPersistThis!"
    with db_factory() as db:
        task = _manager(db).commit(
            _user(),
            body={"cloudInit": {"userData": secret}},
            idempotency_key="request-secret",
            lease_id="lease-1",
            resolved_targets=AGENT_TARGET,
        )

        assert is_encrypted_task_request(task.request)
        assert secret not in str(task.request)
        decrypted = json.loads(
            decrypt_task_request(task.request, task_uuid=task.uuid),
        )
        assert decrypted["body"]["cloudInit"]["userData"] == secret

        response = Task.model_validate(task).model_dump(mode="json")
        assert response["request"] == {"redacted": True}
        assert secret not in json.dumps(response)


def test_legacy_rest_request_keeps_existing_plain_json_contract(
    db_factory: sessionmaker[Session],
) -> None:
    with db_factory() as db:
        task = _manager(db).commit(
            _user(),
            body={"name": "legacy-vm"},
        )

        assert not is_encrypted_task_request(task.request)
        assert json.loads(task.request)["body"] == {"name": "legacy-vm"}
        response = Task.model_validate(task).model_dump(mode="json")
        assert response["request"]["body"] == {"name": "legacy-vm"}


def test_agent_request_encryption_key_is_required(
    db_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("AGENT_TASK_ENCRYPTION_KEY")
    with db_factory() as db:
        with pytest.raises(TaskRequestEncryptionConfigurationError):
            _manager(db).commit(
                _user(),
                body={"cloudInit": {"userData": "secret"}},
                idempotency_key="request-no-key",
                lease_id="lease-1",
                resolved_targets=AGENT_TARGET,
            )
        assert db.query(TaskModel).count() == 0


def test_task_runner_commits_handler_database_updates(
    db_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with db_factory() as db:
        task = _manager(db).commit(
            _user(),
            body={"name": "agent"},
            idempotency_key="request-handler-commit",
            lease_id="lease-1",
            resolved_targets=AGENT_TARGET,
        )
        task_uuid = task.uuid

    manager = TaskBase()

    @manager("post.vm.root")
    def handler(db: Session, model: TaskModel, req: object) -> None:
        del db, req
        model.message = "handlerのDB更新"

    monkeypatch.setattr(task_functions, "SessionLocal", db_factory)
    monkeypatch.setattr(
        task_functions,
        "evaluate_dispatch_policy",
        lambda _db, _task: None,
    )
    manager.run("post.vm.root", task_uuid)

    with db_factory() as db:
        persisted = _required_task(db.get(TaskModel, task_uuid))
        assert persisted is not None
        assert persisted.message == "handlerのDB更新"


def test_task_runner_rechecks_policy_while_target_lock_is_held(
    db_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with db_factory() as db:
        task = _manager(db).commit(
            _user(),
            body={"name": "agent"},
            idempotency_key="request-lock-policy",
            lease_id="lease-1",
            resolved_targets=AGENT_TARGET,
        )
        acquire_target_reservations(
            db,
            resolved_targets=_required_resolved_targets(task),
            correlation_id=_required_correlation_id(task),
            lease_id=_required_lease_id(task),
        )
        db.commit()
        task_uuid = task.uuid

    manager = TaskBase()
    handler_called = False
    lock_active = False
    original_locks = task_functions.task_target_advisory_locks

    @manager("post.vm.root")
    def handler(db: Session, model: TaskModel, req: object) -> None:
        nonlocal handler_called
        del db, model, req
        assert lock_active is True
        handler_called = True

    @contextmanager
    def observed_locks(
        db: Session,
        task: TaskModel,
    ) -> Iterator[tuple[tuple[int, str], ...]]:
        nonlocal lock_active
        with original_locks(db, task) as lock_keys:
            lock_active = True
            try:
                yield lock_keys
            finally:
                lock_active = False

    def validate_after_lock(db: Session, task: TaskModel) -> None:
        del db, task
        assert lock_active is True

    monkeypatch.setattr(task_functions, "SessionLocal", db_factory)
    monkeypatch.setattr(
        task_functions,
        "task_target_advisory_locks",
        observed_locks,
    )
    monkeypatch.setattr(
        task_functions,
        "evaluate_dispatch_policy",
        validate_after_lock,
    )

    manager.run("post.vm.root", task_uuid)

    assert handler_called is True
    assert lock_active is False


def test_task_runner_rejects_target_changed_while_waiting_for_lock(
    db_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with db_factory() as db:
        task = _manager(db).commit(
            _user(),
            body={"name": "agent"},
            idempotency_key="request-lock-target-change",
            lease_id="lease-1",
            resolved_targets=AGENT_TARGET,
        )
        task_uuid = task.uuid

    manager = TaskBase()
    handler_called = False

    @manager("post.vm.root")
    def handler(db: Session, model: TaskModel, req: object) -> None:
        nonlocal handler_called
        del db, model, req
        handler_called = True

    @contextmanager
    def change_target_during_lock_wait(
        db: Session,
        task: TaskModel,
    ) -> Iterator[tuple[tuple[int, str], ...]]:
        original_specs = task_functions._task_target_advisory_lock_specs(task)
        task.resolved_targets = [{"resourceType": "vm", "resourceId": "vm-2"}]
        db.commit()
        yield original_specs

    monkeypatch.setattr(task_functions, "SessionLocal", db_factory)
    monkeypatch.setattr(
        task_functions,
        "task_target_advisory_locks",
        change_target_during_lock_wait,
    )

    with pytest.raises(TaskDispatchRejected) as exc_info:
        manager.run("post.vm.root", task_uuid)

    assert exc_info.value.error_code == "TASK_RESOLVED_TARGET_CHANGED"
    assert handler_called is False


def test_worker_rejects_policy_failure_before_handler(
    db_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import worker

    with db_factory() as db:
        task = _manager(db).commit(
            _user(),
            body={"name": "agent"},
            idempotency_key="request-0005",
            lease_id="lease-1",
            resolved_targets=AGENT_TARGET,
        )
        task_uuid = task.uuid

    monkeypatch.setattr(worker, "SessionLocal", db_factory)
    monkeypatch.setattr(task_functions, "SessionLocal", db_factory)
    monkeypatch.setattr(
        task_functions,
        "evaluate_dispatch_policy",
        lambda _db, _task: None,
    )
    monkeypatch.setattr(
        worker,
        "evaluate_dispatch_policy",
        lambda _db, _task: (_ for _ in ()).throw(
            TaskDispatchRejected(
                "leaseが失効しています",
                error_code="LEASE_REVOKED",
            )
        ),
    )
    monkeypatch.setattr(worker, "record_worker_outcome", lambda _db, _task: None)

    worker.exec_task(TaskBase(), task_uuid)

    with db_factory() as db:
        rejected = db.query(TaskModel).filter(TaskModel.uuid == task_uuid).one()
        assert rejected.status == "error"
        assert rejected.error_code == "LEASE_REVOKED"


def test_worker_holds_reservation_when_outcome_audit_fails(
    db_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import worker

    with db_factory() as db:
        task = _manager(db).commit(
            _user(),
            body={"name": "agent"},
            idempotency_key="request-audit-failure-reservation",
            lease_id="lease-1",
            resolved_targets=AGENT_TARGET,
        )
        acquire_target_reservations(
            db,
            resolved_targets=_required_resolved_targets(task),
            correlation_id=_required_correlation_id(task),
            lease_id=_required_lease_id(task),
        )
        db.commit()
        task_uuid = task.uuid

    monkeypatch.setattr(worker, "SessionLocal", db_factory)
    monkeypatch.setattr(
        worker,
        "evaluate_dispatch_policy",
        lambda _db, _task: (_ for _ in ()).throw(
            TaskDispatchRejected(
                "leaseが失効しています",
                error_code="LEASE_REVOKED",
            ),
        ),
    )
    monkeypatch.setattr(
        worker,
        "record_worker_outcome",
        lambda _db, _task: (_ for _ in ()).throw(RuntimeError("audit unavailable")),
    )

    worker.exec_task(TaskBase(), task_uuid)

    with db_factory() as db:
        uncertain = _required_task(db.get(TaskModel, task_uuid))
        assert uncertain.status == "unknown"
        assert uncertain.error_code == "TASK_OUTCOME_AUDIT_FAILED"
        assert db.query(TaskTargetReservationModel).count() == 2


def test_worker_marks_cancelled_when_request_arrives_during_lock_wait(
    db_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import worker

    with db_factory() as db:
        task = _manager(db).commit(
            _user(),
            body={"name": "agent"},
            idempotency_key="request-cancel-lock-wait",
            lease_id="lease-1",
            resolved_targets=AGENT_TARGET,
        )
        acquire_target_reservations(
            db,
            resolved_targets=_required_resolved_targets(task),
            correlation_id=_required_correlation_id(task),
            lease_id=_required_lease_id(task),
        )
        db.commit()
        task_uuid = task.uuid

    manager = TaskBase()
    handler_called = False

    @manager("post.vm.root")
    def must_not_run(db: Session, model: TaskModel, req: object) -> None:
        nonlocal handler_called
        del db, model, req
        handler_called = True

    def release_on_terminal(db: Session, task: TaskModel) -> None:
        release_target_reservations_if_terminal(db, _required_correlation_id(task))

    monkeypatch.setattr(worker, "SessionLocal", db_factory)
    monkeypatch.setattr(task_functions, "SessionLocal", db_factory)
    monkeypatch.setattr(worker, "evaluate_dispatch_policy", lambda _db, _task: None)
    monkeypatch.setattr(
        task_functions,
        "evaluate_dispatch_policy",
        lambda _db, _task: (_ for _ in ()).throw(
            TaskCancellationRequested("taskのキャンセルが要求されています"),
        ),
    )
    monkeypatch.setattr(worker, "record_worker_outcome", release_on_terminal)

    worker.exec_task(manager, task_uuid)

    with db_factory() as db:
        cancelled = _required_task(db.get(TaskModel, task_uuid))
        assert handler_called is False
        assert cancelled.status == "cancelled"
        assert cancelled.error_code == "TASK_CANCELLED"
        assert cancelled.retryable is False
        assert db.query(TaskTargetReservationModel).count() == 0


def test_worker_marks_unknown_when_outcome_recording_fails(
    db_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import worker

    with db_factory() as db:
        task = _manager(db).commit(
            _user(),
            body={"name": "agent"},
            idempotency_key="request-0006",
            lease_id="lease-1",
            resolved_targets=AGENT_TARGET,
        )
        task_uuid = task.uuid

    manager = TaskBase()

    @manager("post.vm.root")
    def successful_handler(db: Session, model: TaskModel, req: object) -> None:
        model.result = {"ok": True}
        db.commit()

    monkeypatch.setattr(worker, "SessionLocal", db_factory)
    monkeypatch.setattr(task_functions, "SessionLocal", db_factory)
    monkeypatch.setattr(
        task_functions,
        "evaluate_dispatch_policy",
        lambda _db, _task: None,
    )
    monkeypatch.setattr(worker, "evaluate_dispatch_policy", lambda _db, _task: None)
    monkeypatch.setattr(
        worker,
        "record_worker_outcome",
        lambda _db, _task, **_kwargs: (_ for _ in ()).throw(
            RuntimeError("audit unavailable")
        ),
    )

    worker.exec_task(manager, task_uuid)

    with db_factory() as db:
        unknown = db.query(TaskModel).filter(TaskModel.uuid == task_uuid).one()
        assert unknown.status == "unknown"
        assert unknown.error_code == "TASK_OUTCOME_PERSISTENCE_FAILED"
        assert unknown.retryable is False


def test_worker_marks_agent_handler_failure_after_effect_unknown(
    db_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import worker

    with db_factory() as db:
        task = _manager(db).commit(
            _user(),
            body={"name": "agent"},
            idempotency_key="request-handler-failure-after-effect",
            lease_id="lease-1",
            resolved_targets=AGENT_TARGET,
        )
        task_uuid = task.uuid

    manager = TaskBase()
    effect_started = False

    @manager("post.vm.root")
    def failing_handler(db: Session, model: TaskModel, req: object) -> None:
        nonlocal effect_started
        del db, model, req
        effect_started = True
        raise RuntimeError("provider node returned HTTP 500")

    monkeypatch.setattr(worker, "SessionLocal", db_factory)
    monkeypatch.setattr(task_functions, "SessionLocal", db_factory)
    monkeypatch.setattr(worker, "evaluate_dispatch_policy", lambda _db, _task: None)
    monkeypatch.setattr(
        task_functions,
        "evaluate_dispatch_policy",
        lambda _db, _task: None,
    )
    monkeypatch.setattr(worker, "record_worker_outcome", lambda _db, _task: None)

    worker.exec_task(manager, task_uuid)

    with db_factory() as db:
        unknown = _required_task(db.get(TaskModel, task_uuid))
        assert effect_started is True
        assert unknown.status == "unknown"
        assert unknown.error_code == "TASK_EXECUTION_OUTCOME_UNKNOWN"
        assert unknown.retryable is False
        assert unknown.message is not None
        assert "HTTP 500" not in unknown.message


def test_worker_releases_reservation_only_after_success_commit_ack(
    db_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import worker

    with db_factory() as db:
        task = _manager(db).commit(
            _user(),
            body={"name": "agent"},
            idempotency_key="success-reservation-release",
            lease_id="lease-1",
            resolved_targets=AGENT_TARGET,
        )
        acquire_target_reservations(
            db,
            resolved_targets=_required_resolved_targets(task),
            correlation_id=_required_correlation_id(task),
            lease_id=_required_lease_id(task),
        )
        task.status = "reconciling"
        db.commit()
        task_uuid = task.uuid

    release_flags: list[bool] = []

    def record_outcome(
        db: Session,
        task: TaskModel,
        *,
        release_reservations: bool = True,
    ) -> None:
        release_flags.append(release_reservations)
        if release_reservations:
            release_target_reservations_if_terminal(db, _required_correlation_id(task))

    monkeypatch.setattr(worker, "SessionLocal", db_factory)
    monkeypatch.setattr(worker, "record_worker_outcome", record_outcome)

    worker._mark_finished(task_uuid, run_time=1.0)

    with db_factory() as db:
        assert _required_task(db.get(TaskModel, task_uuid)).status == "finish"
        assert db.query(TaskTargetReservationModel).count() == 2

    worker._release_finished_target_reservations(task_uuid)

    with db_factory() as db:
        assert db.query(TaskTargetReservationModel).count() == 0
    assert release_flags == [False]


def test_worker_commit_ambiguity_keeps_unknown_reservation(
    db_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import worker

    with db_factory() as db:
        task = _manager(db).commit(
            _user(),
            body={"name": "agent"},
            idempotency_key="ambiguous-success-commit",
            lease_id="lease-1",
            resolved_targets=AGENT_TARGET,
        )
        acquire_target_reservations(
            db,
            resolved_targets=_required_resolved_targets(task),
            correlation_id=_required_correlation_id(task),
            lease_id=_required_lease_id(task),
        )
        task.status = "reconciling"
        db.commit()
        task_uuid = task.uuid

    class AmbiguousSessionLocal:
        @staticmethod
        @contextmanager
        def begin() -> Iterator[Session]:
            with db_factory() as db:
                yield db
                # DB server側ではcommit済みだが、応答だけ失われた状態を再現する。
                db.commit()
                raise RuntimeError("commit acknowledgment lost")

    def record_outcome(
        db: Session,
        task: TaskModel,
        *,
        release_reservations: bool = True,
    ) -> None:
        if release_reservations:
            release_target_reservations_if_terminal(db, _required_correlation_id(task))

    monkeypatch.setattr(worker, "SessionLocal", AmbiguousSessionLocal)
    monkeypatch.setattr(worker, "record_worker_outcome", record_outcome)

    with pytest.raises(RuntimeError, match="acknowledgment") as exc_info:
        worker._mark_finished(task_uuid, run_time=1.0)

    monkeypatch.setattr(worker, "SessionLocal", db_factory)
    worker._persist_unknown_after_effect(
        task_uuid,
        exc_info.value,
        run_time=1.0,
    )

    with db_factory() as db:
        task = _required_task(db.get(TaskModel, task_uuid))
        assert task.status == "unknown"
        assert task.error_code == "TASK_OUTCOME_PERSISTENCE_FAILED"
        assert db.query(TaskTargetReservationModel).count() == 2


def test_worker_rejects_tampered_encrypted_request_before_handler(
    db_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import worker

    secret = "sensitive-cloud-init-value"
    with db_factory() as db:
        task = _manager(db).commit(
            _user(),
            body={"cloudInit": {"userData": secret}},
            idempotency_key="request-tampered",
            lease_id="lease-1",
            resolved_targets=AGENT_TARGET,
        )
        wrapper = json.loads(task.request)
        first = wrapper["ciphertext"][0]
        wrapper["ciphertext"] = ("A" if first != "A" else "B") + wrapper[
            "ciphertext"
        ][1:]
        task.request = json.dumps(wrapper)
        task_uuid = task.uuid
        db.commit()

    handler_called = False
    manager = TaskBase()

    @manager("post.vm.root")
    def must_not_run(db: Session, model: TaskModel, req: object) -> None:
        nonlocal handler_called
        handler_called = True

    monkeypatch.setattr(worker, "SessionLocal", db_factory)
    monkeypatch.setattr(task_functions, "SessionLocal", db_factory)
    monkeypatch.setattr(
        task_functions,
        "evaluate_dispatch_policy",
        lambda _db, _task: None,
    )
    monkeypatch.setattr(worker, "evaluate_dispatch_policy", lambda _db, _task: None)
    monkeypatch.setattr(worker, "record_worker_outcome", lambda _db, _task: None)

    worker.exec_task(manager, task_uuid)

    with db_factory() as db:
        failed = db.query(TaskModel).filter(TaskModel.uuid == task_uuid).one()
        assert handler_called is False
        assert failed.status == "error"
        assert failed.error_code == "TASK_REQUEST_DECRYPTION_FAILED"
        assert failed.retryable is False
        assert secret not in str(failed.message)
        assert secret not in str(failed.log)


def test_worker_restart_marks_inflight_task_unknown(
    db_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import worker

    with db_factory() as db:
        task = _manager(db).commit(
            _user(),
            body={"name": "agent"},
            idempotency_key="request-0007",
            lease_id="lease-1",
            resolved_targets=AGENT_TARGET,
        )
        task.status = "start"
        task_uuid = task.uuid
        db.commit()

    monkeypatch.setattr(worker, "SessionLocal", db_factory)
    monkeypatch.setattr(worker, "record_worker_outcome", lambda _db, _task: None)
    worker.init_scheduler()

    with db_factory() as db:
        recovered = db.query(TaskModel).filter(TaskModel.uuid == task_uuid).one()
        assert recovered.status == "unknown"
        assert recovered.error_code == "WORKER_RESTARTED_OUTCOME_UNKNOWN"
        assert recovered.retryable is False


def test_worker_restart_preserves_legacy_lost_semantics_and_agent_queue(
    db_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import worker

    with db_factory() as db:
        legacy_queued = _manager(db).commit(
            _user(),
            body={"name": "legacy-queued"},
        )
        legacy_started = _manager(db).commit(
            _user(),
            body={"name": "legacy-started"},
        )
        legacy_started.status = "start"
        agent_queued = _manager(db).commit(
            _user(),
            body={"name": "agent-queued"},
            idempotency_key="request-agent-queued-restart",
            lease_id="lease-1",
            resolved_targets=AGENT_TARGET,
        )
        task_ids = (legacy_queued.uuid, legacy_started.uuid, agent_queued.uuid)
        db.commit()

    monkeypatch.setattr(worker, "SessionLocal", db_factory)
    monkeypatch.setattr(worker, "record_worker_outcome", lambda _db, _task: None)
    worker.init_scheduler()

    with db_factory() as db:
        legacy_queued = _required_task(db.get(TaskModel, task_ids[0]))
        legacy_started = _required_task(db.get(TaskModel, task_ids[1]))
        agent_queued = _required_task(db.get(TaskModel, task_ids[2]))
        assert legacy_queued.status == "lost"
        assert legacy_started.status == "lost"
        assert legacy_started.error_code == "WORKER_RESTARTED_TASK_LOST"
        assert agent_queued.status == "init"


@pytest.mark.parametrize(
    ("dependency_status", "expected_status", "expected_reservations"),
    [
        ("unknown", "cancelled", 2),
        ("error", "error", 0),
        ("cancelled", "cancelled", 0),
    ],
)
def test_worker_stops_serial_dependency_chain_after_unfinished_task(
    db_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    dependency_status: str,
    expected_status: str,
    expected_reservations: int,
) -> None:
    import worker

    with db_factory() as db:
        root = _manager(db).commit(
            _user(),
            body={"step": "root"},
            idempotency_key=f"serial-chain-{dependency_status}",
            lease_id="lease-serial-chain",
            resolved_targets=AGENT_TARGET,
        )
        first = _manager(db, method="put").commit(
            _user(),
            body={"step": "first"},
            dep_uuid=root.uuid,
            lease_id=_required_lease_id(root),
        )
        second = _manager(db, method="delete").commit(
            _user(),
            body={"step": "second"},
            dep_uuid=first.uuid,
            lease_id=_required_lease_id(root),
        )
        acquire_target_reservations(
            db,
            resolved_targets=_required_resolved_targets(root),
            correlation_id=_required_correlation_id(root),
            lease_id=_required_lease_id(root),
        )
        root.status = "finish"
        first.status = dependency_status
        db.commit()
        second_uuid = second.uuid

    def record_and_release(db: Session, task: TaskModel) -> None:
        release_target_reservations_if_terminal(db, _required_correlation_id(task))

    monkeypatch.setattr(worker, "SessionLocal", db_factory)
    monkeypatch.setattr(worker, "record_worker_outcome", record_and_release)
    worker.run_scheduler(TaskBase())

    with db_factory() as db:
        stopped = _required_task(db.get(TaskModel, second_uuid))
        assert stopped.status == expected_status
        assert db.query(TaskTargetReservationModel).count() == expected_reservations


def test_worker_resumes_serial_dependency_after_reconciliation(
    db_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import worker

    with db_factory() as db:
        root = _manager(db).commit(
            _user(),
            body={"step": "root"},
            idempotency_key="serial-chain-reconciled",
            lease_id="lease-serial-chain",
            resolved_targets=AGENT_TARGET,
        )
        dependent = _manager(db, method="put").commit(
            _user(),
            body={"step": "dependent"},
            dep_uuid=root.uuid,
            lease_id=_required_lease_id(root),
        )
        acquire_target_reservations(
            db,
            resolved_targets=_required_resolved_targets(root),
            correlation_id=_required_correlation_id(root),
            lease_id=_required_lease_id(root),
        )
        # WebAuthn付きreconcileで外部効果ありと確定した状態を再現する。
        root.status = "finish"
        db.commit()
        dependent_uuid = dependent.uuid

    dispatched: list[str] = []
    monkeypatch.setattr(worker, "SessionLocal", db_factory)
    monkeypatch.setattr(
        worker,
        "exec_task",
        lambda *, task_manager, task_uuid: dispatched.append(task_uuid),
    )

    # 1回目で直列chainの次taskをdispatch可能状態へ遷移させる。
    worker.run_scheduler(TaskBase())
    with db_factory() as db:
        assert _required_task(db.get(TaskModel, dependent_uuid)).status == "init"
        # 後続処理が終わるまではoperation reservationを維持する。
        assert db.query(TaskTargetReservationModel).count() == 2

    # 次のscheduler cycleで確実にworker dispatch対象になる。
    worker.run_scheduler(TaskBase())
    assert dispatched == [dependent_uuid]
