
import pytest

from node.schemas import NodePage


@pytest.fixture(scope="function")
def nodes(env, client, wait_tasks):
    post_node(env, client, wait_tasks)

    res = client.get("/api/nodes")
    yield  NodePage.model_validate(res.json())
    
    delete_node(env, client, wait_tasks)
    


def post_node(env, client, wait_tasks):
    for server in env.servers:
        req_data = {
            "name": server.name,
            "description": "pytest",
            "domain": server.domain,
            "userName": server.username,
            "port": 22,
            "libvirtRole": True
        }
        res = client.post('/api/tasks/nodes', json=req_data)
        assert res.status_code == 200
        
        assert wait_tasks(res, client) == "finish"


def delete_node(env, client, wait_tasks):
    res_node = client.get("/api/nodes")
    nodes = [ i["name"] for i in res_node.json()["data"] ]

    for server in env.servers:
        if server.name not in nodes:
            continue
        res = client.delete(f'/api/tasks/nodes/{server.name}')
        
        assert wait_tasks(res, client) == "finish"
    
    res_node = client.get("/api/nodes")
    return res_node