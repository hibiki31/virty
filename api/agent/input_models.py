"""既存APIに専用schemaがないAgent actionのstrict input。"""

import re

from pydantic import ConfigDict, Field, field_validator

from domain.schemas import DomainForCreate
from mixin.schemas import BaseSchema
from user.schemas import UserPublickey, UserScope


class StrictInput(BaseSchema):
    model_config = ConfigDict(
        alias_generator=BaseSchema.model_config["alias_generator"],
        from_attributes=True,
        populate_by_name=True,
        extra="forbid",
    )


class EmptyInput(StrictInput):
    pass


class AgentProjectFilterInput(StrictInput):
    """paginationを持たないpool一覧向けの任意Project filter。"""

    project_id: str | None = Field(default=None, min_length=1, max_length=6)


class AgentDomainForCreate(DomainForCreate):
    """Agent VM作成ではowner projectを受付時に確定する。"""

    model_config = StrictInput.model_config

    project_id: str = Field(min_length=1, max_length=6)


class AgentDomainProjectUpdateInput(StrictInput):
    """REST bodyから除いたVM UUIDをAgent actionでは明示的に受け取る。"""

    uuid: str = Field(min_length=1, max_length=255)
    project_id: str = Field(min_length=1, max_length=6)


class NetworkPoolDeleteInput(StrictInput):
    id: int


class StoragePoolDeleteInput(StrictInput):
    id: int


class NetworkOvsDeleteInput(StrictInput):
    name: str


class ImageDeleteInput(StrictInput):
    uuid: str
    name: str


class ProjectDeleteInput(StrictInput):
    project_id: str


class AgentProjectForCreate(StrictInput):
    """Project taskのpath外入力をAgent向けにも同じ名称で固定する。"""

    name: str = Field(min_length=1, max_length=64)
    member_ids: list[str] = Field(min_length=1, max_length=256)


class AgentProjectUpdateInput(StrictInput):
    project_id: str = Field(min_length=1, max_length=6)
    name: str = Field(min_length=1, max_length=64)


class AgentProjectMemberInput(StrictInput):
    project_id: str = Field(min_length=1, max_length=6)
    username: str = Field(min_length=1, max_length=255)


class AgentProjectResourceGrantsUpdateInput(StrictInput):
    project_id: str = Field(min_length=1, max_length=6)
    storage_pool_ids: list[int] = Field(default_factory=list, max_length=256)
    network_pool_ids: list[int] = Field(default_factory=list, max_length=256)
    flavor_ids: list[int] = Field(default_factory=list, max_length=256)


class AgentProjectMemberCandidatesInput(StrictInput):
    name_like: str | None = Field(default=None, max_length=255)
    limit: int = Field(default=25, ge=0, le=1000)
    page: int = Field(default=0, ge=0)


class AgentProjectResourceGrantCandidatesInput(StrictInput):
    """global admin向けresource grant候補取得のProject path input。"""

    project_id: str = Field(min_length=1, max_length=6)


class UserDeleteInput(StrictInput):
    username: str


class FlavorDeleteInput(StrictInput):
    flavor_id: int


class AgentUserCreateInput(StrictInput):
    """Project membershipを変更しないAgent専用の利用者作成input。"""

    username: str = Field(min_length=1, max_length=255)
    password: str = Field(
        min_length=8,
        max_length=128,
        pattern=r"^[^\s]+$",
        json_schema_extra={"writeOnly": True},
    )
    scopes: list[UserScope] = Field(default_factory=list, max_length=256)
    publickeys: list[UserPublickey] = Field(default_factory=list, max_length=64)

    @field_validator("password")
    @classmethod
    def strong_password(cls, value: str) -> str:
        categories = sum(
            bool(re.search(pattern, value))
            for pattern in (r"[a-z]", r"[A-Z]", r"\d", r"[^A-Za-z0-9]")
        )
        if categories < 4:
            raise ValueError(
                "Password must contain lower-case, upper-case, digit and symbol",
            )
        return value


class AgentUserUpdateInput(AgentUserCreateInput):
    """REST更新から分離したpassword更新をAgent向けに維持する。"""

    model_config = StrictInput.model_config

    path_username: str = Field(min_length=1, max_length=255)
