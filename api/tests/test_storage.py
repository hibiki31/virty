import httpx
import json
from pprint import pprint
import time
import datetime
import sys

from common import BASE_URL, TEST_ENV, HEADERS, print_resp, wait_tasks



def delete_storage():
    req_datas = [
        {
            "name": "test-img",
            "nodeName": "test-node",
        },
        {
            "name": "test-iso",
            "nodeName": "test-node",
        },
        {
            "name": "test-cloud",
            "nodeName": "test-node",
        },
    ]
    for req_data in req_datas:
        api_delete_storage(pool_name=req_data["name"], node_name=req_data["nodeName"])

def api_delete_storage(pool_name, node_name):
    resp = httpx.request(method="get", url=f'{BASE_URL}/api/storages', headers=HEADERS, params={"name": pool_name, "nodeName": node_name})
    print_resp(resp=resp)

    if resp.json() == []:
        return

    pool_uuid = resp.json()[0]["uuid"]

    resp = httpx.request(method="delete",url=f'{BASE_URL}/api/tasks/storages', headers=HEADERS, json={
        "uuid": pool_uuid,
        "node_name": node_name
    })
    print_resp(resp=resp)
    wait_tasks(resp)


def post_storage():
    req_datas = [
        {
            "name": "test-img",
            "nodeName": "test-node",
            "path": "/var/lib/libvirt/test/images"
        },
        {
            "name": "test-iso",
            "nodeName": "test-node",
            "path": "/var/lib/libvirt/test/iso"
        },
        {
            "name": "test-cloud",
            "nodeName": "test-node",
            "path": "/var/lib/libvirt/test/cloud-init"
        },
    ]
    for req_data in req_datas:
        resp = httpx.request(method="post",url=f'{BASE_URL}/api/tasks/storages', headers=HEADERS, json=req_data)
        print_resp(resp=resp)
        wait_tasks(resp)


