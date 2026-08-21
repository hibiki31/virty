from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, or_
from sqlalchemy.orm import Query, Session

from auth.router import CurrentUser, get_current_user
from domain.models import DomainModel
from mixin.database import get_db
from network.models import NetworkModel, NetworkPortgroupModel
from node.models import AssociationNodeToRoleModel, NodeModel
from project.models import ProjectModel
from storage.models import ImageModel, StorageModel
from task.models import TaskModel

from .schemas import (
    DashboardBreakdown,
    DashboardImageSummary,
    DashboardNetworkSummary,
    DashboardNodeSummary,
    DashboardRecentTask,
    DashboardResponse,
    DashboardStoragePool,
    DashboardStorageSummary,
    DashboardTaskSummary,
    DashboardVmStatuses,
    DashboardVmSummary,
)

app = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

VM_STATUS_FIELDS = {
    1: "running",
    5: "stopped",
    7: "maintenance",
    10: "deleted",
    20: "lost_node",
}
INCOMPLETE_TASK_STATUSES = ("wait", "init", "start")
FAILED_TASK_STATUSES = ("error", "lost")


def _get_node_summary(db: Session) -> DashboardNodeSummary:
    node_count, node_core, node_memory = db.query(
        func.count(NodeModel.name),
        func.coalesce(func.sum(NodeModel.core), 0),
        func.coalesce(func.sum(NodeModel.memory), 0),
    ).one()
    role_rows = db.query(
        AssociationNodeToRoleModel.role_name,
        func.count(AssociationNodeToRoleModel.node_name),
    ).group_by(AssociationNodeToRoleModel.role_name).all()
    roles = [
        DashboardBreakdown(name=name, count=count)
        for name, count in sorted(role_rows, key=lambda row: (-row[1], row[0]))
    ]

    return DashboardNodeSummary(
        count=node_count,
        core=node_core,
        memory_gib=float(node_memory),
        roles=roles,
    )


def _get_visible_vms(
    db: Session,
    current_user: CurrentUser,
    is_admin: bool,
) -> Query:
    query = db.query(DomainModel)
    if is_admin:
        return query
    return query.filter(or_(
        DomainModel.owner_user_id == current_user.id,
        DomainModel.owner_project.has(
            ProjectModel.users.any(username=current_user.id)
        ),
    ))


def _get_vm_summary(
    db: Session,
    current_user: CurrentUser,
    is_admin: bool,
) -> DashboardVmSummary:
    status_rows = _get_visible_vms(db, current_user, is_admin).with_entities(
        DomainModel.status,
        func.count(DomainModel.uuid),
        func.coalesce(func.sum(DomainModel.core), 0),
        func.coalesce(func.sum(DomainModel.memory), 0),
    ).group_by(DomainModel.status).all()

    statuses: dict[str, int] = {
        "running": 0,
        "stopped": 0,
        "maintenance": 0,
        "deleted": 0,
        "lost_node": 0,
        "unknown": 0,
    }
    count = 0
    core = 0
    memory_mib = 0
    for status, status_count, status_core, status_memory in status_rows:
        count += status_count
        if status != 10:
            core += status_core
            memory_mib += status_memory
        status_name = VM_STATUS_FIELDS.get(status, "unknown")
        statuses[status_name] += status_count

    return DashboardVmSummary(
        count=count,
        core=core,
        memory_gib=memory_mib / 1024,
        statuses=DashboardVmStatuses(**statuses),
    )


def _get_storage_summary(db: Session) -> DashboardStorageSummary:
    storage_rows = db.query(
        StorageModel.uuid,
        StorageModel.name,
        StorageModel.node_name,
        StorageModel.capacity,
        StorageModel.available,
    ).all()

    pools: list[DashboardStoragePool] = []
    capacity_gib = 0
    used_gib = 0
    available_gib = 0
    high_usage_count = 0
    for uuid, name, node_name, capacity, available in storage_rows:
        normalized_capacity = max(int(capacity or 0), 0)
        normalized_available = max(int(available or 0), 0)
        used = max(normalized_capacity - normalized_available, 0)
        usage_percent = None
        if normalized_capacity > 0:
            raw_usage_percent = used / normalized_capacity * 100
            usage_percent = round(raw_usage_percent, 1)
            if raw_usage_percent > 80:
                high_usage_count += 1
        pools.append(DashboardStoragePool(
            uuid=uuid,
            name=name or "unknown",
            node_name=node_name or "unknown",
            capacity_gib=normalized_capacity,
            used_gib=used,
            available_gib=normalized_available,
            usage_percent=usage_percent,
        ))
        capacity_gib += normalized_capacity
        used_gib += used
        available_gib += normalized_available

    pools.sort(key=lambda pool: (
        pool.usage_percent is None,
        -(pool.usage_percent or 0),
        pool.name,
        pool.node_name,
        pool.uuid,
    ))

    return DashboardStorageSummary(
        count=len(storage_rows),
        capacity_gib=capacity_gib,
        used_gib=used_gib,
        available_gib=available_gib,
        high_usage_count=high_usage_count,
        highest_usage=pools[:4],
    )


def _get_network_summary(db: Session) -> DashboardNetworkSummary:
    type_rows = db.query(
        NetworkModel.type,
        func.count(NetworkModel.uuid),
    ).group_by(NetworkModel.type).all()
    type_counts: dict[str, int] = {}
    for name, count in type_rows:
        normalized_name = name or "unknown"
        type_counts[normalized_name] = type_counts.get(normalized_name, 0) + count
    network_types = [
        DashboardBreakdown(name=name, count=count)
        for name, count in sorted(type_counts.items(), key=lambda row: (-row[1], row[0]))
    ]
    port_group_count = db.query(func.count(NetworkPortgroupModel.name)).scalar() or 0

    return DashboardNetworkSummary(
        count=sum(item.count for item in network_types),
        port_group_count=port_group_count,
        types=network_types,
    )


def _get_task_summary(
    db: Session,
    current_user: CurrentUser,
    is_admin: bool,
    generated_at: datetime,
) -> DashboardTaskSummary:
    query = db.query(TaskModel)
    if not is_admin:
        query = query.filter(TaskModel.user_id == current_user.id)

    incomplete_count = query.filter(
        TaskModel.status.in_(INCOMPLETE_TASK_STATUSES)
    ).count()
    failed_last_24_hours = query.filter(
        TaskModel.status.in_(FAILED_TASK_STATUSES),
        func.coalesce(TaskModel.update_time, TaskModel.post_time)
        >= generated_at - timedelta(hours=24),
    ).count()
    recent_rows = query.with_entities(
        TaskModel.uuid,
        TaskModel.user_id,
        TaskModel.status,
        TaskModel.resource,
        TaskModel.object,
        TaskModel.method,
        TaskModel.post_time,
        TaskModel.run_time,
    ).order_by(
        TaskModel.post_time.desc().nullslast(),
        TaskModel.uuid.desc(),
    ).limit(6).all()
    recent = [
        DashboardRecentTask(
            uuid=uuid,
            user_id=user_id,
            status=status,
            resource=resource or "unknown",
            object=object or "unknown",
            method=method or "unknown",
            post_time=post_time,
            run_time=run_time,
        )
        for (
            uuid,
            user_id,
            status,
            resource,
            object,
            method,
            post_time,
            run_time,
        ) in recent_rows
    ]

    return DashboardTaskSummary(
        incomplete_count=incomplete_count,
        failed_last_24_hours=failed_last_24_hours,
        recent=recent,
    )


@app.get("", response_model=DashboardResponse)
def get_dashboard(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardResponse:
    generated_at = datetime.now(UTC)
    is_admin = "admin" in current_user.scopes

    return DashboardResponse(
        generated_at=generated_at,
        visibility="all" if is_admin else "assigned",
        nodes=_get_node_summary(db),
        vms=_get_vm_summary(db, current_user, is_admin),
        storages=_get_storage_summary(db),
        networks=_get_network_summary(db),
        images=DashboardImageSummary(count=db.query(ImageModel).count()),
        tasks=_get_task_summary(db, current_user, is_admin, generated_at),
    )
