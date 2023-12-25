from typing import List, Optional

from fastapi_camelcase import CamelModel
from pydantic import BaseModel

from mixin.schemas import GetPagination


# RFCでスネークケース指定あるやんけ
class TokenRFC6749Response(BaseModel):
    access_token: str
    token_type: str


class TokenData(CamelModel):
    id: Optional[str] = None
    scopes: List[str] = []
    role: List[str] = []


class UserBase(CamelModel):
    id: str = None
    class Config:
        orm_mode = True


class UserScope(CamelModel):
    name: str
    class Config:
        orm_mode = True


class UserProject(CamelModel):
    name: str
    class Config:
        orm_mode = True


class UserForQuery(GetPagination):
    name_like: str = None


class User(CamelModel):
    username: str
    scopes: List[UserScope]
    projects: List[UserProject]
    class Config:
        orm_mode = True


class UserPage(CamelModel):
    count: int
    data:List[User]
    class Config:
        orm_mode = True 


class UserForCreate(CamelModel):
    user_id: str
    password: str


class UserInDB(UserBase):
    hashed_password: str


class UserResponse(CamelModel):
    user_id: str
    hashed_password: str


class GroupForUpdate(CamelModel):
    group_id: str
    user_id: str
