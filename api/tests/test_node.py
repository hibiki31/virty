import httpx

from common import BASE_URL, HEADERS, env, print_resp, wait_tasks


def delete_nodes():
    print(f'Start test {len(env["servers"])} servers')
    for server in env["servers"]:
        resp = httpx.request(method="delete",url=f'{BASE_URL}/api/tasks/nodes/{server["name"]}', headers=HEADERS)
        print_resp(resp=resp, allow_not_found=True)
        wait_tasks(resp)

def post_nodes_key():
    req_data = {
        "privateKey": env["key"],
        "publicKey": env["pub"]
    }
    resp = httpx.post(url=f'{BASE_URL}/api/nodes/key', headers=HEADERS, json=req_data)
    print_resp(resp=resp)


def post_nodes():
    for server in env["servers"]:
        req_data = {
            "name": server["name"],
            "description": "string",
            "domain": server["domain"],
            "userName": server["username"],
            "port": 22,
            "libvirtRole": True
        }
        resp = httpx.post(url=f'{BASE_URL}/api/tasks/nodes', headers=HEADERS, json=req_data)
        print_resp(resp=resp)
        wait_tasks(resp)


def patch_nodes_vxlan():
    for server in env["servers"]:
        if not "local" in server:
            continue
        req_data = {
            "nodeName": server["name"],
            "roleName": "vxlan_overlay",
            "extraJson": {
                "region": "test",
                "local_ip": server["local"],
                "network_node_ip": server["remote"]
            }
        }
        resp = httpx.patch(url=f'{BASE_URL}/api/tasks/nodes/roles', headers=HEADERS, json=req_data)
        print_resp(resp=resp)
        wait_tasks(resp)