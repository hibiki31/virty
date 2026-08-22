import pytest
from fastapi.testclient import TestClient

from mixin.database import SessionLocal
from node.models import AssociationNodeToRoleModel, NodeModel, NodeRoleModel
from node.schemas import NodePage
from tests.external.conftest import EnvConfig, wait_tasks
from tests.external.support.manifest import ManifestEntry, mark_current_entry_created


@pytest.fixture(scope="session")
def nodes(env, client):
    post_node(env, client)
    response = client.get("/api/nodes")
    response.raise_for_status()
    return NodePage.model_validate(response.json())


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
    
    for server_index, server in enumerate(env.servers):
        req_data = {
            "name": server.name,
            "description": "pytest",
            "domain": server.domain,
            "userName": server.username,
            "port": 22,
            # role taskは固定名のstorage/networkを管理nodeへ作るため実行しない。
            "libvirtRole": False
        }
        if server.name in nodes:
            raise AssertionError(
                "node API collision precondition failed: "
                f"server_index={server_index} count=1"
            )
            
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
        mark_current_entry_created(
            env,
            ManifestEntry(kind="node", name=server.name),
        )


def delete_node_target(
    client: TestClient,
    node_name: str,
    *,
    skip_absent: bool = True,
) -> None:
    response = client.get("/api/nodes")
    response.raise_for_status()
    page = NodePage.model_validate(response.json())
    exact = [node for node in page.data if node.name == node_name]
    if not exact and skip_absent:
        return
    if len(exact) != 1:
        raise RuntimeError(f"node cleanup inventory mismatch: count={len(exact)}")
    task_response = client.delete(f"/api/tasks/nodes/{node_name}")
    task_response.raise_for_status()
    assert wait_tasks(task_response, client) == "finish"
    confirm = client.get("/api/nodes")
    confirm.raise_for_status()
    remaining = [
        node
        for node in NodePage.model_validate(confirm.json()).data
        if node.name == node_name
    ]
    if remaining:
        raise RuntimeError("node cleanup API postcondition failed: count=1")
