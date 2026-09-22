import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from domain.models import DomainDriveModel, DomainInterfaceModel, DomainModel
from mixin.database import Base
from network.models import NetworkModel, NetworkPoolModel, NetworkPortgroupModel
from node.models import NodeModel
from project.models import ProjectModel
from resource_deletion import (
    ResourceDeletionConflictError,
    ensure_image_deletable,
    ensure_network_deletable,
    ensure_network_port_deletable,
    ensure_storage_deletable,
)
from storage.models import (
    AssociationStoragePoolModel,
    ImageModel,
    StorageModel,
    StoragePoolModel,
)
from user.models import UserModel


def test_shared_resource_deletion_checks_grants_and_vm_references() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        user = UserModel(username="member", hashed_password="unused")
        node = NodeModel(
            name="node-a",
            description="resource deletion guard test",
            domain="node.invalid",
            user_name="unused",
            port=22,
            core=1,
            memory=1024,
            cpu_gen="test",
            os_like="linux",
            os_name="test",
            os_version="1",
            status=10,
            ansible_facts={},
        )
        storage = StorageModel(
            uuid="storage-a",
            name="storage-a",
            node_name=node.name,
            capacity=1024,
            available=1024,
            path="/shared/storage-a",
            active=True,
            auto_start=True,
            status=2,
            update_token="test",
        )
        storage_pool = StoragePoolModel(
            name="storage-pool-a",
            storages=[AssociationStoragePoolModel(storage=storage)],
        )
        network = NetworkModel(
            uuid="network-a",
            name="network-a-name",
            node_name=node.name,
            bridge="virbr-a",
            type="openvswitch",
            active=True,
            auto_start=True,
            update_token="test",
        )
        port = NetworkPortgroupModel(
            network=network,
            name="tenant-a",
            is_default=False,
            update_token="test",
        )
        network_pool = NetworkPoolModel(name="network-pool-a", ports=[port])
        project = ProjectModel(
            id="aaaaaa",
            name="Project A",
            users=[user],
            storage_pools=[storage_pool],
            network_pools=[network_pool],
        )
        disk = DomainDriveModel(
            target="vda",
            device="disk",
            type="file",
            update_token="test",
        )
        disk.source = "/shared/storage-a/vm-a.qcow2"
        cdrom = DomainDriveModel(
            target="hda",
            device="cdrom",
            type="file",
            update_token="test",
        )
        cdrom.source = "/shared/storage-a/install.iso"
        interface = DomainInterfaceModel(
            mac="52:54:00:00:00:01",
            type="network",
            update_token="test",
        )
        interface.network = network.name
        interface.port = port.name
        domain = DomainModel(
            uuid="vm-a",
            name="vm-a",
            core=1,
            memory=1024,
            status=5,
            update_token="test",
            node_name=node.name,
            drives=[disk, cdrom],
            interfaces=[interface],
        )
        domain.owner_project_id = project.id
        image = ImageModel(
            name="install.iso",
            storage=storage,
            capacity=128,
            allocation=128,
            path="/shared/storage-a/install.iso",
            update_token="test",
        )
        image.domain_uuid = domain.uuid
        db.add_all([node, project, domain, image])
        db.commit()

        with pytest.raises(ResourceDeletionConflictError, match="grant中のstorage"):
            ensure_storage_deletable(db, storage.uuid)
        with pytest.raises(ResourceDeletionConflictError, match="参照中のimage"):
            ensure_image_deletable(db, storage.uuid, image.name)
        with pytest.raises(ResourceDeletionConflictError, match="grant中のnetwork"):
            ensure_network_deletable(db, network.uuid)
        with pytest.raises(ResourceDeletionConflictError, match="grant中のportgroup"):
            ensure_network_port_deletable(db, network.uuid, port.name)

        # grantを明示解除しても、VM参照が残る限りresource本体は削除できない。
        project.storage_pools = []
        project.network_pools = []
        db.flush()
        with pytest.raises(ResourceDeletionConflictError, match="diskまたはCD-ROM"):
            ensure_storage_deletable(db, storage.uuid)
        with pytest.raises(ResourceDeletionConflictError, match="VM interface"):
            ensure_network_deletable(db, network.uuid)
        with pytest.raises(ResourceDeletionConflictError, match="VM interface"):
            ensure_network_port_deletable(db, network.uuid, port.name)

        db.delete(interface)
        db.delete(disk)
        db.delete(cdrom)
        image.domain_uuid = None
        db.flush()

        assert ensure_storage_deletable(db, storage.uuid).uuid == storage.uuid
        assert ensure_image_deletable(db, storage.uuid, image.name) == [image]
        assert ensure_network_deletable(db, network.uuid).uuid == network.uuid
        assert (
            ensure_network_port_deletable(db, network.uuid, port.name).name
            == port.name
        )
