import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# relationship名の解決と全table登録のためimportする。
import models as _all_models  # noqa: F401
from auth.router import CurrentUser
from flavor.models import FlavorModel
from mixin.database import Base
from mixin.exception import ApiError, ApiErrorCode
from network.models import NetworkModel, NetworkPoolModel
from node.models import NodeModel
from project.models import ProjectModel
from resource_authorization import (
    allowed_flavor_ids,
    allowed_network_ids,
    allowed_node_names,
    allowed_storage_ids,
    get_authorized_network,
    get_authorized_storage,
    require_admin,
)
from storage.models import (
    AssociationStoragePoolModel,
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
    storage_a = StorageModel(uuid="storage-a", name="allowed", node_name="node-a")
    storage_b = StorageModel(uuid="storage-b", name="denied", node_name="node-b")
    storage_pool_a = StoragePoolModel(
        name="pool-a",
        storages=[AssociationStoragePoolModel(storage=storage_a)],
    )
    storage_pool_b = StoragePoolModel(
        name="pool-b",
        storages=[AssociationStoragePoolModel(storage=storage_b)],
    )
    network_a = NetworkModel(uuid="network-a", name="allowed", node_name="node-a")
    network_b = NetworkModel(uuid="network-b", name="denied", node_name="node-b")
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
