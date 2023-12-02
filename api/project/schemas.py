from anyio import Any
from fastapi_camelcase import CamelModel
from typing import List, Optional
from pydantic import BaseModel


class ProjectBase(CamelModel):
    id: str
    name: str
    class Config:
        orm_mode = True

class ProjectForCreate(CamelModel):
    project_name: str
    user_ids: List[str]


class ProjectForDelete(CamelModel):
    id: str


class ProjectForUpdate(CamelModel):
    project_id: str
    user_id: str


class ProjectUser(CamelModel):
    username: str
    class Config:
        orm_mode = True

class Project(ProjectBase):
    core: int
    memory_g: int
    storage_capacity_g: int
    users: List[ProjectUser]
    used_memory_g: int
    used_core: int
    network_pools: Any
    storage_pools: Any
    class Config:
        orm_mode = True