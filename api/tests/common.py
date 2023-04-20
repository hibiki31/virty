import httpx
import json
from pprint import pprint
import time
import datetime
import sys

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


def wait_tasks(resp):
    for task in resp.json():
        uuid = task["uuid"]
        counter = 0
        while True:
            resp = httpx.request(method="get",url=f'{BASE_URL}/api/tasks/{uuid}', headers=HEADERS).json()
            print(f"wait {uuid} {resp['object']} {counter}s")
            if resp["status"] == "finish":
                print("finish")
                break
            elif resp["status"] == "error":
                print("error")
                break
            time.sleep(5)
            counter += 5


def print_resp(resp: httpx.Response, allow_not_found=False, debug=False):
    if resp.status_code == 200:
        print(f"{Color.BLUE}{resp} {resp.request.method} {resp.url}{Color.END}")
    else:
        print(f"{Color.RED}{resp} {resp.request.method} {resp.url}{Color.END}")

    if debug:
        print("-------------------------------------")
        pprint(resp.json()) 
        print("-------------------------------------")
        print()

    if allow_not_found and resp.status_code == 404:
        print(f"{Color.GREEN} Allow not found{Color.END}")
    elif resp.status_code != 200:
        raise Exception