from datetime import datetime
from typing import Any, List, Literal

from pydantic import Json, field_validator

from mixin.schemas import BaseSchema, GetPagination
from task.crypto import redact_encrypted_task_request


class TaskBase(BaseSchema):
    post_time: datetime | None = None
    run_time: float | None = None
    start_time: datetime | None = None
    update_time: datetime | None = None
    user_id: str | None = None
    status: str | None = None
    resource: str
    object: str
    method: str
    dependence_uuid: str | None = None
    request: Json | None = None
    result: dict | None = None
    message: str | None = None
    log: str | None = None
    principal_id: str | None = None
    idempotency_key: str | None = None
    request_hash: str | None = None
    agent_request_hash: str | None = None
    correlation_id: str | None = None
    lease_id: str | None = None
    risk: str | None = None
    resolved_targets: list[Any] | None = None
    expected_generation: Any | None = None
    error_code: str | None = None
    retryable: bool | None = None
    archived_at: datetime | None = None

    @field_validator("request", mode="before")
    @classmethod
    def redact_agent_request(cls, value: Any) -> Any:
        return redact_encrypted_task_request(value)


class TaskForCreate(TaskBase):
    pass


class Task(TaskBase):
    uuid: str


class TaskPage(BaseSchema):
    count: int
    data: List[Task]


class TaskForQuery(GetPagination):
    resource: str | None = None
    object: str | None = None
    method: str | None = None
    status: str | None = None


class TaskRequest(BaseSchema):
    url: str | None = None
    path_param: Any
    body: Any


class TaskIncompleteForQuery(BaseSchema):
    reference_hash: str | None = None
    admin: bool | None = None


class TaskIncomplete(BaseSchema):
    hash: str
    count: int
    uuids: List[str]


OperationStatus = Literal[
    "queued",
    "running",
    "succeeded",
    "failed",
    "cancel_requested",
    "cancelled",
    "unknown",
]


class TaskOperation(BaseSchema):
    operation_id: str
    task_ids: List[str]
    normalized_status: OperationStatus
    message: str | None = None
    error_code: str | None = None
    retryable: bool = False
