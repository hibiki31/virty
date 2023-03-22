#!/usr/bin/env python3
import httpx
import json
from pprint import pprint
import time
import datetime
import sys

args = sys.argv


BASE_URL = "http://localhost:8765"


TEST_ENV = json.load(open('./tests/env.json', 'r'))

class Color:
    BLACK     = '\033[30m'
    RED       = '\033[31m'
    GREEN     = '\033[32m'
    YELLOW    = '\033[33m'
    BLUE      = '\033[34m'
    PURPLE    = '\033[35m'
    CYAN      = '\033[36m'
    WHITE     = '\033[37m'
    END       = '\033[0m'
    BOLD      = '\038[1m'
    UNDERLINE = '\033[4m'
    INVISIBLE = '\033[08m'
    REVERCE   = '\033[07m'


if not httpx.get(f'{BASE_URL}/api/version').json()["initialized"]:
    req_data = {
        "username": str(TEST_ENV["username"]),
        "password": str(TEST_ENV["password"])
    }
    print(req_data)
    print(httpx.post(f'{BASE_URL}/api/auth/setup', json=req_data))

req_data = {
    "username": TEST_ENV["username"],
    "password": TEST_ENV["password"]
}


resp = httpx.post(f'{BASE_URL}/api/auth', data=req_data)


ACCESS_TOKEN = resp.json()["access_token"]
HEADERS = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json'    
}


def main():
    print("Setup done")
    api_auth_validate()
    api_users_me()
    # post_nodes_key()
    # delete_nodes()
    # post_nodes()
    # delete_storage()
    # post_storage()
    put_list()




def print_resp(resp: httpx.Response):
    print(resp, resp.request.method, resp.url)
    print(Color.BLUE+"-------------------------------------"+Color.END)
    pprint(resp.json()) 
    print(Color.BLUE+"-------------------------------------"+Color.END)

    if resp.status_code != 200:
        raise Exception

    print()


def put_list():
    resp = httpx.put(f'{BASE_URL}/api/tasks/images',headers=HEADERS)
    print_resp(resp=resp)
    
    resp = httpx.put(f'{BASE_URL}/api/tasks/vms',headers=HEADERS)
    print_resp(resp=resp)

    resp = httpx.put(f'{BASE_URL}/api/tasks/networks',headers=HEADERS)
    print_resp(resp=resp)


def api_auth_validate():
    resp = httpx.get(f'{BASE_URL}/api/auth/validate',headers=HEADERS)
    print_resp(resp=resp)

def api_users_me():
    resp = httpx.get(f'{BASE_URL}/api/users/me',headers=HEADERS)
    print_resp(resp=resp)


def delete_nodes():
    node_name = "test-node"
    resp = httpx.request(method="delete",url=f'{BASE_URL}/api/nodes/{node_name}', headers=HEADERS, json=req_data)
    print_resp(resp=resp)


def delete_nodes():
    node_name = "test-node"
    resp = httpx.request(method="delete",url=f'{BASE_URL}/api/storages', headers=HEADERS, json=req_data)
    print_resp(resp=resp)


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


def wait_tasks(resp):
    for task in resp.json():
        uuid = task["uuid"]
        counter = 0
        while True:
            print(f"wait {uuid} {counter}s")
            resp = httpx.request(method="get",url=f'{BASE_URL}/api/tasks/{uuid}', headers=HEADERS).json()
            if resp["status"] == "finish":
                print("finish")
                break
            elif resp["status"] == "error":
                print("error")
                break
            time.sleep(5)
            counter += 5
            

def print_tasks():
    resp = httpx.request(method="get",url=f'{BASE_URL}/api/tasks', headers=HEADERS).json()
    count = 0
    for task in resp:
        print ("{:<20} {:<4} {:<8} {:<7} {:<9} {:<5} {:<9}".format(
            datetime.datetime.fromisoformat(task["postTime"]).strftime('%Y-%m-%d %H:%M:%S'),
            f'{int(task["runTime"])}s',
            task["status"],
            task["method"],
            task["resource"],
            task["object"],
            task["message"]
        ))
        count += 1
        if count >= 10:
            break

def print_storages():
    resp = httpx.request(method="get",url=f'{BASE_URL}/api/storages', headers=HEADERS).json()
    for task in resp:
        print ("{:<38} {:<15} {:<8} {:<5} {:<5} {:<5} {:<9}".format(
            task["uuid"],
            task["name"],
            task["status"],
            task["capacity"],
            task["available"],
            task["nodeName"],
            task["active"]
        ))

def print_nodes():
    resp = httpx.request(method="get",url=f'{BASE_URL}/api/nodes', headers=HEADERS).json()
    for task in resp:
        print ("{:<15} {:<8} {:<5} {:<5} {:<5} {:<9}".format(
            task["name"],
            task["domain"],
            task["userName"],
            task["core"],
            task["memory"],
            str(task["roles"])
        ))



if __name__ == "__main__":
    if len(args) == 2:
        if args[1] == "show-task":
            print_tasks()
        if args[1] == "show-storage":
            print_storages()
        if args[1] == "show-nodes":
            print_nodes()
    else:
        main()