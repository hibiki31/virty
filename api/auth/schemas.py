from typing import List, Optional
from pydantic import BaseModel
from mixin.schemas import BaseSchema

# RFCでスネークケース指定あるやんけ
class TokenRFC6749Response(BaseModel):
    access_token: str
    token_type: str


class AuthValidateResponse(TokenRFC6749Response):
    username: str


class TokenData(BaseSchema):
    user_id: Optional[str] | None = None
    scopes: List[str] = []
    role: List[str] = []
    projects: List[str] = []

class SetupRequest(BaseSchema):
    username: str
    password: str

