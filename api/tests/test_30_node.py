from fastapi.testclient import TestClient

from tests.conftest import EnvConfig
from tests.fixtures.node import delete_node, post_node


def test_delete(env, client):
    res_node = delete_node(env=env, client=client)
    
    assert res_node.status_code == 200
    assert res_node.json()["count"] == 0


def test_key_generate(env, client):
    req_data = {
        "generate": True
    }
    res = client.post("/api/nodes/key", json=req_data)
    assert res.status_code == 200


def test_post_nodes_key(env, client):
    req_data = {
        "privateKey": env.key,
        "publicKey": env.pub,
    }
    res = client.post("/api/nodes/key", json=req_data)
    assert res.status_code == 200


def test_post_nodes(env: EnvConfig, client: TestClient):
    post_node(env, client)


# @tester
# def patch_nodes_vxlan():
#     for server in env["servers"]:
#         if "local" not in server:
#             continue
#         req_data = {
#             "nodeName": server["name"],
#             "roleName": "vxlan_overlay",
#             "extraJson": {
#                 "region": "test",
#                 "local_ip": server["local"],
#                 "network_node_ip": server["remote"]
#             }
#         }
#         resp = httpx.patch(url=f'{BASE_URL}/api/tasks/nodes/roles', headers=HEADERS, json=req_data)
#         print_resp(resp=resp)
#         wait_tasks(resp)