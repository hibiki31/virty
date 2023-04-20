import httpx
import json
from pprint import pprint
import time
import datetime
import sys

from common import BASE_URL, TEST_ENV, HEADERS, print_resp, wait_tasks



def delete_nodes():
    node_name = "test-node"
    resp = httpx.request(method="delete",url=f'{BASE_URL}/api/nodes/{node_name}', headers=HEADERS)
    print_resp(resp=resp, allow_not_found=True)


def post_nodes_key():
    req_data = {
        "privateKey": TEST_ENV["key"],
        "publicKey": TEST_ENV["pub"]
    }
    resp = httpx.post(url=f'{BASE_URL}/api/nodes/key', headers=HEADERS, json=req_data)
    print_resp(resp=resp)


def post_nodes():
    req_data = {
        "name": "test-node",
        "description": "string",
        "domain": TEST_ENV["server"],
        "userName": TEST_ENV["server_user"],
        "port": 22,
        "libvirtRole": True
    }
    resp = httpx.post(url=f'{BASE_URL}/api/tasks/nodes', headers=HEADERS, json=req_data)
    print_resp(resp=resp)
    wait_tasks(resp)