from collections.abc import Iterable

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from domain.models import DomainModel
from flavor.models import FlavorModel
from network.models import NetworkPoolModel
from resource_authorization import (
    domain_resource_conflicts,
    network_grants_for_pool_ids,
    project_flavor_ids,
    project_network_pool_ids,
    project_storage_pool_ids,
)
from storage.models import (
    AssociationStoragePoolModel,
    ImageModel,
    StoragePoolModel,
)
from user.models import UserModel, association_users_to_projects

from .models import (
    ProjectModel,
    association_projects_to_flavors_pools,
    association_projects_to_networks_pools,
    association_projects_to_storages_pools,
    generate_project_id,
)
from .schemas import ProjectResourceGrantsUpdate


class ProjectServiceError(ValueError):
    """Project操作でclientへ安全に返せる検証エラー。"""


class ProjectNotFoundError(ProjectServiceError):
    pass


class ProjectMemberNotFoundError(ProjectServiceError):
    pass


class ProjectGrantNotFoundError(ProjectServiceError):
    pass


class ProjectConflictError(ProjectServiceError):
    pass


def lock_project(db: Session, project_id: str) -> ProjectModel:
    """Project行をlockし、変更対象relationshipを最新状態へ読み直す。"""

    locked_id = (
        db.query(ProjectModel.id)
        .filter(ProjectModel.id == project_id)
        .with_for_update()
        .scalar()
    )
    if locked_id is None:
        raise ProjectNotFoundError("Projectが見つかりません")
    project = db.get(ProjectModel, project_id)
    if project is None:
        raise ProjectNotFoundError("Projectが見つかりません")
    relationships = ["users", "storage_pools", "network_pools", "flavors"]
    db.expire(project, relationships)
    for relationship in relationships:
        getattr(project, relationship)
    return project


def _normalize_name(name: str) -> str:
    normalized = name.strip()
    if not 1 <= len(normalized) <= 64:
        raise ProjectConflictError("Project名は1〜64文字で指定してください")
    return normalized


def create_project_with_members(
    db: Session,
    *,
    name: str,
    member_ids: Iterable[str],
) -> ProjectModel:
    """明示されたmemberだけを含むProjectを衝突retry付きで作る。"""

    normalized_member_ids = set(member_ids)
    users = (
        db.query(UserModel)
        .filter(UserModel.username.in_(normalized_member_ids))
        .all()
    )
    if {user.username for user in users} != normalized_member_ids:
        raise ProjectMemberNotFoundError("指定されたProject memberが見つかりません")

    for _ in range(16):
        project = ProjectModel(
            id=generate_project_id(),
            name=_normalize_name(name),
            users=users,
        )
        try:
            with db.begin_nested():
                db.add(project)
                db.flush()
        except IntegrityError:
            # 6桁IDの競合だけをretryする。その他の整合性違反は次の検査で顕在化する。
            continue
        return project
    raise ProjectConflictError("Project IDを安全に採番できませんでした")


def rename_project(project: ProjectModel, name: str) -> ProjectModel:
    project.name = _normalize_name(name)
    return project


def add_project_member(
    db: Session,
    project: ProjectModel,
    username: str,
) -> ProjectModel:
    user = db.get(UserModel, username)
    if user is None:
        raise ProjectMemberNotFoundError("指定された利用者が見つかりません")
    if all(member.username != username for member in project.users):
        project.users.append(user)
    return project


def remove_project_member(
    project: ProjectModel,
    username: str,
) -> ProjectModel:
    member = next(
        (member for member in project.users if member.username == username),
        None,
    )
    if member is None:
        # DELETEを冪等にし、既に非memberなら現在の状態を返す。
        return project
    if len(project.users) == 1:
        raise ProjectConflictError("Projectから最後のmemberは削除できません")
    project.users.remove(member)
    return project


def ensure_user_memberships_deletable(db: Session, username: str) -> None:
    """User削除がProjectの最後のmemberを暗黙削除しないことを確認する。"""

    project_ids = sorted({
        str(project_id)
        for (project_id,) in db.query(
            association_users_to_projects.c.project_id,
        ).filter(
            association_users_to_projects.c.user_id == username,
        ).all()
    })
    for project_id in project_ids:
        db.query(ProjectModel.id).filter(
            ProjectModel.id == project_id,
        ).with_for_update().scalar()
        member_count = db.query(
            association_users_to_projects.c.user_id,
        ).filter(
            association_users_to_projects.c.project_id == project_id,
        ).count()
        if member_count <= 1:
            raise ProjectConflictError(
                "Projectの最後のmemberである利用者は削除できません"
            )


def ensure_project_deletable(
    db: Session,
    project_id: str,
    *,
    lock: bool = False,
) -> ProjectModel:
    if lock:
        locked_id = (
            db.query(ProjectModel.id)
            .filter(ProjectModel.id == project_id)
            .with_for_update()
            .scalar()
        )
        if locked_id is None:
            raise ProjectNotFoundError("Projectが見つかりません")
    project = db.get(ProjectModel, project_id)
    if project is None:
        raise ProjectNotFoundError("Projectが見つかりません")
    if (
        db.query(DomainModel.uuid)
        .filter(DomainModel.owner_project_id == project_id)
        .first()
        is not None
    ):
        raise ProjectConflictError("VMが所属しているProjectは削除できません")
    return project


def _used_flavor_ids(
    db: Session,
    project_id: str,
) -> set[int]:
    domains = (
        db.query(DomainModel)
        .filter(DomainModel.owner_project_id == project_id)
        .all()
    )
    domain_ids = {domain.uuid for domain in domains}
    if not domains:
        return set()
    drive_sources = {
        drive.source
        for domain in domains
        for drive in domain.drives
        if drive.source is not None and drive.device == "disk"
    }
    image_query = db.query(ImageModel.flavor_id).filter(
        ImageModel.domain_uuid.in_(domain_ids)
    )
    if drive_sources:
        image_query = db.query(ImageModel.flavor_id).filter(
            or_(
                ImageModel.domain_uuid.in_(domain_ids),
                ImageModel.path.in_(drive_sources),
            )
        )
    return {
        int(flavor_id)
        for (flavor_id,) in image_query.all()
        if flavor_id is not None
    }


def _validate_grant_removal(
    db: Session,
    *,
    project_id: str,
    storage_pool_ids: set[int],
    network_pool_ids: set[int],
    flavor_ids: set[int],
) -> None:
    granted_storage_ids = {
        str(storage_uuid)
        for (storage_uuid,) in db.query(AssociationStoragePoolModel.storage_uuid)
        .filter(AssociationStoragePoolModel.pool_id.in_(storage_pool_ids))
        .all()
    }
    granted_network_ids, granted_network_ports = network_grants_for_pool_ids(
        db,
        network_pool_ids,
    )
    _validate_project_resource_coverage(
        db,
        project_id=project_id,
        storage_ids=granted_storage_ids,
        network_ids=granted_network_ids,
        network_ports=granted_network_ports,
        flavor_ids=flavor_ids,
    )


def _validate_project_resource_coverage(
    db: Session,
    *,
    project_id: str,
    storage_ids: set[str],
    network_ids: set[str],
    network_ports: set[tuple[str, str]],
    flavor_ids: set[int],
) -> None:
    for domain in db.query(DomainModel).filter(
        DomainModel.owner_project_id == project_id,
    ):
        conflicts = domain_resource_conflicts(
            db,
            domain,
            storage_ids=storage_ids,
            network_ids=network_ids,
            network_ports=network_ports,
        )
        if conflicts:
            raise ProjectConflictError(
                "使用中VMが依存するresource grantは解除できません: "
                + ", ".join(conflicts)
            )

    used_flavor_ids = _used_flavor_ids(db, project_id)
    if not used_flavor_ids.issubset(flavor_ids):
        raise ProjectConflictError("使用中VMが依存するflavor grantは解除できません")


def replace_project_resource_grants(
    db: Session,
    project: ProjectModel,
    request: ProjectResourceGrantsUpdate,
) -> ProjectModel:
    storage_ids = set(request.storage_pool_ids)
    network_ids = set(request.network_pool_ids)
    flavor_ids = set(request.flavor_ids)

    storage_pools = (
        db.query(StoragePoolModel).filter(StoragePoolModel.id.in_(storage_ids)).all()
    )
    network_pools = (
        db.query(NetworkPoolModel).filter(NetworkPoolModel.id.in_(network_ids)).all()
    )
    flavors = db.query(FlavorModel).filter(FlavorModel.id.in_(flavor_ids)).all()
    if {pool.id for pool in storage_pools} != storage_ids:
        raise ProjectGrantNotFoundError("指定されたstorage poolが見つかりません")
    if {pool.id for pool in network_pools} != network_ids:
        raise ProjectGrantNotFoundError("指定されたnetwork poolが見つかりません")
    if {flavor.id for flavor in flavors} != flavor_ids:
        raise ProjectGrantNotFoundError("指定されたflavorが見つかりません")

    _validate_grant_removal(
        db,
        project_id=project.id,
        storage_pool_ids=storage_ids,
        network_pool_ids=network_ids,
        flavor_ids=flavor_ids,
    )
    project.storage_pools = sorted(storage_pools, key=lambda pool: pool.id)
    project.network_pools = sorted(network_pools, key=lambda pool: pool.id)
    project.flavors = sorted(flavors, key=lambda flavor: flavor.id)
    return project


def ensure_network_pool_deletable(db: Session, pool_id: int) -> NetworkPoolModel:
    """network pool削除がProject所属VMのgrantを暗黙解除しないことを確認する。"""
    locked_pool_id = (
        db.query(NetworkPoolModel.id)
        .filter(NetworkPoolModel.id == pool_id)
        .with_for_update()
        .scalar()
    )
    if locked_pool_id is None:
        raise ProjectGrantNotFoundError("指定されたnetwork poolが見つかりません")

    project_ids = sorted({
        str(project_id)
        for (project_id,) in db.query(
            association_projects_to_networks_pools.c.projects_id,
        ).filter(
            association_projects_to_networks_pools.c.networks_pools_id == pool_id,
        ).all()
    })
    for project_id in project_ids:
        db.query(ProjectModel.id).filter(
            ProjectModel.id == project_id,
        ).with_for_update().scalar()
        _validate_grant_removal(
            db,
            project_id=project_id,
            storage_pool_ids=project_storage_pool_ids(db, project_id),
            network_pool_ids=project_network_pool_ids(db, project_id) - {pool_id},
            flavor_ids=project_flavor_ids(db, project_id),
        )

    pool = db.get(NetworkPoolModel, pool_id)
    if pool is None:
        raise ProjectGrantNotFoundError("指定されたnetwork poolが見つかりません")
    return pool


def ensure_storage_pool_update_allowed(
    db: Session,
    pool_id: int,
    storage_ids: set[str],
) -> StoragePoolModel:
    """storage pool更新が使用中VMのgrantを暗黙解除しないことを確認する。"""

    locked_pool_id = (
        db.query(StoragePoolModel.id)
        .filter(StoragePoolModel.id == pool_id)
        .with_for_update()
        .scalar()
    )
    if locked_pool_id is None:
        raise ProjectGrantNotFoundError("指定されたstorage poolが見つかりません")

    project_ids = sorted({
        str(project_id)
        for (project_id,) in db.query(
            association_projects_to_storages_pools.c.projects_id,
        ).filter(
            association_projects_to_storages_pools.c.storages_pools_id == pool_id,
        ).all()
    })
    for project_id in project_ids:
        db.query(ProjectModel.id).filter(
            ProjectModel.id == project_id,
        ).with_for_update().scalar()
        remaining_pool_ids = project_storage_pool_ids(db, project_id) - {pool_id}
        granted_storage_ids = {
            str(storage_uuid)
            for (storage_uuid,) in db.query(
                AssociationStoragePoolModel.storage_uuid,
            ).filter(
                AssociationStoragePoolModel.pool_id.in_(remaining_pool_ids),
            ).all()
        }
        granted_storage_ids.update(storage_ids)
        granted_network_ids, granted_network_ports = network_grants_for_pool_ids(
            db,
            project_network_pool_ids(db, project_id),
        )
        _validate_project_resource_coverage(
            db,
            project_id=project_id,
            storage_ids=granted_storage_ids,
            network_ids=granted_network_ids,
            network_ports=granted_network_ports,
            flavor_ids=project_flavor_ids(db, project_id),
        )

    pool = db.get(StoragePoolModel, pool_id)
    if pool is None:
        raise ProjectGrantNotFoundError("指定されたstorage poolが見つかりません")
    return pool


def ensure_storage_pool_deletable(db: Session, pool_id: int) -> StoragePoolModel:
    """storage pool削除を、空集合への完全置換と同じ境界で検証する。"""

    return ensure_storage_pool_update_allowed(db, pool_id, set())


def remove_storage_pool(db: Session, pool: StoragePoolModel) -> None:
    """複合主キーassociationを先に削除してstorage pool本体を除去する。"""

    db.query(AssociationStoragePoolModel).filter(
        AssociationStoragePoolModel.pool_id == pool.id,
    ).delete(synchronize_session="fetch")
    db.expire(pool, ["storages"])
    db.delete(pool)


def ensure_flavor_deletable(db: Session, flavor_id: int) -> FlavorModel:
    """flavor削除が使用中VMのgrantを暗黙解除しないことを確認する。"""

    locked_flavor_id = (
        db.query(FlavorModel.id)
        .filter(FlavorModel.id == flavor_id)
        .with_for_update()
        .scalar()
    )
    if locked_flavor_id is None:
        raise ProjectGrantNotFoundError("指定されたflavorが見つかりません")

    project_ids = sorted({
        str(project_id)
        for (project_id,) in db.query(
            association_projects_to_flavors_pools.c.projects_id,
        ).filter(
            association_projects_to_flavors_pools.c.flavors_id == flavor_id,
        ).all()
    })
    for project_id in project_ids:
        db.query(ProjectModel.id).filter(
            ProjectModel.id == project_id,
        ).with_for_update().scalar()
        if flavor_id in _used_flavor_ids(db, project_id):
            raise ProjectConflictError(
                "使用中VMが依存するflavor grantは解除できません"
            )

    flavor = db.get(FlavorModel, flavor_id)
    if flavor is None:
        raise ProjectGrantNotFoundError("指定されたflavorが見つかりません")
    return flavor
