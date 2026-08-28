"""共有resource削除前のProject/VM依存検査。

RESTとAgentの受付処理、workerの実行直前で同じ関数を呼び、Project grantや
VM参照を迂回して管理node側のresourceだけが削除されることを防ぐ。
"""

from collections.abc import Callable

from sqlalchemy import or_
from sqlalchemy.orm import Session

from domain.models import DomainDriveModel, DomainInterfaceModel, DomainModel
from network.models import (
    NetworkModel,
    NetworkPortgroupModel,
    associations_networks,
    associations_networks_pools,
)
from project.models import (
    ProjectModel,
    association_projects_to_networks_pools,
    association_projects_to_storages_pools,
)
from storage.models import (
    AssociationStoragePoolModel,
    ImageModel,
    StorageModel,
)


class ResourceDeletionError(ValueError):
    """resource削除でclientへ安全に返せる検証エラー。"""


class ResourceDeletionNotFoundError(ResourceDeletionError):
    pass


class ResourceDeletionConflictError(ResourceDeletionError):
    pass


def _lock_projects(db: Session, project_ids: set[str]) -> None:
    """Project mutationと同じProject行を固定順でlockする。"""

    if not project_ids:
        return
    db.query(ProjectModel.id).filter(
        ProjectModel.id.in_(sorted(project_ids)),
    ).order_by(ProjectModel.id).with_for_update().all()


def _lock_domains(db: Session, domain_ids: set[str]) -> None:
    if not domain_ids:
        return
    db.query(DomainModel.uuid).filter(
        DomainModel.uuid.in_(sorted(domain_ids)),
    ).order_by(DomainModel.uuid).with_for_update().all()


def _project_ids_for_domains(db: Session, domain_ids: set[str]) -> set[str]:
    if not domain_ids:
        return set()
    return {
        str(project_id)
        for (project_id,) in db.query(DomainModel.owner_project_id).filter(
            DomainModel.uuid.in_(domain_ids),
            DomainModel.owner_project_id.is_not(None),
        ).all()
    }


def _project_ids_for_storage_grant(db: Session, storage_uuid: str) -> set[str]:
    pool_ids = {
        int(pool_id)
        for (pool_id,) in db.query(AssociationStoragePoolModel.pool_id).filter(
            AssociationStoragePoolModel.storage_uuid == storage_uuid,
        ).all()
    }
    if not pool_ids:
        return set()
    return {
        str(project_id)
        for (project_id,) in db.query(
            association_projects_to_storages_pools.c.projects_id,
        ).filter(
            association_projects_to_storages_pools.c.storages_pools_id.in_(
                pool_ids,
            ),
        ).all()
    }


def _network_pool_ids(
    db: Session,
    network_uuid: str,
    port_name: str | None = None,
) -> set[int]:
    """network全体または対象portを含むpool IDを返す。"""

    result = {
        int(pool_id)
        for (pool_id,) in db.query(associations_networks.c.pool_id).filter(
            associations_networks.c.network_uuid == network_uuid,
        ).all()
    }
    port_query = db.query(associations_networks_pools.c.pool_id).filter(
        associations_networks_pools.c.port_network_uuid == network_uuid,
    )
    if port_name is not None:
        port_query = port_query.filter(
            associations_networks_pools.c.port_name == port_name,
        )
    result.update(int(pool_id) for (pool_id,) in port_query.all())
    return result


def _project_ids_for_network_grant(
    db: Session,
    network_uuid: str,
    port_name: str | None = None,
) -> set[str]:
    pool_ids = _network_pool_ids(db, network_uuid, port_name)
    if not pool_ids:
        return set()
    return {
        str(project_id)
        for (project_id,) in db.query(
            association_projects_to_networks_pools.c.projects_id,
        ).filter(
            association_projects_to_networks_pools.c.networks_pools_id.in_(
                pool_ids,
            ),
        ).all()
    }


def _path_is_in_storage(source: str, storage_path: str | None) -> bool:
    if not storage_path:
        return False
    base = storage_path.rstrip("/") or "/"
    if base == "/":
        return source.startswith("/")
    return source == base or source.startswith(f"{base}/")


def _storage_domain_ids(db: Session, storage: StorageModel) -> set[str]:
    images = db.query(ImageModel.path, ImageModel.domain_uuid).filter(
        ImageModel.storage_uuid == storage.uuid,
    ).all()
    image_paths = {str(path) for path, _ in images if path is not None}
    result = {
        str(domain_uuid)
        for _, domain_uuid in images
        if domain_uuid is not None
    }
    for domain_uuid, source in db.query(
        DomainDriveModel.domain_uuid,
        DomainDriveModel.source,
    ).join(
        DomainModel,
        DomainModel.uuid == DomainDriveModel.domain_uuid,
    ).filter(
        DomainModel.node_name == storage.node_name,
        DomainDriveModel.source.is_not(None),
    ).all():
        if source in image_paths or _path_is_in_storage(str(source), storage.path):
            result.add(str(domain_uuid))
    return result


def _image_domain_ids(
    db: Session,
    storage: StorageModel,
    images: list[ImageModel],
) -> set[str]:
    paths = {str(image.path) for image in images}
    result = {
        str(image.domain_uuid)
        for image in images
        if image.domain_uuid is not None
    }
    if paths:
        result.update(
            str(domain_uuid)
            for (domain_uuid,) in db.query(DomainDriveModel.domain_uuid).join(
                DomainModel,
                DomainModel.uuid == DomainDriveModel.domain_uuid,
            ).filter(
                DomainModel.node_name == storage.node_name,
                DomainDriveModel.source.in_(paths),
            ).all()
        )
    return result


def _network_domain_ids(db: Session, network: NetworkModel) -> set[str]:
    network_names = {str(network.uuid), str(network.name)}
    query = db.query(DomainInterfaceModel.domain_uuid).join(
        DomainModel,
        DomainModel.uuid == DomainInterfaceModel.domain_uuid,
    ).filter(DomainModel.node_name == network.node_name)
    conditions = [DomainInterfaceModel.network.in_(network_names)]
    if network.bridge:
        conditions.append(DomainInterfaceModel.bridge == network.bridge)
    return {
        str(domain_uuid)
        for (domain_uuid,) in query.filter(or_(*conditions)).all()
    }


def _network_port_domain_ids(
    db: Session,
    network: NetworkModel,
    port: NetworkPortgroupModel,
) -> set[str]:
    network_names = {str(network.uuid), str(network.name)}
    port_conditions = [DomainInterfaceModel.port == port.name]
    if port.is_default:
        port_conditions.extend([
            DomainInterfaceModel.port.is_(None),
            DomainInterfaceModel.port == "",
        ])
    return {
        str(domain_uuid)
        for (domain_uuid,) in db.query(DomainInterfaceModel.domain_uuid).join(
            DomainModel,
            DomainModel.uuid == DomainInterfaceModel.domain_uuid,
        ).filter(
            DomainModel.node_name == network.node_name,
            DomainInterfaceModel.network.in_(network_names),
            or_(*port_conditions),
        ).all()
    }


def _lock_dependency_context(
    db: Session,
    *,
    grant_project_ids: set[str],
    domain_ids: set[str],
) -> None:
    _lock_domains(db, domain_ids)
    _lock_projects(
        db,
        grant_project_ids | _project_ids_for_domains(db, domain_ids),
    )


def _lock_and_recheck(
    db: Session,
    *,
    target_lock: Callable[[], bool],
    dependency_state: Callable[[], tuple[set[str], set[str]]],
) -> tuple[set[str], set[str]]:
    """Domain→Project→対象resourceの順でlockして依存を再確認する。"""

    grant_project_ids, domain_ids = dependency_state()
    _lock_dependency_context(
        db,
        grant_project_ids=grant_project_ids,
        domain_ids=domain_ids,
    )
    if not target_lock():
        raise ResourceDeletionNotFoundError("削除対象resourceが見つかりません")

    # Project lock取得前にcommitされたgrant/VM変更を、対象lock取得後に拾う。
    grant_project_ids, domain_ids = dependency_state()
    _lock_dependency_context(
        db,
        grant_project_ids=grant_project_ids,
        domain_ids=domain_ids,
    )
    return grant_project_ids, domain_ids


def ensure_storage_deletable(db: Session, storage_uuid: str) -> StorageModel:
    storage = db.get(StorageModel, storage_uuid)
    if storage is None:
        raise ResourceDeletionNotFoundError("storageが見つかりません")

    def state() -> tuple[set[str], set[str]]:
        current = db.get(StorageModel, storage_uuid)
        if current is None:
            return set(), set()
        return (
            _project_ids_for_storage_grant(db, storage_uuid),
            _storage_domain_ids(db, current),
        )

    granted_projects, domain_ids = _lock_and_recheck(
        db,
        target_lock=lambda: db.query(StorageModel.uuid).filter(
            StorageModel.uuid == storage_uuid,
        ).with_for_update().scalar() is not None,
        dependency_state=state,
    )
    if granted_projects:
        raise ResourceDeletionConflictError(
            "Projectへgrant中のstorageはpoolから解除するまで削除できません"
        )
    if domain_ids:
        raise ResourceDeletionConflictError(
            "VMのdiskまたはCD-ROMが参照中のstorageは削除できません"
        )
    current = db.get(StorageModel, storage_uuid)
    if current is None:  # pragma: no cover - target lock後の防御
        raise ResourceDeletionNotFoundError("storageが見つかりません")
    return current


def ensure_image_deletable(
    db: Session,
    storage_uuid: str,
    image_name: str,
) -> list[ImageModel]:
    storage = db.get(StorageModel, storage_uuid)
    if storage is None:
        raise ResourceDeletionNotFoundError("storageが見つかりません")
    images = db.query(ImageModel).filter(
        ImageModel.storage_uuid == storage_uuid,
        ImageModel.name == image_name,
    ).all()
    if not images:
        raise ResourceDeletionNotFoundError("imageが見つかりません")

    def state() -> tuple[set[str], set[str]]:
        current_images = db.query(ImageModel).filter(
            ImageModel.storage_uuid == storage_uuid,
            ImageModel.name == image_name,
        ).all()
        return (
            _project_ids_for_storage_grant(db, storage_uuid),
            _image_domain_ids(db, storage, current_images),
        )

    _, domain_ids = _lock_and_recheck(
        db,
        target_lock=lambda: bool(
            db.query(ImageModel.path).filter(
                ImageModel.storage_uuid == storage_uuid,
                ImageModel.name == image_name,
            ).order_by(ImageModel.path).with_for_update().all()
        ),
        dependency_state=state,
    )
    if domain_ids:
        raise ResourceDeletionConflictError(
            "VMのdiskまたはCD-ROMが参照中のimageは削除できません"
        )
    return db.query(ImageModel).filter(
        ImageModel.storage_uuid == storage_uuid,
        ImageModel.name == image_name,
    ).order_by(ImageModel.path).all()


def ensure_network_deletable(db: Session, network_uuid: str) -> NetworkModel:
    network = db.get(NetworkModel, network_uuid)
    if network is None:
        raise ResourceDeletionNotFoundError("networkが見つかりません")

    def state() -> tuple[set[str], set[str]]:
        current = db.get(NetworkModel, network_uuid)
        if current is None:
            return set(), set()
        return (
            _project_ids_for_network_grant(db, network_uuid),
            _network_domain_ids(db, current),
        )

    granted_projects, domain_ids = _lock_and_recheck(
        db,
        target_lock=lambda: db.query(NetworkModel.uuid).filter(
            NetworkModel.uuid == network_uuid,
        ).with_for_update().scalar() is not None,
        dependency_state=state,
    )
    if granted_projects:
        raise ResourceDeletionConflictError(
            "Projectへgrant中のnetworkはpoolから解除するまで削除できません"
        )
    if domain_ids:
        raise ResourceDeletionConflictError(
            "VM interfaceが参照中のnetworkは削除できません"
        )
    current = db.get(NetworkModel, network_uuid)
    if current is None:  # pragma: no cover - target lock後の防御
        raise ResourceDeletionNotFoundError("networkが見つかりません")
    return current


def ensure_network_port_deletable(
    db: Session,
    network_uuid: str,
    port_name: str,
) -> NetworkPortgroupModel:
    network = db.get(NetworkModel, network_uuid)
    port = db.query(NetworkPortgroupModel).filter(
        NetworkPortgroupModel.network_uuid == network_uuid,
        NetworkPortgroupModel.name == port_name,
    ).one_or_none()
    if network is None or port is None:
        raise ResourceDeletionNotFoundError("networkまたはportgroupが見つかりません")

    def state() -> tuple[set[str], set[str]]:
        current_port = db.query(NetworkPortgroupModel).filter(
            NetworkPortgroupModel.network_uuid == network_uuid,
            NetworkPortgroupModel.name == port_name,
        ).one_or_none()
        if current_port is None:
            return set(), set()
        return (
            _project_ids_for_network_grant(db, network_uuid, port_name),
            _network_port_domain_ids(db, network, current_port),
        )

    granted_projects, domain_ids = _lock_and_recheck(
        db,
        target_lock=lambda: db.query(NetworkPortgroupModel.name).filter(
            NetworkPortgroupModel.network_uuid == network_uuid,
            NetworkPortgroupModel.name == port_name,
        ).with_for_update().scalar() is not None,
        dependency_state=state,
    )
    if granted_projects:
        raise ResourceDeletionConflictError(
            "Projectへgrant中のportgroupはpoolから解除するまで削除できません"
        )
    if domain_ids:
        raise ResourceDeletionConflictError(
            "VM interfaceが参照中のportgroupは削除できません"
        )
    current = db.query(NetworkPortgroupModel).filter(
        NetworkPortgroupModel.network_uuid == network_uuid,
        NetworkPortgroupModel.name == port_name,
    ).one_or_none()
    if current is None:  # pragma: no cover - target lock後の防御
        raise ResourceDeletionNotFoundError("networkまたはportgroupが見つかりません")
    return current
