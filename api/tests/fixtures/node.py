import pytest
from fastapi.testclient import TestClient

from node.schemas import NodePage
from tests.conftest import EnvConfig, wait_tasks


@pytest.fixture(scope="function")
def nodes(env, client):
    post_node(env, client, skipp=True)

    res = client.get("/api/nodes")
    yield  NodePage.model_validate(res.json())


@pytest.fixture(scope="module")
def installed_sshkeys(env, client):
    req_data = {
        "privateKey": env.key,
        "publicKey": env.pub,
    }
    res = client.post("/api/nodes/key", json=req_data)
    assert res.status_code == 200


def post_node(env: EnvConfig, client: TestClient, skipp=False):
    res_node = client.get("/api/nodes")
    nodes = [ i["name"] for i in res_node.json()["data"] ]
    
    for server in env.servers:
        req_data = {
            "name": server.name,
            "description": "pytest",
            "domain": server.domain,
            "userName": server.username,
            "port": 22,
            "libvirtRole": True
        }
        if skipp and server.name in nodes:
            continue
            
        res = client.post('/api/tasks/nodes', json=req_data)
        assert res.status_code == 200
        
        assert wait_tasks(res, client) == "finish"


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