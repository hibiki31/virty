import re
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from mixin.schemas import BaseSchema, GetPagination


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
    username: str = Field(
        min_length=3,
        max_length=30,
        pattern=r"^[A-Za-z][A-Za-z0-9_-]*$"
    )
    password: str = Field(
        min_length=8,
        max_length=128,
        pattern=r'^[^\s]+$'
    )
    
    @field_validator('password')
    def strong_password(cls, v: str) -> str:
        categories = sum(
            bool(re.search(p, v)) for p in (r'[a-z]', r'[A-Z]', r'\d', r'[^A-Za-z0-9]')
        )
        if categories < 4:
            raise ValueError('Password must contain lower-case, upper-case, digit and symbol')
        return v


class UserInDB(UserBase):
    hashed_password: str


class UserResponse(BaseSchema):
    username: str


class GroupForUpdate(BaseSchema):
    group_id: str
    user_id: str
