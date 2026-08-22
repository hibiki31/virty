"""worker taskの応答契約と有限待機。"""

from __future__ import annotations

import hashlib
import time
from collections.abc import Callable
from typing import Any, Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, ValidationError


TERMINAL_SUCCESS = "finish"
TERMINAL_FAILURES = {"error", "lost"}
KNOWN_STATUSES = {"wait", "init", "start", TERMINAL_SUCCESS, *TERMINAL_FAILURES}


class HttpResponse(Protocol):
    def raise_for_status(self) -> None: ...

    def json(self) -> Any: ...


class TaskClient(Protocol):
    def get(self, path: str) -> HttpResponse: ...


class QueuedTask(BaseModel):
    model_config = ConfigDict(extra="ignore", strict=True)

    uuid: str


class TaskSnapshot(BaseModel):
    model_config = ConfigDict(extra="ignore", strict=True)

    uuid: str
    status: str
    message: str | None = None
    log: str | None = None


def _safe_task_id(task_uuid: str) -> str:
    return hashlib.sha256(task_uuid.encode("utf-8")).hexdigest()[:12]


class TaskPollingError(RuntimeError):
    """task本文を表示せず、詳細を属性として保持するpolling error。"""

    def __init__(self, reason: str, snapshots: dict[str, TaskSnapshot] | None = None):
        self.reason = reason
        self.snapshots = snapshots or {}
        safe_states = ", ".join(
            f"id={_safe_task_id(task_uuid)} status={snapshot.status}"
            for task_uuid, snapshot in sorted(self.snapshots.items())
        )
        suffix = f": {safe_states}" if safe_states else ""
        super().__init__(f"task polling {reason}{suffix}")


def _parse_queued_tasks(response: HttpResponse) -> list[str]:
    try:
        response.raise_for_status()
        payload = response.json()
    except Exception:
        raise TaskPollingError("enqueue HTTP response is invalid") from None
    if not isinstance(payload, list) or not payload:
        raise TaskPollingError("enqueue response is not a non-empty list")
    try:
        tasks = [QueuedTask.model_validate(item) for item in payload]
    except ValidationError:
        raise TaskPollingError("enqueue response schema is invalid") from None
    uuids = [task.uuid for task in tasks]
    try:
        normalized_uuids = [str(UUID(task_uuid)) for task_uuid in uuids]
    except (ValueError, AttributeError, TypeError):
        raise TaskPollingError("enqueue response UUID format is invalid") from None
    if len(normalized_uuids) != len(set(normalized_uuids)):
        raise TaskPollingError("enqueue response UUIDs are empty or duplicated")
    return normalized_uuids


def _read_snapshot(client: TaskClient, task_uuid: str) -> TaskSnapshot:
    try:
        response = client.get(f"/api/tasks/{task_uuid}")
        response.raise_for_status()
        snapshot = TaskSnapshot.model_validate(response.json())
    except Exception:
        raise TaskPollingError("task HTTP response or schema is invalid") from None
    try:
        snapshot_uuid = str(UUID(snapshot.uuid))
    except (ValueError, AttributeError, TypeError):
        raise TaskPollingError("task response identity or status is invalid") from None
    if snapshot_uuid != task_uuid or snapshot.status not in KNOWN_STATUSES:
        raise TaskPollingError("task response identity or status is invalid")
    snapshot.uuid = snapshot_uuid
    return snapshot


def wait_for_tasks(
    enqueue_response: HttpResponse,
    client: TaskClient,
    *,
    timeout_seconds: float = 900,
    poll_interval: float = 0.5,
    clock: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
) -> list[TaskSnapshot]:
    """全taskを同じdeadlineで監視し、全件finishしたsnapshotを返す。"""

    if timeout_seconds <= 0 or poll_interval <= 0:
        raise ValueError("timeoutとpoll intervalは正数で指定してください")
    task_uuids = _parse_queued_tasks(enqueue_response)
    pending = set(task_uuids)
    last_snapshots: dict[str, TaskSnapshot] = {}
    deadline = clock() + timeout_seconds

    while pending:
        for task_uuid in task_uuids:
            if task_uuid not in pending:
                continue
            snapshot = _read_snapshot(client, task_uuid)
            last_snapshots[task_uuid] = snapshot
            if snapshot.status in TERMINAL_FAILURES:
                raise TaskPollingError("reached failure state", last_snapshots)
            if snapshot.status == TERMINAL_SUCCESS:
                pending.remove(task_uuid)

        if not pending:
            return [last_snapshots[task_uuid] for task_uuid in task_uuids]

        remaining = deadline - clock()
        if remaining <= 0:
            raise TaskPollingError("timed out", last_snapshots)
        sleep(min(poll_interval, remaining))

    raise AssertionError("unreachable")
