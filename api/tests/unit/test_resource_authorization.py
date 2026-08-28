import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# relationship名の解決と全table登録のためimportする。
import models as _all_models  # noqa: F401
from auth.router import CurrentUser
from domain.models import DomainDriveModel, DomainInterfaceModel, DomainModel
from flavor.models import FlavorModel
from mixin.database import Base
from mixin.exception import ApiError, ApiErrorCode
from network.models import NetworkModel, NetworkPoolModel, NetworkPortgroupModel
from node.models import NodeModel
from project.models import ProjectModel
from resource_authorization import (
    allowed_flavor_ids,
    allowed_image_keys,
    allowed_network_ids,
    allowed_network_port_names,
    allowed_node_names,
    allowed_storage_ids,
    domain_resource_conflicts,
    get_authorized_network,
    get_authorized_storage,
    get_project_network,
    project_allows_image,
    project_allows_network_attachment,
    project_network_ids,
    require_admin,
)
from storage.models import (
    AssociationStoragePoolModel,
    ImageModel,
    StorageModel,
    StoragePoolModel,
)

def _flavor(name: str) -> FlavorModel:
    return FlavorModel(
        name=name,
        os="linux",
        manual_url="https://docs.example.invalid",
        icon="linux",
        cloud_init_ready=False,
        cloud_init_user="cloud-user",
        description=name,
    )


def _seed(db: Session) -> None:
    node_a = NodeModel(name="node-a")
    node_b = NodeModel(name="node-b")
    storage_a = StorageModel(
        uuid="storage-a",
        name="allowed",
        node_name="node-a",
        path="/storage/allowed",
    )
    storage_b = StorageModel(
        uuid="storage-b",
        name="denied",
        node_name="node-b",
        path="/storage/denied",
    )
    storage_pool_a = StoragePoolModel(
        name="pool-a",
        storages=[AssociationStoragePoolModel(storage=storage_a)],
    )
    storage_pool_b = StoragePoolModel(
        name="pool-b",
        storages=[AssociationStoragePoolModel(storage=storage_b)],
    )
    network_a = NetworkModel(
        uuid="network-a",
        name="allowed",
        node_name="node-a",
        bridge="virbr-allowed",
    )
    network_b = NetworkModel(
        uuid="network-b",
        name="denied",
        node_name="node-b",
        bridge="virbr-denied",
    )
    network_pool_a = NetworkPoolModel(name="network-pool-a", networks=[network_a])
    network_pool_b = NetworkPoolModel(name="network-pool-b", networks=[network_b])
    flavor_a = _flavor("flavor-a")
    flavor_b = _flavor("flavor-b")
    db.add_all([
        node_a,
        node_b,
        ProjectModel(
            id="aaaaaa",
            name="allowed",
            storage_pools=[storage_pool_a],
            network_pools=[network_pool_a],
            flavors=[flavor_a],
        ),
        ProjectModel(
            id="bbbbbb",
            name="denied",
            storage_pools=[storage_pool_b],
            network_pools=[network_pool_b],
            flavors=[flavor_b],
        ),
    ])
    db.commit()


def test_project_resource_pools_define_object_access() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        _seed(db)
        user = CurrentUser(
            id="alice",
            token="token",
            scopes=["user"],
            projects=["aaaaaa"],
        )

        assert allowed_storage_ids(db, user) == {"storage-a"}
        assert allowed_network_ids(db, user) == {"network-a"}
        assert allowed_flavor_ids(db, user) == {
            db.query(FlavorModel.id).filter(FlavorModel.name == "flavor-a").scalar()
        }
        assert allowed_node_names(db, user) == {"node-a"}
        assert get_authorized_storage(db, "storage-a", user).name == "allowed"
        assert get_authorized_network(db, "network-a", user).name == "allowed"

        with pytest.raises(ApiError) as storage_error:
            get_authorized_storage(db, "storage-b", user)
        assert storage_error.value.status_code == 404
        assert storage_error.value.code is ApiErrorCode.STORAGE_NOT_FOUND

        with pytest.raises(ApiError) as network_error:
            get_authorized_network(db, "network-b", user)
        assert network_error.value.status_code == 404
        assert network_error.value.code is ApiErrorCode.NETWORK_NOT_FOUND


def test_global_operation_requires_current_admin_grant() -> None:
    user = CurrentUser(id="alice", token="token", scopes=["node.manage"])
    with pytest.raises(ApiError) as error:
        require_admin(user)
    assert error.value.status_code == 403

    require_admin(CurrentUser(id="root", token="token", scopes=["admin"]))


def test_project_image_requires_same_project_flavor_or_no_flavor() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        _seed(db)
        storage = db.get(StorageModel, "storage-a")
        allowed_flavor = db.query(FlavorModel).filter_by(name="flavor-a").one()
        denied_flavor = db.query(FlavorModel).filter_by(name="flavor-b").one()
        assert storage is not None

        generic = ImageModel(
            name="generic.qcow2",
            storage=storage,
            path="/storage/allowed/generic.qcow2",
        )
        generic.flavor_id = None
        matching = ImageModel(
            name="matching.qcow2",
            storage=storage,
            path="/storage/allowed/matching.qcow2",
            flavor=allowed_flavor,
        )
        cross_project = ImageModel(
            name="cross.qcow2",
            storage=storage,
            path="/storage/allowed/cross.qcow2",
            flavor=denied_flavor,
        )
        db.add_all([generic, matching, cross_project])
        db.flush()

        assert project_allows_image(db, "aaaaaa", generic)
        assert project_allows_image(db, "aaaaaa", matching)
        assert not project_allows_image(db, "aaaaaa", cross_project)

        user = CurrentUser(
            id="alice",
            token="token",
            scopes=["image.read"],
            projects=["aaaaaa", "bbbbbb"],
        )
        assert allowed_image_keys(db, user) == {
            (generic.storage_uuid, generic.path),
            (matching.storage_uuid, matching.path),
        }
        assert allowed_image_keys(db, user, "aaaaaa") == {
            (generic.storage_uuid, generic.path),
            (matching.storage_uuid, matching.path),
        }


def test_explicit_project_filter_does_not_use_membership_union() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        _seed(db)
        user = CurrentUser(
            id="alice",
            token="token",
            scopes=["user"],
            projects=["aaaaaa", "bbbbbb"],
        )

        assert allowed_storage_ids(db, user, "aaaaaa") == {"storage-a"}
        assert allowed_network_ids(db, user, "aaaaaa") == {"network-a"}
        assert allowed_node_names(db, user, "aaaaaa") == {"node-a"}

        admin = CurrentUser(id="root", token="token", scopes=["admin"])
        with pytest.raises(ApiError) as error:
            allowed_storage_ids(db, admin, "bbbbbb")
        assert error.value.status_code == 404
        assert error.value.code is ApiErrorCode.PROJECT_NOT_FOUND

        admin.projects = ["bbbbbb"]
        assert allowed_storage_ids(db, admin, "bbbbbb") == {"storage-b"}


def test_domain_resource_conflicts_are_project_exact_and_fail_closed() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        _seed(db)
        drive = DomainDriveModel(
            target="vda",
            device="disk",
            type="file",
            update_token="test",
        )
        drive.source = "/storage/allowed/vm-a.qcow2"
        interface = DomainInterfaceModel(
            mac="52:54:00:00:00:01",
            type="network",
            update_token="test",
        )
        interface.network = "allowed"
        domain = DomainModel(
            uuid="vm-a",
            name="vm-a",
            node_name="node-a",
            drives=[drive],
            interfaces=[interface],
        )

        assert domain_resource_conflicts(
            db,
            domain,
            storage_ids={"storage-a"},
            network_ids={"network-a"},
        ) == []
        assert domain_resource_conflicts(
            db,
            domain,
            storage_ids={"storage-b"},
            network_ids={"network-b"},
        ) == [
            "storage:/storage/allowed/vm-a.qcow2",
            "network:allowed",
        ]


def test_registered_cdrom_is_checked_and_nullable_storage_path_is_safe() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        _seed(db)
        storage = StorageModel(
            uuid="storage-null-path",
            name="nullable-path",
            node_name="node-a",
        )
        # 旧inventoryにはNULL pathがあり得るため、型上の現行契約を越えて再現する。
        setattr(storage, "path", None)
        registered_iso = ImageModel(
            name="install.iso",
            storage=storage,
            path="/inventory/install.iso",
        )
        db.add_all([storage, registered_iso])
        db.flush()

        registered = DomainDriveModel(
            target="hda",
            device="cdrom",
            type="file",
            update_token="test",
        )
        registered.source = registered_iso.path
        cloud_init = DomainDriveModel(
            target="hdb",
            device="cdrom",
            type="file",
            update_token="test",
        )
        cloud_init.source = "/run/virty/cloud-init.iso"
        domain = DomainModel(
            uuid="vm-cdrom",
            name="vm-cdrom",
            node_name="node-a",
            drives=[registered, cloud_init],
        )

        assert domain_resource_conflicts(
            db,
            domain,
            storage_ids=set(),
            network_ids=set(),
        ) == ["storage:/inventory/install.iso"]
        assert domain_resource_conflicts(
            db,
            domain,
            storage_ids={storage.uuid},
            network_ids=set(),
        ) == []


def test_portgroup_grant_does_not_grant_the_whole_network() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        node = NodeModel(name="node-port")
        network = NetworkModel(
            uuid="network-port",
            name="port-only",
            node_name=node.name,
            bridge="virbr-port",
        )
        granted_port = NetworkPortgroupModel(
            network=network,
            name="tenant-a",
            is_default=False,
            update_token="test",
        )
        denied_port = NetworkPortgroupModel(
            network=network,
            name="tenant-b",
            is_default=False,
            update_token="test",
        )
        project = ProjectModel(
            id="cccccc",
            name="port-only",
            network_pools=[NetworkPoolModel(
                name="port-pool",
                ports=[granted_port],
            )],
        )
        db.add_all([node, project, denied_port])
        db.commit()
        user = CurrentUser(
            id="alice",
            token="token",
            scopes=["user"],
            projects=[project.id],
        )

        assert project_network_ids(db, project.id) == {network.uuid}
        assert allowed_network_port_names(
            db,
            user,
            network.uuid,
        ) == {granted_port.name}
        assert allowed_network_port_names(
            db,
            user,
            network.uuid,
            project.id,
        ) == {granted_port.name}

        admin_without_membership = CurrentUser(
            id="root",
            token="token",
            scopes=["admin"],
            projects=[],
        )
        assert allowed_network_ids(db, admin_without_membership) == set()
        with pytest.raises(ApiError) as filtered_error:
            allowed_network_ids(
                db,
                admin_without_membership,
                project.id,
            )
        assert filtered_error.value.status_code == 404
        assert filtered_error.value.code is ApiErrorCode.PROJECT_NOT_FOUND
        assert project_allows_network_attachment(
            db,
            project.id,
            network.uuid,
            granted_port.name,
        )
        assert not project_allows_network_attachment(
            db,
            project.id,
            network.uuid,
            None,
        )
        assert not project_allows_network_attachment(
            db,
            project.id,
            network.uuid,
            "tenant-b",
        )
        assert get_project_network(
            db,
            project.id,
            network.uuid,
            user,
            granted_port.name,
        ) is network
        with pytest.raises(ApiError) as error:
            get_project_network(db, project.id, network.uuid, user, "tenant-b")
        assert error.value.status_code == 404
        assert error.value.code is ApiErrorCode.NETWORK_NOT_FOUND

        interface = DomainInterfaceModel(
            mac="52:54:00:00:00:02",
            type="network",
            update_token="test",
        )
        interface.network = network.name
        interface.port = granted_port.name
        domain = DomainModel(
            uuid="vm-port",
            name="vm-port",
            node_name=node.name,
            interfaces=[interface],
        )
        assert domain_resource_conflicts(
            db,
            domain,
            storage_ids=set(),
            network_ids=set(),
            network_ports={(network.uuid, granted_port.name)},
        ) == []
        interface.port = "tenant-b"
        assert domain_resource_conflicts(
            db,
            domain,
            storage_ids=set(),
            network_ids=set(),
            network_ports={(network.uuid, granted_port.name)},
        ) == ["network:port-only"]
