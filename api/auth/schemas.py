from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from mixin.schemas import BaseSchema
from auth.password import NewPassword
from user.schemas import UserForCreate


# RFCでスネークケース指定あるやんけ
class TokenRFC6749Response(BaseModel):
    access_token: str
    token_type: str


class AuthValidateResponse(TokenRFC6749Response):
    username: str


class TokenData(BaseSchema):
    user_id: Optional[str] | None = None
    scopes: List[str] = Field(default_factory=list)
    role: List[str] = Field(default_factory=list)
    projects: List[str] = Field(default_factory=list)

class SetupRequest(BaseSchema):
    username: str = Field(min_length=1, max_length=255)
    password: NewPassword

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        return UserForCreate.validate_username(value)
