import pytest

from mixin.database import SessionLocal
from network.models import NetworkModel, NetworkPoolModel
from project.service import create_project_with_members
from storage.models import (
    AssociationStoragePoolModel,
    StorageModel,
    StoragePoolModel,
)
from tests.external.support.manifest import (
    ManifestEntry,
    mark_current_entry_created,
)


@pytest.fixture(scope="session")
def created_project(env, created_network, created_storage) -> str:
    """外部VM試験用Projectへ、このrunで作成したresourceだけをgrantする。"""

    expected_nodes = {server.name for server in env.servers}
    expected_storage_names = {storage.name for storage in env.storages}
    expected_network_names = {network.name for network in env.networks}
    storage_ids = {
        storage.uuid
        for storage in created_storage.data
        if storage.node_name in expected_nodes
        and storage.name in expected_storage_names
    }
    network_ids = {
        network.uuid
        for network in created_network.data
        if network.node_name in expected_nodes
        and network.name in expected_network_names
    }
    expected_storage_count = len(env.servers) * len(env.storages)
    expected_network_count = len(env.servers) * len(env.networks)
    if len(storage_ids) != expected_storage_count:
        raise AssertionError(
            "Project storage grant precondition failed: "
            f"count={len(storage_ids)} expected={expected_storage_count}"
        )
    if len(network_ids) != expected_network_count:
        raise AssertionError(
            "Project network grant precondition failed: "
            f"count={len(network_ids)} expected={expected_network_count}"
        )

    project_ids: list[str] = []
    with SessionLocal.begin() as db:
        storages = db.query(StorageModel).filter(StorageModel.uuid.in_(storage_ids)).all()
        networks = db.query(NetworkModel).filter(NetworkModel.uuid.in_(network_ids)).all()
        for project_config in env.projects:
            storage_pool = StoragePoolModel(
                name=f"{project_config.name}-storage-grant",
                storages=[
                    AssociationStoragePoolModel(storage=storage)
                    for storage in storages
                ],
            )
            network_pool = NetworkPoolModel(
                name=f"{project_config.name}-network-grant",
                networks=networks,
            )
            db.add_all([storage_pool, network_pool])
            project = create_project_with_members(
                db,
                name=project_config.name,
                member_ids=[env.username],
            )
            project.storage_pools = [storage_pool]
            project.network_pools = [network_pool]
            project_ids.append(project.id)

    for project_config in env.projects:
        mark_current_entry_created(
            env,
            ManifestEntry(kind="project", name=project_config.name),
        )
    if not project_ids:
        raise AssertionError("Project fixtureには1件以上のProjectが必要です")
    return project_ids[0]
