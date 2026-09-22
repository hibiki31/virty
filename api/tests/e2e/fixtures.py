"""実機情報を含まない決定的なE2E fixture。"""

from typing import Any

from sqlalchemy.orm import Session

from auth.function import get_password_hash
from domain.models import DomainModel
from flavor.models import FlavorModel
from module.xmllib import XmlEditor
from network.models import NetworkModel, NetworkPoolModel
from node.models import AssociationNodeToRoleModel, NodeModel, NodeRoleModel
from project.models import ProjectModel
from storage.models import AssociationStoragePoolModel, ImageModel, StorageModel, StoragePoolModel
from tests.e2e.backends import inventory_domain_xml
from tests.e2e.state import empty_state
from user.models import UserModel, UserScopeModel


PASSWORD = "E2e-password-123!"
MANIFEST: dict[str, Any] = {
    "users": {role: {"username": f"e2e-{role}", "password": PASSWORD} for role in ("admin", "member", "outsider")},
    "projects": {"alpha": {"id": "aa0001", "name": "E2E Alpha"}, "beta": {"id": "bb0002", "name": "E2E Beta"}},
    "resources": {
        "nodeName": "e2e-node", "storageUuid": "11111111-1111-4111-8111-111111111111",
        "networkUuid": "22222222-2222-4222-8222-222222222222", "flavorId": 1,
        "storagePoolId": 1, "networkPoolId": 1, "imageName": "e2e-template.qcow2",
        "imagePath": "/e2e/images/e2e-template.qcow2", "storageName": "E2E Storage",
        "networkName": "E2E Network", "storagePoolName": "E2E Storage Pool",
        "networkPoolName": "E2E Network Pool", "flavorName": "E2E Linux",
    },
    "vms": {
        "alpha": {"uuid": "33333333-3333-4333-8333-333333333333", "name": "e2e-alpha-vm"},
        "beta": {"uuid": "44444444-4444-4444-8444-444444444444", "name": "e2e-beta-vm"},
    },
}


def seed_database(db: Session) -> dict[str, Any]:
    """DBの所有者・grantとfake inventoryを一致させる。"""

    state = empty_state()
    resources = MANIFEST["resources"]
    password_hash = get_password_hash(PASSWORD)
    users: dict[str, UserModel] = {}
    for role, values in MANIFEST["users"].items():
        user = UserModel(username=values["username"], hashed_password=password_hash)
        user.session_generation = f"e2e-{role}"
        scopes = ["admin"] if role == "admin" else ["user", "vm.create", "vm.delete", "vm.attach"]
        user.scopes = [UserScopeModel(name=scope) for scope in scopes]
        db.add(user)
        users[role] = user

    node = NodeModel(name=resources["nodeName"], description="E2E専用fixture", domain="e2e-node.invalid", user_name="e2e", port=22,
                     core=16, memory=32768, cpu_gen="E2E CPU", os_like="debian", os_name="E2E Linux", os_version="1", status=10, ansible_facts={})
    db.add(node)
    db.add(NodeRoleModel(name="libvirt"))
    db.flush()
    db.add(AssociationNodeToRoleModel(node_name=node.name, role_name="libvirt", extra_json={}))

    flavor = FlavorModel(name=resources["flavorName"], os="linux", description="E2E用template", icon="linux", manual_url="https://example.invalid/manual", cloud_init_ready=False, cloud_init_user="e2e")
    db.add(flavor)
    storage = StorageModel(uuid=resources["storageUuid"], name=resources["storageName"], node_name=node.name,
                           capacity=256, available=240, path="/e2e/images", active=True, auto_start=True, status=2, update_token="e2e-seed")
    network = NetworkModel(uuid=resources["networkUuid"], name=resources["networkName"], node_name=node.name,
                           type="bridge", bridge="e2e-br0", active=True, auto_start=True, update_token="e2e-seed")
    network.dhcp = False
    db.add_all([storage, network])
    db.flush()
    image = ImageModel(name=resources["imageName"], storage_uuid=storage.uuid, path=resources["imagePath"], capacity=4, allocation=1, flavor=flavor, update_token="e2e-seed")
    db.add(image)
    storage_pool = StoragePoolModel(name=resources["storagePoolName"], storages=[AssociationStoragePoolModel(storage_uuid=storage.uuid)])
    network_pool = NetworkPoolModel(name=resources["networkPoolName"], networks=[network])
    db.add_all([storage_pool, network_pool])
    db.flush()
    if (flavor.id, storage_pool.id, network_pool.id) != (1, 1, 1):
        raise RuntimeError("E2E fixtureのsequenceが初期化されていません")

    for label, project in MANIFEST["projects"].items():
        db.add(ProjectModel(**project, users=[users["admin"], users["member" if label == "alpha" else "outsider"]],
                            storage_pools=[storage_pool] if label == "alpha" else [], network_pools=[network_pool] if label == "alpha" else [],
                            flavors=[flavor] if label == "alpha" else []))
    db.flush()

    for label, vm in MANIFEST["vms"].items():
        domain = DomainModel(**vm, node_name=node.name, core=1, memory=1024, status=5,
                             storage_used=0, update_token="e2e-seed")
        domain.owner_project_id = MANIFEST["projects"][label]["id"]
        domain.vnc_port = "0"
        db.add(domain)
        editor = XmlEditor("static", "domain_base")
        editor.domain_uuid_generate(domain_uuid=vm["uuid"])
        editor.domain_base_edit(domain_name=vm["name"], memory_mega_byte=1024, core=1, vnc_port=0)
        state["domains"][vm["uuid"]] = {"node_name": node.name, "xml": inventory_domain_xml(editor.dump_str()), "status": 5, "auto": False}

    state["storages"][storage.uuid] = {
        "uuid": storage.uuid, "name": storage.name, "node_name": node.name, "domain": node.domain,
        "path": storage.path, "capacity": 256, "available": 240, "allocation": 16,
        "active": True, "auto_start": True, "status": 2,
        "images": [{"name": image.name, "path": image.path, "capacity": 4, "allocation": 1}],
    }
    state["networks"][network.uuid] = {"uuid": network.uuid, "name": network.name, "node_name": node.name, "type": "bridge", "bridge": "e2e-br0", "active": True, "auto_start": True, "dhcp": False, "portgroups": []}
    return state
