import multiprocessing as mp
import os
import traceback
from datetime import datetime
from pathlib import Path
from time import sleep, time

from sqlalchemy import or_
from sqlalchemy.orm import Session

from agent.tasks import worker_task as agent_tasks
from domain.tasks import worker_task as domain_tasks
from images.tasks import worker_task as image_tasks
from mixin.database import SessionLocal
from mixin.log import setup_logger
from models import TaskModel
from network.tasks import worker_task as network_tasks
from node.tasks import worker_task as node_tasks
from project.tasks import worker_task as project_tasks
from settings import DATA_ROOT
from storage.tasks import worker_task as storage_tasks
from task.functions import (
    QUEUED_STATUSES,
    TaskBase,
    evaluate_dispatch_policy,
    is_agent_task,
    record_worker_outcome,
    release_target_reservations_if_terminal,
)

logger = setup_logger(__name__)


def main() -> None:
    # Ansible runnerがforkしてSessionを破壊しないようにする。
    mp.set_start_method("spawn", force=True)

    ansible_private_path = os.path.join(DATA_ROOT, "ansible")
    os.makedirs(ansible_private_path, exist_ok=True)

    task_manager = TaskBase()
    task_manager.include_task(domain_tasks)
    task_manager.include_task(node_tasks)
    task_manager.include_task(storage_tasks)
    task_manager.include_task(network_tasks)
    task_manager.include_task(project_tasks)
    task_manager.include_task(image_tasks)
    task_manager.include_task(agent_tasks)

    init_scheduler()
    ready_file = os.getenv("VIRTY_WORKER_READY_FILE")
    if ready_file:
        Path(ready_file).touch()
        logger.info("Workerの起動準備が完了しました")

    while True:
        run_scheduler(task_manager)
        sleep(0.1)


def _record_outcome_safely(db: Session, task: TaskModel) -> None:
    try:
        # recorder障害でtask状態までrollbackしないようsavepointを分ける。
        with db.begin_nested():
            record_worker_outcome(db, task)
    except Exception as exc:
        logger.error(
            f"task結果の監査・breaker記録に失敗しました: {task.uuid}: {exc}",
            exc_info=True,
        )
        if is_agent_task(task) and task.status != "unknown":
            # 監査不能の結果を確定扱いにせず、reservationも解放しない。
            task.status = "unknown"
            task.message = "Agent task結果の監査を確定できませんでした"
            task.error_code = "TASK_OUTCOME_AUDIT_FAILED"
            task.retryable = False
            task.update_time = datetime.now().astimezone()


def init_scheduler() -> None:
    """worker停止中だったtaskを経路別の安全な状態へ回収する。"""

    with SessionLocal.begin() as db:
        interrupted_tasks = (
            db.query(TaskModel)
            .filter(
                or_(
                    TaskModel.status.in_(
                        ("start", "reconciling", "cancel_requested"),
                    ),
                    (
                        TaskModel.lease_id.is_(None)
                        & TaskModel.idempotency_key.is_(None)
                        & TaskModel.status.notin_(
                            ("finish", "lost", "error", "cancelled", "unknown"),
                        )
                    ),
                ),
            )
            .with_for_update()
            .all()
        )
        now = datetime.now().astimezone()
        for task in interrupted_tasks:
            if is_agent_task(task):
                task.status = "unknown"
                task.message = "結果確定前にworkerが再起動しました"
                task.error_code = "WORKER_RESTARTED_OUTCOME_UNKNOWN"
            else:
                # 既存REST taskは従来どおり、未完了状態をlostとして回収する。
                task.status = "lost"
                task.message = "worker再起動のためtaskを実行できませんでした"
                task.error_code = "WORKER_RESTARTED_TASK_LOST"
            task.retryable = False
            task.update_time = now
            _record_outcome_safely(db, task)

        if interrupted_tasks:
            logger.error(
                f"結果未確定のtaskを{len(interrupted_tasks)}件検出しました",
            )


def _mark_dependency_terminal(task: TaskModel, depends_task: TaskModel) -> None:
    if depends_task.status in {"error", "lost"}:
        task.status = "error"
        task.message = "依存先taskが失敗しました"
        task.error_code = "DEPENDENCY_FAILED"
    else:
        task.status = "cancelled"
        task.message = "依存先taskが完了していません"
        task.error_code = "DEPENDENCY_NOT_COMPLETED"
    task.retryable = False
    task.update_time = datetime.now().astimezone()


def run_scheduler(task_manager: TaskBase) -> None:
    init_tasks_uuid: list[str] = []

    with SessionLocal.begin() as db:
        tasks = (
            db.query(TaskModel)
            .filter(
                or_(
                    TaskModel.status == "init",
                    TaskModel.status == "wait",
                ),
            )
            .order_by(TaskModel.post_time)
            .with_for_update()
            .all()
        )

        for task in tasks:
            if task.status == "init":
                init_tasks_uuid.append(task.uuid)
                continue

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
                task.update_time = datetime.now().astimezone()
                _record_outcome_safely(db, task)
            elif depends_task.status in {
                "error",
                "lost",
                "unknown",
                "cancelled",
            }:
                _mark_dependency_terminal(task, depends_task)
                _record_outcome_safely(db, task)
            elif depends_task.status == "finish":
                task.status = "init"

    for task_uuid in init_tasks_uuid:
        exec_task(task_manager=task_manager, task_uuid=task_uuid)


def _exception_metadata(
    exc: Exception,
    *,
    default_code: str,
) -> tuple[str, bool]:
    error_code = str(
        getattr(exc, "error_code", None)
        or getattr(exc, "code", None)
        or default_code
    )
    retryable = bool(getattr(exc, "retryable", False))
    return error_code, retryable


def _safe_agent_failure_message(exc: Exception, *, outcome_unknown: bool) -> str:
    if bool(getattr(exc, "safe_message", False)) or getattr(exc, "code", None):
        return str(exc)
    if outcome_unknown:
        return "Agent taskの実行結果を安全に確認できませんでした"
    return "Agent taskを外部処理前に拒否しました"


def _reject_before_dispatch(task_uuid: str, exc: Exception) -> None:
    error_code, retryable = _exception_metadata(
        exc,
        default_code="TASK_POLICY_REJECTED",
    )
    with SessionLocal.begin() as db:
        task = (
            db.query(TaskModel)
            .filter(TaskModel.uuid == task_uuid)
            .with_for_update()
            .one_or_none()
        )
        if task is None:
            logger.warning(f"dispatch拒否対象のtaskが削除されています: {task_uuid}")
            return
        agent_task = is_agent_task(task)
        cancelled = bool(getattr(exc, "cancelled", False))
        task.status = "cancelled" if cancelled else "error"
        task.message = (
            "dispatch前にtaskがキャンセルされました"
            if cancelled
            else _safe_agent_failure_message(exc, outcome_unknown=False)
            if agent_task
            else str(exc)
        )
        task.error_code = "TASK_CANCELLED" if cancelled else error_code
        task.retryable = False if cancelled else retryable
        task.update_time = datetime.now().astimezone()
        _record_outcome_safely(db, task)


def _persist_execution_failure(
    task_uuid: str,
    exc: Exception,
    *,
    run_time: float,
) -> None:
    with SessionLocal.begin() as db:
        task = (
            db.query(TaskModel)
            .filter(TaskModel.uuid == task_uuid)
            .with_for_update()
            .one()
        )
        agent_task = is_agent_task(task)
        cancelled = bool(getattr(exc, "cancelled", False))
        outcome_unknown = bool(getattr(exc, "outcome_unknown", agent_task))
        default_code = (
            "TASK_EXECUTION_OUTCOME_UNKNOWN"
            if agent_task and outcome_unknown
            else "TASK_EXECUTION_FAILED"
        )
        error_code, retryable = _exception_metadata(exc, default_code=default_code)
        if cancelled:
            task.status = "cancelled"
        elif agent_task and outcome_unknown:
            task.status = "unknown"
        else:
            task.status = "error"
        task.message = (
            "外部処理開始前にtaskがキャンセルされました"
            if cancelled
            else _safe_agent_failure_message(exc, outcome_unknown=outcome_unknown)
            if agent_task
            else str(exc)
        )
        task.error_code = "TASK_CANCELLED" if cancelled else error_code
        # 結果不明のAgent taskは自動再試行させない。
        task.retryable = (
            retryable if task.status not in {"unknown", "cancelled"} else False
        )
        task.update_time = datetime.now().astimezone()
        task.run_time = run_time
        if not agent_task:
            task.write_log(traceback.format_exc())
        _record_outcome_safely(db, task)


def _persist_unknown_after_effect(
    task_uuid: str,
    exc: Exception,
    *,
    run_time: float,
) -> None:
    try:
        with SessionLocal.begin() as db:
            task = (
                db.query(TaskModel)
                .filter(TaskModel.uuid == task_uuid)
                .with_for_update()
                .one()
            )
            agent_task = is_agent_task(task)
            task.status = "unknown"
            task.message = (
                "外部処理完了後にAgent taskの結果を永続化できませんでした"
                if agent_task
                else f"外部処理完了後に結果を永続化できませんでした: {exc}"
            )
            task.error_code = "TASK_OUTCOME_PERSISTENCE_FAILED"
            task.retryable = False
            task.update_time = datetime.now().astimezone()
            task.run_time = run_time
            if not agent_task:
                task.write_log(traceback.format_exc())
            _record_outcome_safely(db, task)
    except Exception as persist_exc:
        logger.critical(
            f"結果不明taskの永続化にも失敗しました: {task_uuid}: {persist_exc}",
            exc_info=True,
        )
        raise


def _mark_reconciling(task_uuid: str, *, run_time: float) -> None:
    with SessionLocal.begin() as db:
        task = (
            db.query(TaskModel)
            .filter(TaskModel.uuid == task_uuid)
            .with_for_update()
            .one()
        )
        if task.status != "cancel_requested":
            task.status = "reconciling"
            task.message = "外部処理が完了し、結果を確認しています"
        task.error_code = None
        task.retryable = False
        task.update_time = datetime.now().astimezone()
        task.run_time = run_time


def _mark_finished(task_uuid: str, *, run_time: float) -> None:
    with SessionLocal.begin() as db:
        task = (
            db.query(TaskModel)
            .filter(TaskModel.uuid == task_uuid)
            .with_for_update()
            .one()
        )
        cancellation_was_requested = task.status == "cancel_requested"
        task.status = "finish"
        if cancellation_was_requested:
            task.message = "dispatch後にキャンセル要求を受けましたがtaskは完了しました"
        task.error_code = None
        task.retryable = None
        task.update_time = datetime.now().astimezone()
        task.run_time = run_time
        # 監査失敗時はcommitせず、呼出し側がunknownとして確定する。
        # reservationは成功commitのACK後に別transactionで解放する。
        record_worker_outcome(db, task, release_reservations=False)


def _release_finished_target_reservations(task_uuid: str) -> None:
    """成功結果の確定後にだけoperation reservationを解放する。"""

    with SessionLocal.begin() as db:
        task = (
            db.query(TaskModel)
            .filter(TaskModel.uuid == task_uuid)
            .with_for_update()
            .one_or_none()
        )
        if task is None or task.status != "finish" or not is_agent_task(task):
            return
        release_target_reservations_if_terminal(
            db,
            task.correlation_id or task.uuid,
        )


def exec_task(task_manager: TaskBase, task_uuid: str) -> None:
    agent_task = False
    try:
        with SessionLocal.begin() as db:
            task = (
                db.query(TaskModel)
                .filter(TaskModel.uuid == task_uuid)
                .with_for_update()
                .one_or_none()
            )
            if task is None:
                logger.warning(f"dispatch対象のtaskが削除されています: {task_uuid}")
                return
            if task.status not in QUEUED_STATUSES:
                return

            agent_task = is_agent_task(task)
            # policy側の途中更新も、拒否時にはsavepointごと破棄する。
            with db.begin_nested():
                evaluate_dispatch_policy(db, task)

            task.status = "start"
            task.start_time = datetime.now().astimezone()
            task_key = f"{task.method}.{task.resource}.{task.object}"
    except Exception as exc:
        if agent_task:
            error_code, _ = _exception_metadata(
                exc,
                default_code="TASK_POLICY_REJECTED",
            )
            logger.error(
                f"dispatch前のpolicy検査でAgent taskを拒否しました: "
                f"{task_uuid}: {error_code}",
            )
        else:
            logger.error(
                f"dispatch前のpolicy検査でtaskを拒否しました: {task_uuid}: {exc}",
                exc_info=True,
            )
        _reject_before_dispatch(task_uuid, exc)
        return

    start_time = time()
    try:
        logger.info(f"[Worker] task開始: {task_uuid} {task_key}")
        task_manager.run(key=task_key, task_uuid=task_uuid)
        logger.info(f"[Worker] 外部処理完了: {task_uuid} {task_key}")
    except Exception as exc:
        if agent_task:
            error_code, _ = _exception_metadata(
                exc,
                default_code="TASK_EXECUTION_OUTCOME_UNKNOWN",
            )
            logger.error(
                f"Agent task handlerが失敗しました: {task_uuid}: {error_code}",
            )
        else:
            logger.error(exc, exc_info=True)
        _persist_execution_failure(
            task_uuid,
            exc,
            run_time=time() - start_time,
        )
        return

    run_time = time() - start_time
    try:
        # Agent taskは外部処理と成功記録の間を明示し、再起動時にunknownへ回収する。
        with SessionLocal() as db:
            task = db.query(TaskModel).filter(TaskModel.uuid == task_uuid).one()
            agent_task = is_agent_task(task)
        if agent_task:
            _mark_reconciling(task_uuid, run_time=run_time)
        _mark_finished(task_uuid, run_time=run_time)
        logger.info(f"[Worker] task成功: {task_uuid} {task_key}")
    except Exception as exc:
        if agent_task:
            error_code, _ = _exception_metadata(
                exc,
                default_code="TASK_OUTCOME_PERSISTENCE_FAILED",
            )
            logger.error(
                f"Agent taskの外部処理後の結果確定に失敗しました: "
                f"{task_uuid}: {error_code}",
            )
        else:
            logger.error(
                f"外部処理後の結果確定に失敗しました: {task_uuid}: {exc}",
                exc_info=True,
            )
        _persist_unknown_after_effect(task_uuid, exc, run_time=run_time)
        return

    try:
        # finishと監査のcommitが成功したことを確認してから解放する。
        _release_finished_target_reservations(task_uuid)
    except Exception as exc:
        # 成功結果は確定済み。reservationは次回取得時にも安全に回収できる。
        logger.error(
            f"成功taskのtarget reservation解放に失敗しました: "
            f"{task_uuid}: {exc}",
            exc_info=True,
        )


if __name__ == "__main__":
    main()
