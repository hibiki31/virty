import httpx

from common import BASE_URL, HEADERS, print_resp, wait_tasks


def post_network():
    request_data = {
        "name": "test-br",
        "nodeName": "test-node",
        "type": "bridge",
        "bridgeDevice": "br-test"
    }
    resp = httpx.request(method="post",url=f'{BASE_URL}/api/tasks/networks', headers=HEADERS, json=request_data)
    print_resp(resp=resp)
    wait_tasks(resp)


def delete_network():
    resp = httpx.request(method="get", url=f'{BASE_URL}/api/networks', params={"admin":True},headers=HEADERS)
    print_resp(resp=resp)

    for net in resp.json():
        if net["name"] == "test-br":
            resp = httpx.request(method="delete",url=f'{BASE_URL}/api/tasks/networks/{net["uuid"]}', headers=HEADERS)
            print_resp(resp=resp)
            wait_tasks(resp)