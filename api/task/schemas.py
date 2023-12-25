from datetime import datetime
from typing import Any, List

from fastapi_camelcase import CamelModel

from mixin.schemas import GetPagination


class TaskBase(CamelModel):
    post_time: datetime = None
    run_time: float = None
    start_time: datetime = None
    update_time: datetime = None
    user_id: str = None
    status: str = None
    resource: str = None
    object: str = None
    method: str = None
    dependence_uuid: str = None
    request: Any = None
    result: dict = None
    message: str = None
    log: str = None

    class Config:
        orm_mode  =  True
    

class TaskForCreate(TaskBase):
    pass


class TaskForQuery(GetPagination):
    resource: str = None
    object: str = None
    method: str = None
    status: str = None


class Task(TaskBase):
    uuid: str = None


class TaskPage(CamelModel):
    count: int
    data: List[Task]


class TaskRequest(CamelModel):
    url: str = None
    path_param: Any
    body: Any


class TaskIncomplete(CamelModel):
    hash: str
    count: int
    uuids: List[str]