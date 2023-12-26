from typing import List, Optional

from pydantic import BaseModel

from mixin.schemas import GetPagination, BaseSchema


# RFCでスネークケース指定あるやんけ
class TokenRFC6749Response(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseSchema):
    id: Optional[str] | None = None
    scopes: List[str] = []
    role: List[str] = []


class UserBase(BaseSchema):
    id: str | None = None


class UserScope(BaseSchema):
    name: str


class UserProject(BaseSchema):
    name: str


class UserForQuery(GetPagination):
    name_like: str | None = None


class User(BaseSchema):
    username: str
    scopes: List[UserScope]
    projects: List[UserProject]


class UserPage(BaseSchema):
    count: int
    data:List[User]


class UserForCreate(BaseSchema):
    user_id: str
    password: str


class UserInDB(UserBase):
    hashed_password: str


class UserResponse(BaseSchema):
    user_id: str
    hashed_password: str


class GroupForUpdate(BaseSchema):
    group_id: str
    user_id: str
