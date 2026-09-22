from typing import Annotated, List, Optional

from cryptography.exceptions import UnsupportedAlgorithm
from cryptography.hazmat.primitives.serialization import load_ssh_public_key
from pydantic import AfterValidator, BaseModel, ConfigDict, Field, field_validator
from pydantic_core import PydanticCustomError

from auth.password import NewPassword
from mixin.schemas import BaseSchema, GetPagination


class TokenRFC6749Response(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseSchema):
    id: Optional[str] | None = None
    scopes: List[str] = Field(default_factory=list)
    role: List[str] = Field(default_factory=list)


class UserBase(BaseSchema):
    id: str | None = None


class UserScope(BaseSchema):
    name: str


class UserProject(BaseSchema):
    id: str
    name: str

class UserPublickey(BaseSchema):
    name: str
    publickey: str


class UserPublickeyInput(UserPublickey):
    name: str = Field(min_length=1, max_length=255)
    publickey: str = Field(min_length=1, max_length=16384)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not value.strip():
            raise PydanticCustomError("key_name_required", "A key name is required.")
        return value

    @field_validator("publickey")
    @classmethod
    def validate_key(cls, value: str) -> str:
        try:
            if "PRIVATE KEY" in value or "\n" in value.strip() or "\r" in value.strip():
                raise ValueError("invalid key")
            load_ssh_public_key(value.strip().encode("utf-8"))
        except (ValueError, TypeError, UnsupportedAlgorithm) as exc:
            raise PydanticCustomError("invalid_public_key", "A valid SSH public key is required.") from exc
        return value.strip()


def unique_publickeys(value: list[UserPublickeyInput]) -> list[UserPublickeyInput]:
    if len({key.name for key in value}) != len(value):
        raise PydanticCustomError("duplicate_key_name", "Public key names must be unique.")
    return value


PublickeyInputList = Annotated[
    list[UserPublickeyInput], Field(max_length=64), AfterValidator(unique_publickeys),
]

class UserForQuery(GetPagination):
    name_like: str | None = None


class User(BaseSchema):
    username: str
    scopes: List[UserScope] = Field(default_factory=list)
    projects: List[UserProject] = Field(default_factory=list)
    publickeys: List[UserPublickey] = Field(default_factory=list)


class UserPage(BaseSchema):
    count: int
    data:List[User]

class UserForCreate(BaseSchema):
    username: str = Field(min_length=1, max_length=255)
    scopes: List[UserScope] = Field(default_factory=list, max_length=256)
    publickeys: PublickeyInputList = Field(default_factory=list)
    password: NewPassword

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        if not value.strip() or "/" in value or any(ord(char) < 32 for char in value):
            raise PydanticCustomError("invalid_username", "The user name is invalid.")
        return value

class UserForUpdate(BaseSchema):
    scopes: List[UserScope]
    publickeys: PublickeyInputList


class UserProfile(TokenData):
    username: str
    projects: list[UserProject] = Field(default_factory=list)
    publickeys: list[UserPublickey] = Field(default_factory=list)


class OwnPublickeysUpdate(BaseSchema):
    model_config = ConfigDict(extra="forbid")
    publickeys: PublickeyInputList


class PasswordReset(BaseSchema):
    model_config = ConfigDict(extra="forbid")
    new_password: NewPassword


class PasswordChange(PasswordReset):
    current_password: str = Field(min_length=1, json_schema_extra={"writeOnly": True})

class UserInDB(UserBase):
    hashed_password: str


class UserResponse(BaseSchema):
    username: str
