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