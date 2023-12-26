from typing import List

from anyio import Any

from mixin.schemas import GetPagination, BaseSchema


class ProjectBase(BaseSchema):
    id: str
    name: str
    

class ProjectForCreate(BaseSchema):
    project_name: str
    user_ids: List[str]


class ProjectForDelete(BaseSchema):
    id: str


class ProjectForUpdate(BaseSchema):
    project_id: str
    user_id: str


class ProjectUser(BaseSchema):
    username: str


class ProjectForQuery(GetPagination):
    name_like: str | None = None


class Project(ProjectBase):
    memory_g: int
    core: int
    storage_capacity_g: int
    users: List[ProjectUser]
    used_memory_g: int
    used_core: int
    network_pools: Any
    storage_pools: Any


class ProjectPage(BaseSchema):
    count: int
    data: List[Project]