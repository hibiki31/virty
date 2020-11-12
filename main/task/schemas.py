from fastapi_camelcase import CamelModel
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TaskBase(CamelModel):
    post_time: datetime = None
    run_time: int = None
    user_id: str = None
    status: str = None
    resource: str = None
    object: str = None
    method: str = None
    json_str: str = None
    message: str = None

class TaskInsert(TaskBase):
    pass

class TaskSelect(TaskBase):
    uuid: str = None
    class Config:
        orm_mode  =  True
