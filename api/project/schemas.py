from typing import List

from anyio import Any
from fastapi_camelcase import CamelModel

from mixin.schemas import GetPagination


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


class ProjectForQuery(GetPagination):
    name_like: str = None


class Project(ProjectBase):
    memory_g: int
    core: int
    storage_capacity_g: int
    users: List[ProjectUser]
    used_memory_g: int
    used_core: int
    network_pools: Any
    storage_pools: Any
    class Config:
        orm_mode = True


class ProjectPage(CamelModel):
    count: int
    data: List[Project]