from fastapi_camelcase import CamelModel
from typing import List, Optional
from pydantic import BaseModel

from user.schemas import UserBase


class GroupBase(CamelModel):
    id: str
    class Config:
        orm_mode = True

class GroupPost(CamelModel):
    group_id: str

class GroupPatch(CamelModel):
    group_id: str
    user_id: str

class GroupSelect(GroupBase):
    users: List[UserBase]