import pytest
from fastapi.testclient import TestClient

from mixin.database import SessionLocal
from node.models import AssociationNodeToRoleModel, NodeModel, NodeRoleModel
from node.schemas import NodePage
from tests.external.conftest import EnvConfig, wait_tasks


@pytest.fixture(scope="function")
def nodes(env, client):
    post_node(env, client)

    res = client.get("/api/nodes")
    try:
        yield NodePage.model_validate(res.json())
    finally:
        delete_node(env, client)


@pytest.fixture(scope="session", autouse=True)
def installed_sshkeys(env, client):
    req_data = {
        "privateKey": env.key,
        "publicKey": env.pub,
    }
    res = client.post("/api/nodes/key", json=req_data)
    assert res.status_code == 200


def post_node(env: EnvConfig, client: TestClient):
    res_node = client.get("/api/nodes")
    nodes = [ i["name"] for i in res_node.json()["data"] ]
    
    for server in env.servers:
        req_data = {
            "name": server.name,
            "description": "pytest",
            "domain": server.domain,
            "userName": server.username,
            "port": 22,
            # role taskは固定名のstorage/networkを管理nodeへ作るため実行しない。
            "libvirtRole": False
        }
        assert server.name not in nodes, f"既存nodeは再利用できません: {server.name}"
            
        res = client.post('/api/tasks/nodes', json=req_data)
        assert res.status_code == 200
        
        assert wait_tasks(res, client) == "finish"

        # このrun専用DBだけへroleを付与し、resource reloadの対象にする。
        with SessionLocal.begin() as db:
            node = db.query(NodeModel).filter(NodeModel.name == server.name).one()
            role = (
                db.query(NodeRoleModel)
                .filter(NodeRoleModel.name == "libvirt")
                .one_or_none()
            )
            if role is None:
                role = NodeRoleModel(name="libvirt")
                db.add(role)
            association = AssociationNodeToRoleModel(extra_json={})
            association.role = role
            node.roles.append(association)


def delete_node(env, client):
    res_node = client.get("/api/nodes")
    nodes = [ i["name"] for i in res_node.json()["data"] ]

    for server in env.servers:
        if server.name not in nodes:
            continue
        res = client.delete(f'/api/tasks/nodes/{server.name}')
        
        assert wait_tasks(res, client) == "finish"
    
    res_node = client.get("/api/nodes")
    return res_node
