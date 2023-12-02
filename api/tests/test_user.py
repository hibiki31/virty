import httpx
import json
from pprint import pprint
import time
import datetime
import sys

from common import BASE_URL, env, HEADERS, print_resp, wait_tasks, tester


@tester
def create_user():
    for env_user in env["users"]:
        req_data = {
            "userId": env_user["username"],
            "password": env_user["password"]
        }
        resp = httpx.request(method="post", url=f'{BASE_URL}/api/users', json=req_data, headers=HEADERS)
        print_resp(resp=resp)


@tester
def delete_user():
    for env_user in env["users"]:
        resp = httpx.request(method="delete", url=f'{BASE_URL}/api/users/{env_user["username"]}', headers=HEADERS)
        print_resp(resp=resp)