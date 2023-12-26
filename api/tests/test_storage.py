import httpx

from common import BASE_URL, env, HEADERS, print_resp, wait_tasks, tester


@tester
def delete_storage():
    for server in env["servers"]:
        for storage in env["storages"]:
            api_delete_storage(pool_name=storage["name"], node_name=server["name"])


def api_delete_storage(pool_name, node_name):
    resp = httpx.request(method="get", url=f'{BASE_URL}/api/storages', headers=HEADERS, params={"name": pool_name, "nodeName": node_name})
    print_resp(resp=resp)

    if resp.json()["data"] == []:
        return

    pool_uuid = resp.json()["data"][0]["uuid"]

    resp = httpx.request(method="delete",url=f'{BASE_URL}/api/tasks/storages/{pool_uuid}', headers=HEADERS)
    print_resp(resp=resp)
    wait_tasks(resp)


@tester
def post_storage():
    for server in env["servers"]:
        for storage in env["storages"]:
            req_data = {
                "name": storage["name"],
                "nodeName": server["name"],
                "path": storage["path"]
            }
            resp = httpx.request(method="post",url=f'{BASE_URL}/api/tasks/storages', headers=HEADERS, json=req_data)
            print_resp(resp=resp)
            wait_tasks(resp)


