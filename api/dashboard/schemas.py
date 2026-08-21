from datetime import datetime
from typing import Literal

from mixin.schemas import BaseSchema


class DashboardBreakdown(BaseSchema):
    name: str
    count: int


class DashboardNodeSummary(BaseSchema):
    count: int
    core: int
    memory_gib: float
    roles: list[DashboardBreakdown]


class DashboardVmStatuses(BaseSchema):
    running: int
    stopped: int
    maintenance: int
    deleted: int
    lost_node: int
    unknown: int


class DashboardVmSummary(BaseSchema):
    count: int
    core: int
    memory_gib: float
    statuses: DashboardVmStatuses


class DashboardStoragePool(BaseSchema):
    uuid: str
    name: str
    node_name: str
    capacity_gib: int
    used_gib: int
    available_gib: int
    usage_percent: float | None


class DashboardStorageSummary(BaseSchema):
    count: int
    capacity_gib: int
    used_gib: int
    available_gib: int
    high_usage_count: int
    highest_usage: list[DashboardStoragePool]


class DashboardNetworkSummary(BaseSchema):
    count: int
    port_group_count: int
    types: list[DashboardBreakdown]


class DashboardImageSummary(BaseSchema):
    count: int


class DashboardRecentTask(BaseSchema):
    uuid: str
    user_id: str | None
    status: str | None
    resource: str
    object: str
    method: str
    post_time: datetime | None
    run_time: float | None


class DashboardTaskSummary(BaseSchema):
    incomplete_count: int
    failed_last_24_hours: int
    recent: list[DashboardRecentTask]


class DashboardResponse(BaseSchema):
    generated_at: datetime
    visibility: Literal["all", "assigned"]
    nodes: DashboardNodeSummary
    vms: DashboardVmSummary
    storages: DashboardStorageSummary
    networks: DashboardNetworkSummary
    images: DashboardImageSummary
    tasks: DashboardTaskSummary
