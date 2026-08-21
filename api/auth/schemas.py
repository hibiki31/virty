from typing import List, Optional

from pydantic import BaseModel, Field

from mixin.schemas import BaseSchema


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
    username: str
    password: str = Field(json_schema_extra={"writeOnly": True})
