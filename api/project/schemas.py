from typing import Literal

from pydantic import Field, field_validator

from mixin.schemas import BaseSchema


def _normalize_project_name(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError("Project名を空にはできません")
    return normalized


class ProjectForCreate(BaseSchema):
    name: str = Field(min_length=1, max_length=64)
    member_ids: list[str] = Field(min_length=1)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return _normalize_project_name(value)

    @field_validator("member_ids")
    @classmethod
    def normalize_member_ids(cls, values: list[str]) -> list[str]:
        normalized = list(dict.fromkeys(value.strip() for value in values))
        if not normalized or any(not value for value in normalized):
            raise ValueError("Project memberを1名以上指定してください")
        return normalized


class ProjectForNameUpdate(BaseSchema):
    name: str = Field(min_length=1, max_length=64)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return _normalize_project_name(value)


class ProjectForQuery(BaseSchema):
    admin: bool = False
    limit: int = Field(default=25, ge=0, le=1000)
    page: int = Field(default=0, ge=0)
    name_like: str | None = Field(default=None, max_length=255)


class ProjectMemberForQuery(BaseSchema):
    limit: int = Field(default=25, ge=0, le=1000)
    page: int = Field(default=0, ge=0)
    name_like: str | None = Field(default=None, max_length=255)


class ProjectMember(BaseSchema):
    username: str


class ProjectMemberPage(BaseSchema):
    count: int
    data: list[ProjectMember]


class ProjectUsage(BaseSchema):
    core: int
    memory_g: float
    storage_g: int


class ProjectLimits(BaseSchema):
    core: int
    memory_g: int
    storage_capacity_g: int | None
    enforced: Literal[False] = False


class ProjectResourceReference(BaseSchema):
    id: int
    name: str


class ProjectResourceGrantsUpdate(BaseSchema):
    storage_pool_ids: list[int]
    network_pool_ids: list[int]
    flavor_ids: list[int]

    @field_validator("storage_pool_ids", "network_pool_ids", "flavor_ids")
    @classmethod
    def normalize_ids(cls, values: list[int]) -> list[int]:
        if any(value <= 0 for value in values):
            raise ValueError("Resource IDは正の整数で指定してください")
        return sorted(set(values))


class ProjectResourceGrantCandidates(BaseSchema):
    storage_pools: list[ProjectResourceReference]
    network_pools: list[ProjectResourceReference]
    flavors: list[ProjectResourceReference]


class ProjectSummary(BaseSchema):
    id: str
    name: str
    member_count: int
    used_core: int
    used_memory_g: float
    used_storage_g: int


class ProjectDetail(ProjectSummary):
    limits: ProjectLimits
    members: list[ProjectMember]
    resource_grants: ProjectResourceGrantsUpdate
    storage_pools: list[ProjectResourceReference]
    network_pools: list[ProjectResourceReference]
    flavors: list[ProjectResourceReference]


class ProjectPage(BaseSchema):
    count: int
    data: list[ProjectSummary]
