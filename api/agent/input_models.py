"""既存APIに専用schemaがないAgent actionのstrict input。"""

from pydantic import ConfigDict, Field

from domain.schemas import DomainForCreate
from mixin.schemas import BaseSchema
from user.schemas import UserForCreate


class StrictInput(BaseSchema):
    model_config = ConfigDict(
        alias_generator=BaseSchema.model_config["alias_generator"],
        from_attributes=True,
        populate_by_name=True,
        extra="forbid",
    )


class EmptyInput(StrictInput):
    pass


class AgentDomainForCreate(DomainForCreate):
    """Agent VM作成ではowner projectを受付時に確定する。"""

    model_config = StrictInput.model_config

    project_id: str = Field(min_length=1, max_length=64)


class AgentDomainProjectUpdateInput(StrictInput):
    """REST bodyから除いたVM UUIDをAgent actionでは明示的に受け取る。"""

    uuid: str = Field(min_length=1, max_length=255)
    project_id: str = Field(min_length=1, max_length=255)


class NetworkPoolDeleteInput(StrictInput):
    id: int


class NetworkOvsDeleteInput(StrictInput):
    name: str


class ImageDeleteInput(StrictInput):
    uuid: str
    name: str


class ProjectDeleteInput(StrictInput):
    project_id: str


class UserDeleteInput(StrictInput):
    username: str


class FlavorDeleteInput(StrictInput):
    flavor_id: int


class AgentUserUpdateInput(UserForCreate):
    """REST更新から分離したpassword・project更新をAgent向けに維持する。"""

    model_config = StrictInput.model_config

    path_username: str = Field(min_length=1, max_length=255)
