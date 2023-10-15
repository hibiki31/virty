from fastapi_camelcase import CamelModel
from pydantic import BaseModel, ValidationError, validator
from typing import List, Optional, Any
from datetime import datetime

from task.models import TaskModel


import json


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
    request: dict = None
    result: dict = None
    message: str = None
    log: str = None

    class Config:
        orm_mode  =  True
    

class TaskForCreate(TaskBase):
    pass


class Task(TaskBase):
    uuid: str = None

    @validator('request', pre=True)
    def json_to_dic(cls, v, values, **kwargs):
        if type(v) == str:
            return dict(json.loads(v))
        return v

class TaskPagesnation(CamelModel):
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