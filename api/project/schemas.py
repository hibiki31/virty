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
    users: List[UserBase]