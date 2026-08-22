import hashlib
import importlib
import json
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from time import time
from typing import Any, Callable, Iterator

from fastapi import BackgroundTasks
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from mixin.database import SessionLocal
from mixin.log import setup_logger
from mixin.schemas import BaseSchema
from task.crypto import (
    decrypt_task_request,
    encrypt_task_request,
    is_encrypted_task_request,
)
from task.models import TaskModel, TaskTargetReservationModel
from task.schemas import OperationStatus, TaskOperation, TaskRequest

logger = setup_logger(__name__)

QUEUED_STATUSES = frozenset({"init", "wait"})
RUNNING_STATUSES = frozenset({"start", "reconciling"})
ARCHIVABLE_STATUSES = frozenset({"finish", "error", "lost", "cancelled"})
RESERVATION_RELEASABLE_STATUSES = frozenset(
    ARCHIVABLE_STATUSES,
)
AGENT_POLICY_MODULE = "agent.policy"


class TaskError(Exception):
    """task制御で利用する基底例外。"""

    error_code = "TASK_ERROR"
    retryable = False
    outcome_unknown = False
    safe_message = True

    def __init__(
        self,
        message: str,
        *,
        error_code: str | None = None,
        retryable: bool | None = None,
    ) -> None:
        super().__init__(message)
        if error_code is not None:
            self.error_code = error_code
        if retryable is not None:
            self.retryable = retryable


class TaskNotFoundError(TaskError):
    error_code = "TASK_NOT_FOUND"


class TaskOwnershipError(TaskError):
    error_code = "TASK_PRINCIPAL_MISMATCH"


class TaskIdempotencyConflict(TaskError):
    error_code = "IDEMPOTENCY_KEY_CONFLICT"


class TaskDispatchRejected(TaskError):
    error_code = "TASK_DISPATCH_REJECTED"


class TaskCancellationRequested(TaskDispatchRejected):
    error_code = "TASK_CANCEL_REQUESTED"
    cancelled = True


class TaskTargetBusy(TaskDispatchRejected):
    error_code = "TARGET_BUSY"
    retryable = True


class TaskPolicyUnavailable(TaskDispatchRejected):
    error_code = "AGENT_POLICY_UNAVAILABLE"
    retryable = True


def _json_compatible(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json", by_alias=True)
    if isinstance(value, dict):
        return {str(key): _json_compatible(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_compatible(item) for item in value]
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def calculate_task_request_hash(
    *,
    method: str,
    resource: str,
    object_name: str,
    path_param: Any = None,
    body: Any = None,
    dependence_uuid: str | None = None,
    expected_generation: Any = None,
    resolved_targets: list[Any] | None = None,
) -> str:
    """taskの副作用を一意に表すcanonical SHA-256を返す。"""

    payload = {
        "method": method,
        "resource": resource,
        "object": object_name,
        "pathParam": _json_compatible(path_param if path_param is not None else {}),
        "body": _json_compatible(body),
        "dependenceUuid": dependence_uuid,
        "expectedGeneration": _json_compatible(expected_generation),
        "resolvedTargets": _json_compatible(resolved_targets),
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _load_agent_policy_function(name: str) -> Callable[..., Any] | None:
    try:
        module = importlib.import_module(AGENT_POLICY_MODULE)
    except ModuleNotFoundError as exc:
        if exc.name in {"agent", AGENT_POLICY_MODULE}:
            return None
        raise TaskPolicyUnavailable(
            "Agent policyの依存moduleを読み込めません",
        ) from exc
    except Exception as exc:
        raise TaskPolicyUnavailable(
            "Agent policyを読み込めません",
        ) from exc

    function = getattr(module, name, None)
    return function if callable(function) else None


def is_agent_task(task: TaskModel) -> bool:
    return bool(task.lease_id or task.idempotency_key)


@dataclass(frozen=True)
class TargetReservationSpec:
    target_key: str
    lock_mode: str


def _target_reservation_key(*parts: str) -> str:
    canonical = json.dumps(parts, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(
        f"virty-agent-target-lock:v2:{canonical}".encode("utf-8"),
    ).hexdigest()


def calculate_target_reservation_specs(
    targets: Any,
) -> tuple[TargetReservationSpec, ...]:
    """resolved targetをresource/family/globalのreader-writer lockへ展開する。"""

    if isinstance(targets, dict):
        targets = [targets]
    if not isinstance(targets, list) or not targets:
        raise TaskDispatchRejected(
            "Agent taskのresolved targetがありません",
            error_code="TASK_RESOLVED_TARGET_REQUIRED",
        )

    modes_by_key: dict[str, str] = {}

    def add_spec(target_key: str, lock_mode: str) -> None:
        current = modes_by_key.get(target_key)
        if current == "exclusive" or current == lock_mode:
            return
        # 同operation内でshared/exclusiveが重なればexclusiveへ縮約する。
        modes_by_key[target_key] = (
            "exclusive" if lock_mode == "exclusive" else current or "shared"
        )

    for target in targets:
        if not isinstance(target, dict):
            raise TaskDispatchRejected(
                "Agent taskのresolved target形式が不正です",
                error_code="TASK_RESOLVED_TARGET_INVALID",
            )
        resource_type = target.get("resourceType") or target.get("resource_type")
        resource_id = target.get("resourceId") or target.get("resource_id")
        if not resource_type or resource_id is None or str(resource_id) == "":
            raise TaskDispatchRejected(
                "Agent taskのresolved target形式が不正です",
                error_code="TASK_RESOLVED_TARGET_INVALID",
            )
        normalized_type = str(resource_type).strip().lower()
        normalized_id = str(resource_id)
        scope = str(
            target.get("reservationScope")
            or target.get("reservation_scope")
            or "resource"
        ).lower()
        requested_mode = target.get("reservationMode") or target.get(
            "reservation_mode"
        )
        mode = str(requested_mode).lower() if requested_mode is not None else None
        if mode not in {None, "shared", "exclusive"}:
            raise TaskDispatchRejected(
                "Agent taskのreservation modeが不正です",
                error_code="TASK_RESERVATION_MODE_INVALID",
            )

        if scope == "resource":
            if mode not in {None, "exclusive"}:
                raise TaskDispatchRejected(
                    "resource reservationはexclusiveである必要があります",
                    error_code="TASK_RESERVATION_MODE_INVALID",
                )
            add_spec(
                _target_reservation_key(
                    "resource",
                    normalized_type,
                    normalized_id,
                ),
                "exclusive",
            )
            # family変更と競合しつつ、別resource同士は並行できるshared guard。
            add_spec(
                _target_reservation_key("family", normalized_type),
                "shared",
            )
        elif scope == "family":
            if mode not in {None, "exclusive"}:
                raise TaskDispatchRejected(
                    "family reservationはexclusiveである必要があります",
                    error_code="TASK_RESERVATION_MODE_INVALID",
                )
            add_spec(
                _target_reservation_key("family", normalized_type),
                "exclusive",
            )
        elif scope == "global":
            add_spec(
                _target_reservation_key(
                    "global",
                    normalized_type,
                    normalized_id,
                ),
                mode or "exclusive",
            )
        else:
            raise TaskDispatchRejected(
                "Agent taskのreservation scopeが不正です",
                error_code="TASK_RESERVATION_SCOPE_INVALID",
            )

    return tuple(
        TargetReservationSpec(target_key=key, lock_mode=modes_by_key[key])
        for key in sorted(modes_by_key)
    )


def calculate_target_reservation_keys(targets: Any) -> tuple[str, ...]:
    """resolved targetから安定したreservation key一覧を返す。"""

    return tuple(
        spec.target_key for spec in calculate_target_reservation_specs(targets)
    )


def _advisory_key(namespace: str, target_key: str) -> int:
    digest = hashlib.sha256(f"{namespace}:{target_key}".encode("ascii")).digest()
    return int.from_bytes(digest[:8], byteorder="big", signed=True)


def _task_target_advisory_lock_specs(
    task: TaskModel,
) -> tuple[tuple[int, str], ...]:
    if not is_agent_task(task):
        return ()
    modes_by_key: dict[int, str] = {}
    for spec in calculate_target_reservation_specs(task.resolved_targets):
        lock_key = _advisory_key("runtime", spec.target_key)
        current = modes_by_key.get(lock_key)
        if current == "exclusive" or current == spec.lock_mode:
            continue
        modes_by_key[lock_key] = (
            "exclusive" if spec.lock_mode == "exclusive" else current or "shared"
        )
    return tuple((key, modes_by_key[key]) for key in sorted(modes_by_key))


def task_target_advisory_lock_keys(task: TaskModel) -> tuple[int, ...]:
    """resolved targetからPostgreSQL advisory lock用の安定keyを作る。"""

    return tuple(
        lock_key for lock_key, _ in _task_target_advisory_lock_specs(task)
    )


def _operation_allows_reservation_release(
    db: Session,
    correlation_id: str,
) -> bool:
    statuses = [
        row[0]
        for row in db.query(TaskModel.status)
        .filter(TaskModel.correlation_id == correlation_id)
        .all()
    ]
    return bool(statuses) and all(
        status in RESERVATION_RELEASABLE_STATUSES for status in statuses
    )


def _insert_target_reservation(
    db: Session,
    *,
    spec: TargetReservationSpec,
    correlation_id: str,
    lease_id: str,
) -> None:
    reservation_id = hashlib.sha256(
        f"{spec.target_key}:{correlation_id}".encode("utf-8"),
    ).hexdigest()
    db.add(
        TaskTargetReservationModel(
            reservation_id=reservation_id,
            target_key=spec.target_key,
            lock_mode=spec.lock_mode,
            correlation_id=correlation_id,
            lease_id=lease_id,
            acquired_at=datetime.now().astimezone(),
        ),
    )
    db.flush()


def _acquire_reservation_transaction_guards(
    db: Session,
    specs: tuple[TargetReservationSpec, ...],
) -> None:
    bind = db.get_bind()
    if bind.dialect.name != "postgresql":
        return
    for guard_key in sorted(
        {_advisory_key("reservation-transaction", spec.target_key) for spec in specs}
    ):
        db.execute(
            text("SELECT pg_advisory_xact_lock(:lock_key)"),
            {"lock_key": guard_key},
        )


def _reservation_is_held_or_raise(
    db: Session,
    *,
    spec: TargetReservationSpec,
    correlation_id: str,
    lease_id: str,
) -> bool:
    rows = (
        db.query(TaskTargetReservationModel)
        .filter(TaskTargetReservationModel.target_key == spec.target_key)
        .with_for_update()
        .all()
    )
    held_by_operation = False
    for row in rows:
        if row.correlation_id == correlation_id:
            if row.lease_id != lease_id:
                raise TaskDispatchRejected(
                    "同じoperationのtarget reservationでleaseが一致しません",
                    error_code="TASK_RESERVATION_LEASE_MISMATCH",
                )
            if row.lock_mode != spec.lock_mode:
                raise TaskDispatchRejected(
                    "同じoperationのtarget reservation modeが一致しません",
                    error_code="TASK_RESERVATION_MODE_MISMATCH",
                )
            held_by_operation = True
            continue
        if _operation_allows_reservation_release(db, row.correlation_id):
            db.delete(row)
            continue
        if spec.lock_mode == "shared" and row.lock_mode == "shared":
            continue
        raise TaskTargetBusy("targetは別のAgent operationが変更中です")
    db.flush()
    return held_by_operation


def acquire_target_reservations(
    db: Session,
    *,
    resolved_targets: Any,
    correlation_id: str,
    lease_id: str,
) -> tuple[str, ...]:
    """operation全体のtargetを確保し、競合中は安全側で拒否する。"""

    if not correlation_id or not lease_id:
        raise TaskDispatchRejected(
            "target reservationにcorrelation IDとlease IDが必要です",
            error_code="TASK_RESERVATION_METADATA_MISSING",
        )
    specs = calculate_target_reservation_specs(resolved_targets)
    # root task・監査など、先行する外側transactionを確定せずflushする。
    db.flush()
    # shared同士を許可しながら判定とINSERTを原子的にする短時間guard。
    _acquire_reservation_transaction_guards(db, specs)
    # 複数targetの途中で競合しても、先に確保したrowを外側へ残さない。
    with db.begin_nested():
        for spec in specs:
            if _reservation_is_held_or_raise(
                db,
                spec=spec,
                correlation_id=correlation_id,
                lease_id=lease_id,
            ):
                continue
            try:
                with db.begin_nested():
                    _insert_target_reservation(
                        db,
                        spec=spec,
                        correlation_id=correlation_id,
                        lease_id=lease_id,
                    )
            except IntegrityError:
                if _reservation_is_held_or_raise(
                    db,
                    spec=spec,
                    correlation_id=correlation_id,
                    lease_id=lease_id,
                ):
                    continue
                raise TaskTargetBusy(
                    "targetは別のAgent operationが変更中です",
                ) from None
    return tuple(spec.target_key for spec in specs)


def validate_target_reservations(db: Session, task: TaskModel) -> None:
    """dispatch対象が同じoperation・leaseで確保済みであることを検査する。"""

    if not is_agent_task(task):
        return
    if not task.correlation_id or not task.lease_id:
        raise TaskDispatchRejected(
            "Agent taskのtarget reservation metadataが不足しています",
            error_code="TASK_RESERVATION_METADATA_MISSING",
        )
    specs = calculate_target_reservation_specs(task.resolved_targets)
    reservations = (
        db.query(TaskTargetReservationModel)
        .filter(
            TaskTargetReservationModel.target_key.in_(
                [spec.target_key for spec in specs],
            ),
            TaskTargetReservationModel.correlation_id == task.correlation_id,
        )
        .all()
    )
    by_key = {reservation.target_key: reservation for reservation in reservations}
    for spec in specs:
        reservation = by_key.get(spec.target_key)
        if reservation is None:
            raise TaskDispatchRejected(
                "Agent taskのtarget reservationがありません",
                error_code="TASK_TARGET_RESERVATION_MISSING",
            )
        if (
            reservation.correlation_id != task.correlation_id
            or reservation.lease_id != task.lease_id
            or reservation.lock_mode != spec.lock_mode
        ):
            raise TaskDispatchRejected(
                "Agent taskのtarget reservationがoperationと一致しません",
                error_code="TASK_TARGET_RESERVATION_MISMATCH",
            )


def release_target_reservations_if_terminal(
    db: Session,
    correlation_id: str | None,
) -> bool:
    """全taskの効果が確定済みの場合だけreservationを解放する。"""

    if not correlation_id or not _operation_allows_reservation_release(
        db,
        correlation_id,
    ):
        return False
    reservations = (
        db.query(
            TaskTargetReservationModel.target_key,
            TaskTargetReservationModel.lock_mode,
        )
        .filter(TaskTargetReservationModel.correlation_id == correlation_id)
        .all()
    )
    if not reservations:
        return False
    # acquire/takeoverと同じ順序の短時間guardでmulti-target deadlockを防ぐ。
    _acquire_reservation_transaction_guards(
        db,
        tuple(
            TargetReservationSpec(target_key=row[0], lock_mode=row[1])
            for row in reservations
        ),
    )
    # guard待機中に状態が変わった場合も安全側で保持する。
    if not _operation_allows_reservation_release(db, correlation_id):
        return False
    deleted = (
        db.query(TaskTargetReservationModel)
        .filter(TaskTargetReservationModel.correlation_id == correlation_id)
        .delete(synchronize_session=False)
    )
    db.flush()
    return deleted > 0


def archive_terminal_tasks(
    db: Session,
    *,
    archived_at: datetime | None = None,
) -> list[TaskModel]:
    """確定済みtaskだけをsoft archiveし、Agent ledgerを保持する。"""

    tasks = (
        db.query(TaskModel)
        .filter(
            TaskModel.archived_at.is_(None),
            TaskModel.status.in_(ARCHIVABLE_STATUSES),
        )
        .order_by(TaskModel.uuid)
        .with_for_update()
        .all()
    )
    archive_time = archived_at or datetime.now().astimezone()
    for task in tasks:
        task.archived_at = archive_time
    db.flush()
    return tasks


def _release_postgresql_target_locks(
    connection: Connection,
    acquired: list[tuple[int, str]],
    *,
    task_uuid: str,
) -> None:
    invalidate = False
    for lock_key, lock_mode in reversed(acquired):
        try:
            unlock_function = (
                "pg_advisory_unlock_shared"
                if lock_mode == "shared"
                else "pg_advisory_unlock"
            )
            released = connection.scalar(
                text(f"SELECT {unlock_function}(:lock_key)"),
                {"lock_key": lock_key},
            )
            if released is not True:
                invalidate = True
        except Exception:
            invalidate = True
            logger.error(
                f"target advisory lockの解放に失敗しました: {task_uuid}",
                exc_info=True,
            )
    if invalidate:
        # poolへlock保持connectionを戻さず、DB切断で必ず解放する。
        connection.invalidate()


@contextmanager
def task_target_advisory_locks(
    db: Session,
    task: TaskModel,
) -> Iterator[tuple[tuple[int, str], ...]]:
    """Agent taskのresolved targetをhandler完了まで直列化する。"""

    lock_specs = _task_target_advisory_lock_specs(task)
    bind = db.get_bind()
    if not lock_specs or bind.dialect.name != "postgresql":
        yield lock_specs
        return

    engine = bind.engine if isinstance(bind, Connection) else bind
    connection: Connection | None = None
    acquired: list[tuple[int, str]] = []
    try:
        connection = engine.connect().execution_options(
            isolation_level="AUTOCOMMIT",
        )
        for lock_key, lock_mode in lock_specs:
            lock_function = (
                "pg_advisory_lock_shared"
                if lock_mode == "shared"
                else "pg_advisory_lock"
            )
            connection.execute(
                text(f"SELECT {lock_function}(:lock_key)"),
                {"lock_key": lock_key},
            )
            acquired.append((lock_key, lock_mode))
    except Exception as exc:
        if connection is not None:
            _release_postgresql_target_locks(
                connection,
                acquired,
                task_uuid=task.uuid,
            )
            connection.close()
        raise TaskPolicyUnavailable(
            "target advisory lockを取得できません",
        ) from exc

    try:
        yield lock_specs
    finally:
        _release_postgresql_target_locks(
            connection,
            acquired,
            task_uuid=task.uuid,
        )
        connection.close()


def evaluate_dispatch_policy(db: Session, task: TaskModel) -> None:
    """worker dispatch直前にAgent側の認可・lease・switchを検査する。"""

    if task.status == "cancel_requested":
        raise TaskCancellationRequested(
            "taskのキャンセルが要求されています",
        )

    if not is_agent_task(task):
        return
    if not task.lease_id:
        raise TaskDispatchRejected(
            "Agent taskに能力leaseがありません",
            error_code="TASK_LEASE_REQUIRED",
        )
    if (
        not task.principal_id
        or not task.correlation_id
        or not task.request_hash
        or not task.resolved_targets
    ):
        raise TaskDispatchRejected(
            "Agent taskの安全性metadataが不足しています",
            error_code="TASK_SAFETY_METADATA_MISSING",
        )
    validate_target_reservations(db, task)

    validator = _load_agent_policy_function("validate_worker_dispatch")
    if validator is None:
        # Agent経路はleaseやglobal switchを検証できない状態で実行しない。
        raise TaskPolicyUnavailable("Agent policy validatorを利用できません")

    decision = validator(db, task)
    if decision is False:
        raise TaskDispatchRejected("Agent policyによりtaskが拒否されました")


def record_worker_outcome(
    db: Session,
    task: TaskModel,
    *,
    release_reservations: bool = True,
) -> None:
    """Agent側の監査と端末別circuit breakerへ結果を通知する。"""

    if not is_agent_task(task):
        return
    recorder = _load_agent_policy_function("record_worker_outcome")
    if recorder is None:
        raise TaskPolicyUnavailable("Agent outcome recorderを利用できません")
    recorder(db, task)
    if release_reservations:
        release_target_reservations_if_terminal(
            db,
            task.correlation_id or task.uuid,
        )


class TaskBase:
    def __init__(self) -> None:
        self.task_func: dict[str, Callable[..., Any]] = {}

    def __call__(self, key: str) -> Callable[..., Any]:
        def receive_func(function: Callable[..., Any]) -> Callable[..., Any]:
            logger.info(f"taskを登録します: {key}")
            self.task_func[key] = function

            def wrapper(*args: Any, **kwargs: Any) -> Any:
                return function(*args, **kwargs)

            return wrapper

        return receive_func

    def include_task(self, task_base: "TaskBase") -> None:
        self.task_func.update(task_base.task_func)

    def run(self, key: str, task_uuid: str) -> Any:
        if key not in self.task_func:
            raise TaskError(
                "task handlerが登録されていません",
                error_code="TASK_HANDLER_NOT_FOUND",
            )

        with SessionLocal() as db:
            task_model = (
                db.query(TaskModel).filter(TaskModel.uuid == task_uuid).one()
            )
            db.commit()
            with task_target_advisory_locks(db, task_model) as lock_specs:
                db.refresh(task_model)
                if is_agent_task(task_model):
                    if _task_target_advisory_lock_specs(task_model) != lock_specs:
                        raise TaskDispatchRejected(
                            "lock待機中にresolved targetが変更されました",
                            error_code="TASK_RESOLVED_TARGET_CHANGED",
                        )
                    try:
                        # lock待機中のlease失効やgeneration変更を再検査する。
                        evaluate_dispatch_policy(db, task_model)
                        db.commit()
                    except TaskError:
                        db.rollback()
                        raise
                    except Exception as exc:
                        db.rollback()
                        error_code = getattr(exc, "error_code", None) or getattr(
                            exc,
                            "code",
                            None,
                        )
                        if error_code:
                            raise TaskDispatchRejected(
                                str(exc),
                                error_code=str(error_code),
                                retryable=bool(getattr(exc, "retryable", False)),
                            ) from exc
                        raise TaskPolicyUnavailable(
                            "target lock取得後のpolicy再検査に失敗しました",
                        ) from exc

                stored_request = task_model.request
                if task_model.lease_id or is_encrypted_task_request(stored_request):
                    serialized_request = decrypt_task_request(
                        stored_request,
                        task_uuid=task_model.uuid,
                    )
                else:
                    serialized_request = stored_request
                result = self.task_func[key](
                    db=db,
                    model=task_model,
                    req=TaskRequest(**json.loads(serialized_request)),
                )
                # handlerのDB更新も外部副作用の結果として確定する。
                # ここで失敗した場合はworkerがunknownへ遷移させる。
                db.commit()
                return result


class TaskManager:
    def __init__(self, db: Session) -> None:
        self.db = db
        self._model: TaskModel | None = None
        self.created = False
        self.idempotency_replayed = False
        self.method: str | None = None
        self.resource: str | None = None
        self.object: str | None = None

    @property
    def model(self) -> TaskModel:
        if self._model is None:
            raise TaskError(
                "taskはまだcommitされていません",
                error_code="TASK_NOT_COMMITTED",
            )
        return self._model

    def select(self, method: str, resource: str, object: str) -> None:
        self.method = method
        self.resource = resource
        self.object = object

    def _set_result(self, model: TaskModel, *, created: bool) -> TaskModel:
        self._model = model
        self.created = created
        self.idempotency_replayed = not created
        # response schemaには露出させず、呼出し側が判定できる一時属性とする。
        model.idempotency_replayed = not created
        return model

    def _find_idempotent_task(
        self,
        *,
        principal_id: str,
        idempotency_key: str,
    ) -> TaskModel | None:
        return (
            self.db.query(TaskModel)
            .filter(
                TaskModel.principal_id == principal_id,
                TaskModel.idempotency_key == idempotency_key,
            )
            .one_or_none()
        )

    def _return_replayed_task(
        self,
        existing: TaskModel,
        *,
        request_hash: str,
        agent_request_hash: str | None,
        commit_transaction: bool,
    ) -> TaskModel:
        if agent_request_hash is not None:
            hashes_match = existing.agent_request_hash == agent_request_hash
        else:
            hashes_match = existing.request_hash == request_hash
        if not hashes_match:
            raise TaskIdempotencyConflict(
                "同じidempotency keyが異なるrequestに使用されています",
            )
        if commit_transaction:
            # commitの従来契約を保ち、同一transactionのDPoP・監査も確定する。
            self.db.commit()
        return self._set_result(existing, created=False)

    def commit(
        self,
        user: Any,
        req: Any = None,
        body: BaseSchema | dict[str, Any] | None = None,
        param: dict[str, Any] | None = None,
        dep_uuid: str | None = None,
        *,
        idempotency_key: str | None = None,
        request_hash: str | None = None,
        agent_request_hash: str | None = None,
        principal_id: str | None = None,
        correlation_id: str | None = None,
        lease_id: str | None = None,
        risk: str | None = None,
        resolved_targets: list[Any] | None = None,
        expected_generation: Any = None,
        commit_transaction: bool = True,
    ) -> TaskModel:
        if self.method is None or self.resource is None or self.object is None:
            raise TaskError(
                "selectを呼び出してからtaskをcommitしてください",
                error_code="TASK_NOT_SELECTED",
            )

        task_uuid = str(uuid.uuid4())
        path_param = param if param is not None else {}
        task_body = body if body is not None else BaseSchema()
        raw_user_id = getattr(user, "id", None) or getattr(user, "username", None)
        user_id = raw_user_id if isinstance(raw_user_id, str) else None
        effective_principal = principal_id or user_id

        if idempotency_key is not None:
            idempotency_key = idempotency_key.strip()
            if not idempotency_key:
                raise TaskIdempotencyConflict("idempotency keyは空にできません")
            if effective_principal is None:
                raise TaskIdempotencyConflict(
                    "idempotency keyにはprincipalが必要です",
                )
        if agent_request_hash is not None:
            agent_request_hash = agent_request_hash.strip().lower()
            if (
                len(agent_request_hash) != 64
                or any(character not in "0123456789abcdef" for character in agent_request_hash)
            ):
                raise TaskIdempotencyConflict(
                    "Agent request hashはSHA-256形式で指定してください",
                    error_code="AGENT_REQUEST_HASH_INVALID",
                )

        parent: TaskModel | None = None
        if dep_uuid is not None:
            parent = (
                self.db.query(TaskModel)
                .filter(TaskModel.uuid == dep_uuid)
                .one_or_none()
            )
            if parent is None:
                raise TaskNotFoundError("依存先taskが見つかりません")

        parent_principal = None
        if parent is not None:
            parent_principal = parent.principal_id or parent.user_id
            if (
                effective_principal is not None
                and parent_principal is not None
                and effective_principal != parent_principal
            ):
                raise TaskOwnershipError(
                    "依存taskのprincipalが親taskと一致しません",
                )
            if (
                correlation_id is not None
                and parent.correlation_id is not None
                and correlation_id != parent.correlation_id
            ):
                raise TaskIdempotencyConflict(
                    "依存taskのcorrelation IDが親taskと一致しません",
                    error_code="TASK_CORRELATION_MISMATCH",
                )
            if (
                lease_id is not None
                and parent.lease_id is not None
                and lease_id != parent.lease_id
            ):
                raise TaskOwnershipError(
                    "依存taskのleaseが親taskと一致しません",
                    error_code="TASK_LEASE_MISMATCH",
                )
            if (
                agent_request_hash is not None
                and parent.agent_request_hash is not None
                and agent_request_hash != parent.agent_request_hash
            ):
                raise TaskIdempotencyConflict(
                    "依存taskのAgent request hashが親taskと一致しません",
                    error_code="TASK_AGENT_REQUEST_HASH_MISMATCH",
                )

        status = "wait" if dep_uuid else "init"
        url = None
        if dep_uuid is None and req is not None:
            url = str(req.url)

        effective_correlation_id = (
            correlation_id
            or (parent.correlation_id if parent is not None else None)
            or (parent.uuid if parent is not None else task_uuid)
        )
        effective_lease_id = lease_id or (
            parent.lease_id if parent is not None else None
        )
        effective_risk = risk or (parent.risk if parent is not None else None)
        effective_targets = resolved_targets
        if effective_targets is None and parent is not None:
            effective_targets = parent.resolved_targets
        effective_agent_request_hash = agent_request_hash
        if effective_agent_request_hash is None and parent is not None:
            effective_agent_request_hash = parent.agent_request_hash
        if effective_principal is None and parent is not None:
            effective_principal = parent_principal

        canonical_request_hash = calculate_task_request_hash(
            method=self.method,
            resource=self.resource,
            object_name=self.object,
            path_param=path_param,
            body=task_body,
            dependence_uuid=dep_uuid,
            expected_generation=expected_generation,
            resolved_targets=effective_targets,
        )
        if request_hash is not None and request_hash != canonical_request_hash:
            raise TaskIdempotencyConflict(
                "request hashがcanonical requestと一致しません",
                error_code="REQUEST_HASH_MISMATCH",
            )

        if idempotency_key is not None:
            if effective_principal is None:
                raise TaskIdempotencyConflict(
                    "idempotency keyにはprincipalが必要です",
                )
            existing = self._find_idempotent_task(
                principal_id=effective_principal,
                idempotency_key=idempotency_key,
            )
            if existing is not None:
                return self._return_replayed_task(
                    existing,
                    request_hash=canonical_request_hash,
                    agent_request_hash=effective_agent_request_hash,
                    commit_transaction=commit_transaction,
                )

        task_request = TaskRequest(url=url, path_param=path_param, body=task_body)
        serialized_request = task_request.model_dump_json()
        if effective_lease_id is not None:
            serialized_request = encrypt_task_request(
                serialized_request,
                task_uuid=task_uuid,
            )

        model = TaskModel(
            uuid=task_uuid,
            post_time=datetime.now().astimezone(),
            run_time=None,
            user_id=user_id,
            principal_id=effective_principal,
            status=status,
            dependence_uuid=dep_uuid,
            resource=self.resource,
            object=self.object,
            method=self.method,
            request=serialized_request,
            message="Task has been queued",
            idempotency_key=idempotency_key,
            request_hash=canonical_request_hash,
            agent_request_hash=effective_agent_request_hash,
            correlation_id=effective_correlation_id,
            lease_id=effective_lease_id,
            risk=effective_risk,
            resolved_targets=effective_targets,
            expected_generation=expected_generation,
        )
        # task以外の監査等の不整合をidempotency raceと誤認しない。
        self.db.flush()
        try:
            # unique raceでもDPoP・監査の外側transactionは保持する。
            with self.db.begin_nested():
                self.db.add(model)
                self.db.flush()
        except IntegrityError:
            if idempotency_key is None or effective_principal is None:
                raise
            existing = self._find_idempotent_task(
                principal_id=effective_principal,
                idempotency_key=idempotency_key,
            )
            if existing is None:
                raise
            return self._return_replayed_task(
                existing,
                request_hash=canonical_request_hash,
                agent_request_hash=effective_agent_request_hash,
                commit_transaction=commit_transaction,
            )

        if commit_transaction:
            self.db.commit()
        persisted = (
            self.db.query(TaskModel).filter(TaskModel.uuid == task_uuid).one()
        )
        return self._set_result(persisted, created=True)


def _find_operation_tasks(db: Session, root_task_uuid: str) -> list[TaskModel]:
    requested = (
        db.query(TaskModel).filter(TaskModel.uuid == root_task_uuid).one_or_none()
    )
    if requested is None:
        raise TaskNotFoundError("operationのroot taskが見つかりません")
    operation_owner = requested.principal_id or requested.user_id

    correlated: list[TaskModel] = []
    if requested.correlation_id:
        correlated = (
            db.query(TaskModel)
            .filter(TaskModel.correlation_id == requested.correlation_id)
            .order_by(TaskModel.post_time, TaskModel.uuid)
            .all()
        )
        correlated = [
            task
            for task in correlated
            if (task.principal_id or task.user_id) == operation_owner
        ]

    # migration前のtaskもdependency chain単位で集約できるようにする。
    root = requested
    visited = {root.uuid}
    while root.dependence_uuid and root.dependence_uuid not in visited:
        parent = (
            db.query(TaskModel)
            .filter(TaskModel.uuid == root.dependence_uuid)
            .one_or_none()
        )
        if parent is None:
            break
        if (parent.principal_id or parent.user_id) != operation_owner:
            break
        root = parent
        visited.add(root.uuid)

    tasks_by_id = {task.uuid: task for task in correlated}
    tasks_by_id[root.uuid] = root
    frontier = list(tasks_by_id)
    while frontier:
        children = (
            db.query(TaskModel)
            .filter(TaskModel.dependence_uuid.in_(frontier))
            .order_by(TaskModel.post_time, TaskModel.uuid)
            .all()
        )
        frontier = []
        for child in children:
            if child.uuid in tasks_by_id:
                continue
            if (child.principal_id or child.user_id) != operation_owner:
                continue
            tasks_by_id[child.uuid] = child
            frontier.append(child.uuid)
    return sorted(
        tasks_by_id.values(),
        key=lambda task: (
            task.post_time.isoformat() if task.post_time is not None else "",
            task.uuid,
        ),
    )


def normalize_operation_status(tasks: list[TaskModel]) -> OperationStatus:
    statuses = {task.status for task in tasks}
    if "unknown" in statuses:
        return "unknown"
    if statuses.intersection({"error", "lost"}):
        return "failed"
    if "cancel_requested" in statuses:
        return "cancel_requested"
    if statuses.intersection(RUNNING_STATUSES):
        return "running"
    if statuses.intersection(QUEUED_STATUSES):
        return "queued"
    if "cancelled" in statuses:
        return "cancelled"
    if statuses == {"finish"}:
        return "succeeded"
    return "unknown"


def get_operation(db: Session, root_task_uuid: str) -> dict[str, Any]:
    tasks = _find_operation_tasks(db, root_task_uuid)
    normalized_status = normalize_operation_status(tasks)

    relevant = next(
        (
            task
            for task in reversed(tasks)
            if task.status
            in {"unknown", "error", "lost", "cancel_requested", "cancelled"}
        ),
        tasks[-1],
    )
    retryable = normalized_status == "failed" and any(
        task.retryable is True for task in tasks
    )
    operation = TaskOperation(
        operation_id=root_task_uuid,
        task_ids=[task.uuid for task in tasks],
        normalized_status=normalized_status,
        message=relevant.message,
        error_code=relevant.error_code,
        retryable=retryable,
    )
    return operation.model_dump()


def request_cancel_operation(
    db: Session,
    operation_id: str,
    principal_id: str,
    *,
    admin: bool = False,
    commit_transaction: bool = True,
) -> dict[str, Any]:
    tasks = _find_operation_tasks(db, operation_id)
    locked_tasks = (
        db.query(TaskModel)
        .filter(TaskModel.uuid.in_([task.uuid for task in tasks]))
        .order_by(TaskModel.uuid)
        .with_for_update()
        .all()
    )

    if not admin:
        for task in locked_tasks:
            owner = task.principal_id or task.user_id
            if owner != principal_id:
                raise TaskOwnershipError(
                    "operationを作成したprincipalだけがキャンセルできます",
                )

    now = datetime.now().astimezone()
    for task in locked_tasks:
        if task.status in QUEUED_STATUSES:
            task.status = "cancelled"
            task.message = "dispatch前にキャンセルされました"
            task.error_code = "TASK_CANCELLED"
            task.retryable = False
            task.update_time = now
        elif task.status in RUNNING_STATUSES:
            task.status = "cancel_requested"
            task.message = "taskのキャンセルを要求しました"
            task.error_code = "TASK_CANCEL_REQUESTED"
            task.retryable = False
            task.update_time = now
    release_target_reservations_if_terminal(db, tasks[0].correlation_id or operation_id)
    if commit_transaction:
        db.commit()
    else:
        db.flush()
    return get_operation(db, operation_id)


def request_operation_cancellation(
    db: Session,
    root_task_uuid: str,
    principal_id: str,
    *,
    admin: bool = False,
    commit_transaction: bool = True,
) -> dict[str, Any]:
    """Agent API用の読みやすいalias。"""

    return request_cancel_operation(
        db,
        root_task_uuid,
        principal_id,
        admin=admin,
        commit_transaction=commit_transaction,
    )


def task_scheduler(db: Session, bg: BackgroundTasks, mode: str = "init") -> None:
    """旧BackgroundTasks scheduler。worker.pyと同じpolicy hookを適用する。"""

    tasks = (
        db.query(TaskModel)
        .filter(TaskModel.status == mode)
        .order_by(TaskModel.post_time)
        .with_for_update()
        .all()
    )

    if not tasks and mode == "init":
        task_scheduler(db=db, bg=bg, mode="wait")
        return
    if not tasks:
        return

    if mode == "init":
        task = tasks[0]
        try:
            evaluate_dispatch_policy(db, task)
        except TaskError as exc:
            cancelled = bool(getattr(exc, "cancelled", False))
            task.status = "cancelled" if cancelled else "error"
            task.message = (
                "dispatch前にtaskがキャンセルされました"
                if cancelled
                else str(exc)
            )
            task.error_code = "TASK_CANCELLED" if cancelled else exc.error_code
            task.retryable = False if cancelled else exc.retryable
            task.update_time = datetime.now().astimezone()
            record_worker_outcome(db, task)
            db.commit()
            return
        task.status = "start"
        db.commit()
        task_runner(db=db, bg=bg, task=task)
        task_scheduler(db=db, bg=bg)
        return

    for task in tasks:
        depends_task = (
            db.query(TaskModel)
            .filter(TaskModel.uuid == task.dependence_uuid)
            .with_for_update()
            .one_or_none()
        )
        if depends_task is None:
            task.status = "error"
            task.message = "依存先taskが見つかりません"
            task.error_code = "DEPENDENCY_NOT_FOUND"
            task.retryable = False
        elif depends_task.status in {"error", "lost"}:
            task.status = "error"
            task.message = "依存先taskが失敗しました"
            task.error_code = "DEPENDENCY_FAILED"
            task.retryable = False
        elif depends_task.status in {"unknown", "cancelled"}:
            task.status = "cancelled"
            task.message = "依存先taskが完了していません"
            task.error_code = "DEPENDENCY_NOT_COMPLETED"
            task.retryable = False
        elif depends_task.status == "finish" and task.status == "wait":
            task.status = "init"
        db.commit()
    task_scheduler(db=db, bg=bg)


def task_runner(db: Session, bg: BackgroundTasks, task: TaskModel) -> None:
    logger.info(
        f"taskを実行します: {task.resource}.{task.object}.{task.method} {task.uuid}"
    )
    start_time = time()
    task_uuid = task.uuid

    try:
        exec(f"{task.method}_{task.resource}_{task.object}(db=db, bg=bg, task=task)")
        task.status = "finish"
        task.error_code = None
        task.retryable = None
    except Exception as exc:
        db.rollback()
        task = db.query(TaskModel).filter(TaskModel.uuid == task_uuid).one()
        agent_task = is_agent_task(task)
        cancelled = bool(getattr(exc, "cancelled", False))
        outcome_unknown = bool(getattr(exc, "outcome_unknown", agent_task))
        if agent_task:
            logger.error(
                "旧schedulerのAgent task handlerが失敗しました: "
                f"{task_uuid}: "
                f"{getattr(exc, 'error_code', None) or getattr(exc, 'code', None) or 'TASK_EXECUTION_FAILED'}"
            )
        else:
            logger.error(exc, exc_info=True)
        if cancelled:
            task.status = "cancelled"
        elif agent_task and outcome_unknown:
            task.status = "unknown"
        else:
            task.status = "error"
        task.message = (
            "外部処理開始前にtaskがキャンセルされました"
            if cancelled
            else str(exc)
            if not agent_task or bool(getattr(exc, "safe_message", False))
            else "Agent taskの実行結果を安全に確認できませんでした"
        )
        task.error_code = "TASK_CANCELLED" if cancelled else (
            getattr(exc, "error_code", None)
            or getattr(exc, "code", None)
            or "TASK_EXECUTION_FAILED"
        )
        task.retryable = (
            False if cancelled else bool(getattr(exc, "retryable", False))
        )

    task.run_time = time() - start_time
    task.update_time = datetime.now().astimezone()
    record_worker_outcome(db, task)
    db.commit()
