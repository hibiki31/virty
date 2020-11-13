from fastapi_camelcase import CamelModel
from pydantic import BaseModel, ValidationError, validator
from typing import List, Optional
from datetime import datetime


import json


class TaskBase(CamelModel):
    post_time: datetime = None
    run_time: int = None
    user_id: str = None
    status: str = None
    resource: str = None
    object: str = None
    method: str = None
    request: dict = None
    message: str = None

    class Config:
        orm_mode  =  True

    @validator('request', pre=True)
    def json_to_dic(cls, v, values, **kwargs):
        if type(v) == str:
            return dict(json.loads(v))
        else:
            return {}
    

class TaskInsert(TaskBase):
    pass

class TaskSelect(TaskBase):
    uuid: str = None
