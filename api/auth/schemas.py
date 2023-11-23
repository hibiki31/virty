from fastapi_camelcase import CamelModel
from typing import List, Optional
from pydantic import BaseModel

# RFCでスネークケース指定あるやんけ
class TokenRFC6749Response(BaseModel):
    access_token: str
    token_type: str


class AuthValidateResponse(TokenRFC6749Response):
    username: str


class TokenData(CamelModel):
    user_id: Optional[str] = None
    scopes: List[str] = []
    role: List[str] = []
    projects: List[str] = []

class SetupRequest(CamelModel):
    username: str
    password: str
    class Config:
        orm_mode = True
