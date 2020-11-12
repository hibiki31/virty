from fastapi_camelcase import CamelModel
from pydantic import BaseModel
from typing import List, Optional


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