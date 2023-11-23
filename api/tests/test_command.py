#!/usr/bin/env python3
import httpx
import datetime
import sys

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
    count = 0
    for task in resp["data"]:
        print ("{:<20} {:<4} {:<8} {:<17} {:<9} {:<5} {:<9}".format(
            datetime.datetime.fromisoformat(task["postTime"]).strftime('%Y-%m-%d %H:%M:%S'),
            f'{int(0 if task["runTime"] == None else task["runTime"])}s',
            task["status"],
            method_color(task["method"]),
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


def print_vms():
    resp = httpx.request(method="get",url=f'{BASE_URL}/api/vms', headers=HEADERS, params={"admin":True}).json()
    for task in resp["data"]:
        print ("{:<38} {:<15} {:<8} {:<5}".format(
            task["uuid"],
            task["name"],
            task["status"],
            task["nodeName"],
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
        if args[1] == "show-node":
            print_nodes()
        if args[1] == "show-vm":
            print_vms()