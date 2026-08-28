from datetime import timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from auth.router import create_access_token
from domain.models import DomainDriveModel, DomainInterfaceModel, DomainModel
from mixin.database import SessionLocal
from network.models import NetworkModel
from node.models import NodeModel
from storage.models import ImageModel, StorageModel
from user.models import UserModel, UserScopeModel


pytestmark = [pytest.mark.integration, pytest.mark.timeout(60)]


def test_vm_detail_resolves_network_and_disk_capacity(api_client: TestClient) -> None:
    suffix = uuid4().hex
    node_name = f"vm-detail-node-{suffix}"
    domain_uuid = str(uuid4())
    network_uuid = str(uuid4())
    storage_uuid = str(uuid4())
    image_path = f"/var/lib/libvirt/images/{suffix}.qcow2"
    username = f"vm-detail-user-{suffix}"

    with SessionLocal.begin() as db:
        db.add(UserModel(username=username, hashed_password="unused"))
        db.add(UserScopeModel(user_id=username, name="admin"))
        db.add(NodeModel(
            name=node_name,
            description="VM detail integration test",
            domain="no-network.invalid",
            user_name="fake-user",
            port=22,
            core=4,
            memory=8192,
            cpu_gen="fake-cpu",
            os_like="debian",
            os_name="Fake Linux",
            os_version="1",
            status=10,
            ansible_facts={"virty_backend": "fake"},
        ))
        db.flush()

        network = NetworkModel(
            uuid=network_uuid,
            name=f"vm-detail-network-{suffix}",
            node_name=node_name,
            bridge=f"virbr-{suffix}",
            type="nat",
            active=True,
            auto_start=True,
            update_token=suffix,
        )
        network.dhcp = False
        db.add(network)
        storage = StorageModel(
            uuid=storage_uuid,
            name=f"vm-detail-storage-{suffix}",
            node_name=node_name,
            capacity=128,
            available=88,
            path="/var/lib/libvirt/images",
            active=True,
            auto_start=True,
            status=2,
            update_token=suffix,
        )
        db.add(storage)
        db.flush()

        domain = DomainModel(
            uuid=domain_uuid,
            name=f"vm-detail-{suffix}",
            core=2,
            memory=2048,
            status=5,
            node_name=node_name,
            update_token=suffix,
            storage_used=40,
        )
        domain.vnc_port = "-1"
        domain.owner_user_id = username
        db.add(domain)
        db.flush()

        interface = DomainInterfaceModel(
            domain_uuid=domain_uuid,
            mac="52:54:00:12:34:56",
            type="network",
            update_token=suffix,
        )
        interface.bridge = f"virbr-{suffix}"
        interface.network = None
        db.add(interface)
        drive = DomainDriveModel(
            domain_uuid=domain_uuid,
            target="vda",
            device="disk",
            type="file",
            update_token=suffix,
        )
        drive.source = image_path
        db.add(drive)
        image = ImageModel(
            name=f"{suffix}.qcow2",
            storage_uuid=storage_uuid,
            capacity=40,
            allocation=2,
            path=image_path,
            update_token=suffix,
        )
        image.domain_uuid = domain_uuid
        db.add(image)

    token = create_access_token(
        {"sub": username, "scopes": ["admin"], "projects": []},
        timedelta(minutes=5),
    )
    try:
        response = api_client.get(
            f"/api/vms/{domain_uuid}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        detail = response.json()
        assert detail["interfaces"] == [{
            "type": "network",
            "mac": "52:54:00:12:34:56",
            "target": None,
            "bridge": f"virbr-{suffix}",
            "network": f"vm-detail-network-{suffix}",
            "networkUuid": network_uuid,
            "port": None,
        }]
        assert detail["drives"] == [{
            "device": "disk",
            "type": "file",
            "source": image_path,
            "target": "vda",
            "capacityGb": 40,
        }]
    finally:
        with SessionLocal.begin() as db:
            db.query(DomainInterfaceModel).filter(
                DomainInterfaceModel.domain_uuid == domain_uuid,
            ).delete()
            db.query(DomainDriveModel).filter(
                DomainDriveModel.domain_uuid == domain_uuid,
            ).delete()
            db.query(ImageModel).filter(
                ImageModel.storage_uuid == storage_uuid,
            ).delete()
            db.query(DomainModel).filter(DomainModel.uuid == domain_uuid).delete()
            db.query(StorageModel).filter(StorageModel.uuid == storage_uuid).delete()
            db.query(NetworkModel).filter(NetworkModel.uuid == network_uuid).delete()
            db.query(NodeModel).filter(NodeModel.name == node_name).delete()
            db.query(UserScopeModel).filter(UserScopeModel.user_id == username).delete()
            db.query(UserModel).filter(UserModel.username == username).delete()
