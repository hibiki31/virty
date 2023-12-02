from fastapi_camelcase import CamelModel
from typing import List, Optional
from pydantic import BaseModel

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


class UserPage(CamelModel):
    username: str
    scopes: List[UserScope]
    projects: List[UserProject]
    class Config:
        orm_mode = True


class User(CamelModel):
    count: int
    data:List[UserPage]
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

class GroupBase(CamelModel):
    group_id: str
    class Config:
        orm_mode = True

class GroupForCreate(GroupBase):
    pass

class GroupForUpdate(CamelModel):
    group_id: str
    user_id: str

class UserWithGroup(UserBase):
    groups: List[GroupBase]

class Group(GroupBase):
    users: List[UserBase]