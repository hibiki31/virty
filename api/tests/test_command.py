#!/usr/bin/env python3
import httpx
import datetime
import sys
from tabulate import tabulate

from common import BASE_URL, HEADERS, print_resp, wait_tasks, Color


args = sys.argv


def put_list():
    resp = httpx.put(f'{BASE_URL}/api/tasks/images',headers=HEADERS)
    print_resp(resp=resp)
    wait_tasks(resp)
    
    resp = httpx.put(f'{BASE_URL}/api/tasks/vms',headers=HEADERS)
    print_resp(resp=resp)
    wait_tasks(resp)

    resp = httpx.put(f'{BASE_URL}/api/tasks/networks',headers=HEADERS)
    print_resp(resp=resp)
    wait_tasks(resp)


def api_auth_validate():
    resp = httpx.get(f'{BASE_URL}/api/auth/validate',headers=HEADERS)
    print_resp(resp=resp)


def api_users_me():
    resp = httpx.get(f'{BASE_URL}/api/users/me',headers=HEADERS)
    print_resp(resp=resp)


def method_color(method):
    if method == "delete":
        return f"{Color.RED}delete{Color.END}"
    elif method == "post":
        return f"{Color.BLUE}post{Color.END}"
    elif method == "put":
        return f"{Color.YELLOW}put{Color.END}"


def print_tasks():
    resp = httpx.request(method="get",url=f'{BASE_URL}/api/tasks', headers=HEADERS).json()
    
    data = []
    for task in resp["data"]:
        task["method"] = method_color(task["method"])
        task["postTime"] = datetime.datetime.fromisoformat(task["postTime"]).strftime('%Y-%m-%d %H:%M:%S')
        task["runTime"] = f'{int(0 if task["runTime"] == None else task["runTime"])}s'
        del task["result"], task["log"], task["startTime"], task["updateTime"], task["request"], task["dependenceUuid"], task["uuid"]
        data.append(task)
    
    print(tabulate(data, tablefmt='simple'))


def print_storages():
    resp = httpx.request(method="get",url=f'{BASE_URL}/api/storages', headers=HEADERS).json()
    data = []
    
    for task in resp["data"]:
        # task["node"] = task["node"]["name"]
        del task["node"]
        data.append(task)
    print(tabulate(data, tablefmt='simple'))

def print_vms():
    resp = httpx.request(method="get",url=f'{BASE_URL}/api/vms', headers=HEADERS, params={"admin":True}).json()
    
    data = []
    for task in resp["data"]:
        data.append(task)
    
    print(tabulate(data, tablefmt='simple'))


def print_users():
    resp = httpx.request(method="get",url=f'{BASE_URL}/api/users', headers=HEADERS, params={"admin":True}).json()
    for task in resp:
        print ("{:<16} {:<64} {:<32}".format(
            task["username"],
            str(task["scopes"]),
            str(task["projects"])
        ))


def print_nodes():
    resp = httpx.request(method="get",url=f'{BASE_URL}/api/nodes', headers=HEADERS).json()
    
    data = []
    for task in resp["data"]:
        del task["cpuGen"], task["description"], task["roles"]
        data.append(task)
    
    print(tabulate(data, headers='keys',tablefmt='simple'))


if __name__ == "__main__":
    if len(args) == 2:
        if args[1] == "show-task":
            print_tasks()
        if args[1] == "show-storage":
            print_storages()
        if args[1] == "show-node":
            print_nodes()
        if args[1] == "show-vm":
            print_vms()
        if args[1] == "show-user":
            print_users()