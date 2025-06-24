from datetime import datetime
from typing import Any, List

from pydantic import Json

from mixin.schemas import BaseSchema, GetPagination


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
    

class TaskForCreate(TaskBase):
    pass


class TaskForQuery(GetPagination):
    resource: str | None = None
    object: str | None = None
    method: str | None = None
    status: str | None = None


class Task(TaskBase):
    uuid: str | None = None


class TaskPage(BaseSchema):
    count: int
    data: List[Task]


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