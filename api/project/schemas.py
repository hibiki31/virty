from anyio import Any
from fastapi_camelcase import CamelModel
from typing import List, Optional
from pydantic import BaseModel

from user.schemas import UserBase


class ProjectBase(CamelModel):
    id: str
    name: str
    class Config:
        orm_mode = True

class PostProject(CamelModel):
    project_name: str
    user_ids: List[str]


class DeleteProject(CamelModel):
    id: str


class ProjectPatch(CamelModel):
    project_id: str
    user_id: str

class ProjectSelect(ProjectBase):
    core: int
    memory_g: int
    storage_capacity_g: int
    users: List[UserBase]
    used_memory_g: int
    used_core: int
    network_pools: Any
    storage_pools: Any