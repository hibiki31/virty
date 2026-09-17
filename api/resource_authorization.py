"""既存REST API向けのproject/object-level認可。

projectが参照するresource poolを正本とし、clientが送るnode名やproject IDだけを
認可根拠にしない。対応先を安全に導出できないglobal操作はrouter側でadmin限定にする。
"""

from sqlalchemy import or_
from sqlalchemy.orm import Session

from auth.router import CurrentUser
from domain.models import DomainModel
from flavor.models import FlavorModel
from mixin.exception import ApiError, ApiErrorCode
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
    ImageModel,
    StorageModel,
    StoragePoolModel,
)


def require_admin(current_user: CurrentUser) -> None:
    current_user.verify_scope(["admin"])


def is_global_inventory(
    current_user: CurrentUser,
    *,
    admin: bool,
    project_id: str | None = None,
) -> bool:
    """明示的な管理readを認可し、Project指定時は通常の境界を維持する。"""
    if admin:
        require_admin(current_user)
    return admin and project_id is None


def _not_found(code: ApiErrorCode) -> ApiError:
    return ApiError(
        404,
        code,
        "The requested resource was not found.",
    )


def project_storage_pool_ids(db: Session, project_id: str) -> set[int]:
    """指定projectへgrantされたstorage pool IDだけを返す。"""
    return {
        int(value)
        for (value,) in db.query(
            association_projects_to_storages_pools.c.storages_pools_id,
        ).filter(
            association_projects_to_storages_pools.c.projects_id == project_id,
        ).all()
    }


def project_storage_ids(db: Session, project_id: str) -> set[str]:
    """指定projectのstorage poolから利用可能なstorageを導出する。"""
    pool_ids = project_storage_pool_ids(db, project_id)
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


def project_network_pool_ids(db: Session, project_id: str) -> set[int]:
    """指定projectへgrantされたnetwork pool IDだけを返す。"""
    return {
        int(value)
        for (value,) in db.query(
            association_projects_to_networks_pools.c.networks_pools_id,
        ).filter(
            association_projects_to_networks_pools.c.projects_id == project_id,
        ).all()
    }


def network_grants_for_pool_ids(
    db: Session,
    pool_ids: set[int],
) -> tuple[set[str], set[tuple[str, str]]]:
    """network pool集合をnetwork全体grantと個別portgroup grantへ分ける。"""
    if not pool_ids:
        return set(), set()
    direct_network_ids = {
        str(network_uuid)
        for (network_uuid,) in db.query(
            associations_networks.c.network_uuid,
        ).filter(
            associations_networks.c.pool_id.in_(pool_ids),
        ).all()
    }
    network_ports = {
        (str(network_uuid), str(port_name))
        for network_uuid, port_name in db.query(
            associations_networks_pools.c.port_network_uuid,
            associations_networks_pools.c.port_name,
        ).filter(
            associations_networks_pools.c.pool_id.in_(pool_ids),
            associations_networks_pools.c.port_name.is_not(None),
        ).all()
    }
    return direct_network_ids, network_ports


def project_direct_network_ids(db: Session, project_id: str) -> set[str]:
    """指定projectへnetwork全体としてgrantされたIDを返す。"""
    direct_network_ids, _ = network_grants_for_pool_ids(
        db,
        project_network_pool_ids(db, project_id),
    )
    return direct_network_ids


def project_network_ports(db: Session, project_id: str) -> set[tuple[str, str]]:
    """指定projectへ個別grantされた(network ID, portgroup名)を返す。"""
    _, network_ports = network_grants_for_pool_ids(
        db,
        project_network_pool_ids(db, project_id),
    )
    return network_ports


def project_network_ids(db: Session, project_id: str) -> set[str]:
    """一覧表示可能なnetworkをnetwork/portgroup grant双方から導出する。"""
    direct_network_ids, network_ports = network_grants_for_pool_ids(
        db,
        project_network_pool_ids(db, project_id),
    )
    return direct_network_ids | {network_id for network_id, _ in network_ports}


def project_allows_network_attachment(
    db: Session,
    project_id: str,
    network_id: str,
    port_name: str | None,
) -> bool:
    """VMのnetwork/portgroup指定がProject grant内かを判定する。"""
    if network_id in project_direct_network_ids(db, project_id):
        return True
    return (
        port_name is not None
        and (network_id, port_name) in project_network_ports(db, project_id)
    )


def project_flavor_ids(db: Session, project_id: str) -> set[int]:
    """指定projectへgrantされたflavor IDだけを返す。"""
    return {
        int(value)
        for (value,) in db.query(
            association_projects_to_flavors_pools.c.flavors_id,
        ).filter(
            association_projects_to_flavors_pools.c.projects_id == project_id,
        ).all()
    }


def project_allows_image(
    db: Session,
    project_id: str,
    image: ImageModel,
) -> bool:
    """imageのstorageと任意のflavorが同じProject grant内か判定する。

    flavor未設定のimageはOS flavorに依存しない汎用imageとして扱う。
    """
    storage_uuid = image.storage_uuid
    if storage_uuid is None and image.storage is not None:
        storage_uuid = image.storage.uuid
    return (
        storage_uuid in project_storage_ids(db, project_id)
        and (
            image.flavor_id is None
            or image.flavor_id in project_flavor_ids(db, project_id)
        )
    )


def allowed_image_keys(
    db: Session,
    current_user: CurrentUser,
    project_id: str | None = None,
) -> set[tuple[str, str]]:
    """storageとflavorを同じProjectで満たすimage keyだけを返す。

    Project filter未指定時も各所属Projectで個別に照合してから和集合にするため、
    Project AのstorageとProject Bのflavorを組み合わせたimageは許可しない。
    """
    if project_id is not None:
        get_member_project(db, project_id, current_user)
        project_ids = [project_id]
    else:
        project_ids = list(dict.fromkeys(current_user.projects))
    grants = [
        (
            project_storage_ids(db, candidate_id),
            project_flavor_ids(db, candidate_id),
        )
        for candidate_id in project_ids
    ]
    storage_ids: set[str] = set()
    for project_storages, _ in grants:
        storage_ids.update(project_storages)
    if not storage_ids:
        return set()
    images = db.query(
        ImageModel.storage_uuid,
        ImageModel.path,
        ImageModel.flavor_id,
    ).filter(ImageModel.storage_uuid.in_(storage_ids)).all()
    return {
        (str(storage_uuid), str(path))
        for storage_uuid, path, flavor_id in images
        if any(
            storage_uuid in project_storages
            and (flavor_id is None or flavor_id in project_flavors)
            for project_storages, project_flavors in grants
        )
    }


def project_node_names(db: Session, project_id: str) -> set[str]:
    """grant済みstorage/networkから指定projectが利用できるnodeを導出する。"""
    storage_ids = project_storage_ids(db, project_id)
    network_ids = project_network_ids(db, project_id)
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
    return storage_nodes | network_nodes


def allowed_storage_pool_ids(
    db: Session,
    current_user: CurrentUser,
    project_id: str | None = None,
) -> set[int]:
    if project_id is not None:
        get_member_project(db, project_id, current_user)
        return project_storage_pool_ids(db, project_id)
    result: set[int] = set()
    for user_project_id in current_user.projects:
        result.update(project_storage_pool_ids(db, user_project_id))
    return result


def allowed_storage_ids(
    db: Session,
    current_user: CurrentUser,
    project_id: str | None = None,
) -> set[str]:
    if project_id is not None:
        get_member_project(db, project_id, current_user)
        return project_storage_ids(db, project_id)
    pool_ids = allowed_storage_pool_ids(db, current_user)
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
    project_id: str | None = None,
) -> set[int]:
    if project_id is not None:
        get_member_project(db, project_id, current_user)
        return project_network_pool_ids(db, project_id)
    result: set[int] = set()
    for user_project_id in current_user.projects:
        result.update(project_network_pool_ids(db, user_project_id))
    return result


def allowed_network_grants(
    db: Session,
    current_user: CurrentUser,
    project_id: str | None = None,
) -> tuple[set[str], set[tuple[str, str]]]:
    """閲覧可能なnetwork全体grantと個別portgroup grantを返す。

    global adminもJWTに含まれるProject membershipを越えて閲覧できない。
    Project filter指定時は対象Projectだけへ絞り込む。
    """
    if project_id is not None:
        get_member_project(db, project_id, current_user)
        return network_grants_for_pool_ids(
            db,
            project_network_pool_ids(db, project_id),
        )

    direct_network_ids: set[str] = set()
    network_ports: set[tuple[str, str]] = set()
    for user_project_id in current_user.projects:
        project_networks, project_ports = network_grants_for_pool_ids(
            db,
            project_network_pool_ids(db, user_project_id),
        )
        direct_network_ids.update(project_networks)
        network_ports.update(project_ports)
    return direct_network_ids, network_ports


def allowed_network_port_names(
    db: Session,
    current_user: CurrentUser,
    network_id: str,
    project_id: str | None = None,
) -> set[str] | None:
    """network詳細で閲覧可能なportgroup名を返す。

    ``None`` はnetwork全体grantがあり全portgroupを閲覧可能であることを表す。
    """
    grants = allowed_network_grants(db, current_user, project_id)
    direct_network_ids, network_ports = grants
    if network_id in direct_network_ids:
        return None
    return {
        port_name
        for granted_network_id, port_name in network_ports
        if granted_network_id == network_id
    }


def allowed_network_ids(
    db: Session,
    current_user: CurrentUser,
    project_id: str | None = None,
) -> set[str]:
    grants = allowed_network_grants(db, current_user, project_id)
    direct_network_ids, network_ports = grants
    return direct_network_ids | {
        network_id for network_id, _ in network_ports
    }


def allowed_flavor_ids(
    db: Session,
    current_user: CurrentUser,
    project_id: str | None = None,
) -> set[int]:
    if project_id is not None:
        get_member_project(db, project_id, current_user)
        return project_flavor_ids(db, project_id)
    result: set[int] = set()
    for user_project_id in current_user.projects:
        result.update(project_flavor_ids(db, user_project_id))
    return result


def allowed_node_names(
    db: Session,
    current_user: CurrentUser,
    project_id: str | None = None,
) -> set[str]:
    if project_id is not None:
        get_member_project(db, project_id, current_user)
        return project_node_names(db, project_id)

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
    *,
    admin: bool = False,
) -> StorageModel:
    global_inventory = is_global_inventory(current_user, admin=admin)
    row = db.get(StorageModel, storage_id)
    allowed = None if global_inventory else allowed_storage_ids(db, current_user)
    if row is None or (allowed is not None and row.uuid not in allowed):
        raise _not_found(ApiErrorCode.STORAGE_NOT_FOUND)
    return row


def get_authorized_storage_pool(
    db: Session,
    pool_id: int,
    current_user: CurrentUser,
) -> StoragePoolModel:
    row = db.get(StoragePoolModel, pool_id)
    allowed = allowed_storage_pool_ids(db, current_user)
    if row is None or (allowed is not None and row.id not in allowed):
        raise _not_found(ApiErrorCode.STORAGE_POOL_NOT_FOUND)
    return row


def get_authorized_network(
    db: Session,
    network_id: str,
    current_user: CurrentUser,
    project_id: str | None = None,
    *,
    admin: bool = False,
) -> NetworkModel:
    global_inventory = is_global_inventory(current_user, admin=admin, project_id=project_id)
    row = db.get(NetworkModel, network_id)
    allowed = None if global_inventory else allowed_network_ids(db, current_user, project_id)
    if row is None or (allowed is not None and row.uuid not in allowed):
        raise _not_found(ApiErrorCode.NETWORK_NOT_FOUND)
    return row


def get_authorized_network_pool(
    db: Session,
    pool_id: int,
    current_user: CurrentUser,
) -> NetworkPoolModel:
    row = db.get(NetworkPoolModel, pool_id)
    allowed = allowed_network_pool_ids(db, current_user)
    if row is None or (allowed is not None and row.id not in allowed):
        raise _not_found(ApiErrorCode.NETWORK_POOL_NOT_FOUND)
    return row


def get_authorized_flavor(
    db: Session,
    flavor_id: int,
    current_user: CurrentUser,
) -> FlavorModel:
    row = db.get(FlavorModel, flavor_id)
    allowed = allowed_flavor_ids(db, current_user)
    if row is None or (allowed is not None and row.id not in allowed):
        raise _not_found(ApiErrorCode.FLAVOR_NOT_FOUND)
    return row


def get_authorized_project(
    db: Session,
    project_id: str,
    current_user: CurrentUser,
) -> ProjectModel:
    return get_member_project(db, project_id, current_user)


def get_member_project(
    db: Session,
    project_id: str,
    current_user: CurrentUser,
) -> ProjectModel:
    """admin bypassなしでJWTに残るProject membershipを要求する。"""
    row = db.get(ProjectModel, project_id)
    if row is None or project_id not in current_user.projects:
        raise _not_found(ApiErrorCode.PROJECT_NOT_FOUND)
    return row


def get_project_storage(
    db: Session,
    project_id: str,
    storage_id: str,
    current_user: CurrentUser,
) -> StorageModel:
    """利用者と指定projectの双方から許可されたstorageを返す。"""
    get_member_project(db, project_id, current_user)
    row = db.get(StorageModel, storage_id)
    if row is None or storage_id not in project_storage_ids(db, project_id):
        raise _not_found(ApiErrorCode.STORAGE_NOT_FOUND)
    return row


def get_project_network(
    db: Session,
    project_id: str,
    network_id: str,
    current_user: CurrentUser,
    port_name: str | None = None,
) -> NetworkModel:
    """利用者と指定projectの双方から許可されたnetwork/portを返す。"""
    get_member_project(db, project_id, current_user)
    row = db.get(NetworkModel, network_id)
    if row is None or not project_allows_network_attachment(
        db,
        project_id,
        network_id,
        port_name,
    ):
        raise _not_found(ApiErrorCode.NETWORK_NOT_FOUND)
    return row


def domain_resource_conflicts(
    db: Session,
    domain: DomainModel,
    *,
    storage_ids: set[str],
    network_ids: set[str],
    network_ports: set[tuple[str, str]] | None = None,
) -> list[str]:
    """VMが指定resource集合の外へ依存している箇所を列挙する。"""
    conflicts: list[str] = []

    storages = db.query(StorageModel).filter(
        StorageModel.node_name == domain.node_name,
    ).all()
    for drive in domain.drives:
        if drive.source is None or drive.device not in {"disk", "cdrom"}:
            continue
        registered_image = (
            db.query(ImageModel)
            .join(StorageModel, ImageModel.storage_uuid == StorageModel.uuid)
            .filter(
                ImageModel.path == drive.source,
                StorageModel.node_name == domain.node_name,
            )
            .order_by(ImageModel.storage_uuid)
            .first()
        )
        # cloud-init等の一時ISOはinventoryへ登録されないため、Project grantの
        # storage依存として扱わない。登録済みISO/CD-ROMだけを検査する。
        if drive.device == "cdrom":
            if registered_image is None:
                continue
            matching_storage_id = registered_image.storage_uuid
            if matching_storage_id not in storage_ids:
                conflicts.append(f"storage:{drive.source}")
            continue
        matching_storage = next(
            (
                storage
                for storage in sorted(
                    (item for item in storages if item.path),
                    key=lambda item: len(item.path or ""),
                    reverse=True,
                )
                if storage.path is not None
                and (
                    drive.source == storage.path
                    or drive.source.startswith(f"{storage.path.rstrip('/')}/")
                )
            ),
            None,
        )
        if matching_storage is None:
            matching_storage_id = (
                registered_image.storage_uuid
                if registered_image is not None
                else None
            )
        else:
            matching_storage_id = matching_storage.uuid
        if matching_storage_id is None or matching_storage_id not in storage_ids:
            conflicts.append(f"storage:{drive.source}")

    networks = db.query(NetworkModel).filter(
        NetworkModel.node_name == domain.node_name,
    ).all()
    for interface in domain.interfaces:
        matching_network = next(
            (
                network
                for network in networks
                if (interface.network and network.name == interface.network)
                or (interface.bridge and network.bridge == interface.bridge)
            ),
            None,
        )
        network_allowed = (
            matching_network is not None
            and (
                matching_network.uuid in network_ids
                or (
                    interface.port is not None
                    and network_ports is not None
                    and (matching_network.uuid, interface.port) in network_ports
                )
            )
        )
        if not network_allowed:
            identity = interface.network or interface.bridge or interface.mac
            conflicts.append(f"network:{identity}")

    return conflicts


def domain_project_resource_conflicts(
    db: Session,
    domain: DomainModel,
    project_id: str,
) -> list[str]:
    """VMをprojectへ所属させる際にgrant外となるresourceを列挙する。"""
    direct_network_ids, network_ports = network_grants_for_pool_ids(
        db,
        project_network_pool_ids(db, project_id),
    )
    conflicts = domain_resource_conflicts(
        db,
        domain,
        storage_ids=project_storage_ids(db, project_id),
        network_ids=direct_network_ids,
        network_ports=network_ports,
    )

    drive_sources = {
        drive.source
        for drive in domain.drives
        if drive.source is not None and drive.device in {"disk", "cdrom"}
    }
    image_query = db.query(ImageModel).join(
        StorageModel,
        ImageModel.storage_uuid == StorageModel.uuid,
    ).filter(StorageModel.node_name == domain.node_name)
    if drive_sources:
        image_query = image_query.filter(or_(
            ImageModel.domain_uuid == domain.uuid,
            ImageModel.path.in_(drive_sources),
        ))
    else:
        image_query = image_query.filter(ImageModel.domain_uuid == domain.uuid)

    storage_ids = project_storage_ids(db, project_id)
    flavor_ids = project_flavor_ids(db, project_id)
    for image in image_query.order_by(ImageModel.storage_uuid, ImageModel.path):
        storage_conflict = f"storage:{image.path}"
        if image.storage_uuid not in storage_ids and storage_conflict not in conflicts:
            conflicts.append(storage_conflict)
        if image.flavor_id is not None and image.flavor_id not in flavor_ids:
            flavor_conflict = f"flavor:{image.flavor_id}"
            if flavor_conflict not in conflicts:
                conflicts.append(flavor_conflict)
    return conflicts
