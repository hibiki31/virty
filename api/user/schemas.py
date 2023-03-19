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

class UserInsert(CamelModel):
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

class GroupInsert(GroupBase):
    pass

class GroupPatch(CamelModel):
    group_id: str
    user_id: str

class UserSelect(UserBase):
    groups: List[GroupBase]

class GroupSelect(GroupBase):
    users: List[UserBase]