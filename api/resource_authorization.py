"""既存REST API向けのproject/object-level認可。

projectが参照するresource poolを正本とし、clientが送るnode名やproject IDだけを
認可根拠にしない。対応先を安全に導出できないglobal操作はrouter側でadmin限定にする。
"""

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from auth.router import CurrentUser
from domain.models import DomainModel
from flavor.models import FlavorModel
from network.models import (
    NetworkModel,
    NetworkPoolModel,
    associations_networks,
    associations_networks_pools,
)
from project.models import (
    ProjectModel,
    association_projects_to_flavors_pools,
    association_projects_to_networks_pools,
    association_projects_to_storages_pools,
)
from storage.models import (
    AssociationStoragePoolModel,
    StorageModel,
    StoragePoolModel,
)

def is_admin(current_user: CurrentUser) -> bool:
    return current_user.verify_scope(["admin"], return_bool=True)


def require_admin(current_user: CurrentUser) -> None:
    current_user.verify_scope(["admin"])


def _not_found(resource: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{resource} not found",
    )


def allowed_storage_pool_ids(
    db: Session,
    current_user: CurrentUser,
) -> set[int] | None:
    if is_admin(current_user):
        return None
    return {
        int(value)
        for (value,) in db.query(
            association_projects_to_storages_pools.c.storages_pools_id,
        ).filter(
            association_projects_to_storages_pools.c.projects_id.in_(
                current_user.projects,
            ),
        ).all()
    }


def allowed_storage_ids(
    db: Session,
    current_user: CurrentUser,
) -> set[str] | None:
    pool_ids = allowed_storage_pool_ids(db, current_user)
    if pool_ids is None:
        return None
    if not pool_ids:
        return set()
    return {
        str(value)
        for (value,) in db.query(
            AssociationStoragePoolModel.storage_uuid,
        ).filter(
            AssociationStoragePoolModel.pool_id.in_(pool_ids),
        ).all()
    }


def allowed_network_pool_ids(
    db: Session,
    current_user: CurrentUser,
) -> set[int] | None:
    if is_admin(current_user):
        return None
    return {
        int(value)
        for (value,) in db.query(
            association_projects_to_networks_pools.c.networks_pools_id,
        ).filter(
            association_projects_to_networks_pools.c.projects_id.in_(
                current_user.projects,
            ),
        ).all()
    }


def allowed_network_ids(
    db: Session,
    current_user: CurrentUser,
) -> set[str] | None:
    pool_ids = allowed_network_pool_ids(db, current_user)
    if pool_ids is None:
        return None
    if not pool_ids:
        return set()
    direct = db.query(associations_networks.c.network_uuid).filter(
        associations_networks.c.pool_id.in_(pool_ids),
    ).all()
    ports = db.query(associations_networks_pools.c.port_network_uuid).filter(
        associations_networks_pools.c.pool_id.in_(pool_ids),
    ).all()
    return {str(value) for (value,) in [*direct, *ports]}


def allowed_flavor_ids(
    db: Session,
    current_user: CurrentUser,
) -> set[int] | None:
    if is_admin(current_user):
        return None
    return {
        int(value)
        for (value,) in db.query(
            association_projects_to_flavors_pools.c.flavors_id,
        ).filter(
            association_projects_to_flavors_pools.c.projects_id.in_(
                current_user.projects,
            ),
        ).all()
    }


def allowed_node_names(
    db: Session,
    current_user: CurrentUser,
) -> set[str] | None:
    if is_admin(current_user):
        return None

    domain_nodes = {
        str(value)
        for (value,) in db.query(DomainModel.node_name).filter(
            or_(
                DomainModel.owner_user_id == current_user.id,
                DomainModel.owner_project_id.in_(current_user.projects),
            ),
        ).all()
    }
    storage_ids = allowed_storage_ids(db, current_user) or set()
    network_ids = allowed_network_ids(db, current_user) or set()
    storage_nodes = {
        str(value)
        for (value,) in db.query(StorageModel.node_name).filter(
            StorageModel.uuid.in_(storage_ids),
        ).all()
    }
    network_nodes = {
        str(value)
        for (value,) in db.query(NetworkModel.node_name).filter(
            NetworkModel.uuid.in_(network_ids),
        ).all()
    }
    return domain_nodes | storage_nodes | network_nodes


def get_authorized_storage(
    db: Session,
    storage_id: str,
    current_user: CurrentUser,
) -> StorageModel:
    row = db.get(StorageModel, storage_id)
    allowed = allowed_storage_ids(db, current_user)
    if row is None or (allowed is not None and row.uuid not in allowed):
        raise _not_found("storage")
    return row


def get_authorized_storage_pool(
    db: Session,
    pool_id: int,
    current_user: CurrentUser,
) -> StoragePoolModel:
    row = db.get(StoragePoolModel, pool_id)
    allowed = allowed_storage_pool_ids(db, current_user)
    if row is None or (allowed is not None and row.id not in allowed):
        raise _not_found("storage pool")
    return row


def get_authorized_network(
    db: Session,
    network_id: str,
    current_user: CurrentUser,
) -> NetworkModel:
    row = db.get(NetworkModel, network_id)
    allowed = allowed_network_ids(db, current_user)
    if row is None or (allowed is not None and row.uuid not in allowed):
        raise _not_found("network")
    return row


def get_authorized_network_pool(
    db: Session,
    pool_id: int,
    current_user: CurrentUser,
) -> NetworkPoolModel:
    row = db.get(NetworkPoolModel, pool_id)
    allowed = allowed_network_pool_ids(db, current_user)
    if row is None or (allowed is not None and row.id not in allowed):
        raise _not_found("network pool")
    return row


def get_authorized_flavor(
    db: Session,
    flavor_id: int,
    current_user: CurrentUser,
) -> FlavorModel:
    row = db.get(FlavorModel, flavor_id)
    allowed = allowed_flavor_ids(db, current_user)
    if row is None or (allowed is not None and row.id not in allowed):
        raise _not_found("flavor")
    return row


def get_authorized_project(
    db: Session,
    project_id: str,
    current_user: CurrentUser,
) -> ProjectModel:
    row = db.get(ProjectModel, project_id)
    if row is None or (
        not is_admin(current_user) and project_id not in current_user.projects
    ):
        raise _not_found("project")
    return row
