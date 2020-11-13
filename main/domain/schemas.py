from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from fastapi_camelcase import CamelModel


class DomainBase(CamelModel):
    uuid: str


class DomainDelete(DomainBase):
    pass


class DomainInsert(DomainBase):
    description: str = None


class DomainSelect(DomainInsert):
    name: str
    core: int
    memory: int
    status: int
    user_id: str = None
    group_id: str = None
    class Config:
        orm_mode  =  True