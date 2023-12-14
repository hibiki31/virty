#!/usr/bin/env python3


import typer
import httpx
import json
import os.path
from typer import Option as tyo
import re
from tabulate import tabulate
from pprint import pprint
import time
import datetime

CONFIG_PATH = f'{os.environ["HOME"]}/.virty_auth'

if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'r') as f:
        auth_json = json.load(f)
        BASE_URL = auth_json["BASE_URL"]
        HEADERS = auth_json["HEADERS"]


app = typer.Typer(help="Virty CLI")
app_get = typer.Typer()
app_delete = typer.Typer()
app_update = typer.Typer()

app.add_typer(app_get, name="get")
app.add_typer(app_delete, name="delete")
app.add_typer(app_update, name="update")


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
def method_color(method):
    if method == "delete":
        return f"{Color.RED}delete{Color.END}"
    elif method == "post":
        return f"{Color.BLUE}post{Color.END}"
    elif method == "put":
        return f"{Color.YELLOW}put{Color.END}"

def complete_name():
    return ["aa"]


def pase_date_short(date_str):
    pase_datetime =  datetime.datetime.fromisoformat(date_str)

    local_timezone = datetime.datetime.now().astimezone().tzinfo

    return pase_datetime.astimezone(local_timezone).strftime('%Y-%m-%d %H:%M:%S')


def wait_tasks(resp):
    for task in resp.json():
        uuid = task["uuid"]
        counter = 0
        while True:
            resp = httpx.request(method="get",url=f'{BASE_URL}/api/tasks/{uuid}', headers=HEADERS).json()
            # print(f"wait {uuid} {resp['resource']} {resp['object']} {counter}s")
            if resp["status"] == "finish":
                print(f"{Color.GREEN}Task Finish {Color.END}{uuid} {resp['resource']} {resp['object']} {counter}s")
                break
            elif resp["status"] == "error":
                print(f"{Color.RED}Task Error {Color.END}{uuid} {resp['resource']} {resp['object']} {counter}s")
                break
            time.sleep(0.5)
            counter += 0.5


def print_resp(resp: httpx.Response, allow_not_found=False, debug=False):    
    if resp.status_code == 200:
        print(f"{Color.BLUE}{resp} {resp.request.method} {resp.url}{Color.END}")
    else:
        print(f"{Color.RED}{resp} {resp.request.method} {resp.url}{Color.END}")

    if debug:
        pprint(resp.json())

    if allow_not_found and resp.status_code == 404:
        print(f"{Color.GREEN}Allow not found{Color.END}")
    elif resp.status_code != 200:
        print(resp.json())
        raise Exception



@app_update.command(name="list-all")
def update_all_list():
    resp = httpx.put(f'{BASE_URL}/api/tasks/images',headers=HEADERS)
    print_resp(resp=resp)
    wait_tasks(resp)
    
    resp = httpx.put(f'{BASE_URL}/api/tasks/vms',headers=HEADERS)
    print_resp(resp=resp)
    wait_tasks(resp)

    resp = httpx.put(f'{BASE_URL}/api/tasks/networks',headers=HEADERS)
    print_resp(resp=resp)
    wait_tasks(resp)


@app.command()
def auth(
        url: str = tyo(...,prompt='URL',hide_input=False),
        username: str = tyo(...,prompt='Username',hide_input=False),
        password: str = tyo(...,prompt='Password',hide_input=True),
    ):
    
    req_data = {
        "username": username,
        "password": password
    }
    url = re.sub(r"$/","",url)
    
    resp = httpx.post(f'{url}/api/auth', data=req_data)
    
    if resp.status_code == 200:
        ACCESS_TOKEN = resp.json()["access_token"]
        HEADERS = {
            'Authorization': f'Bearer {ACCESS_TOKEN}',
            'Content-Type': 'application/json'    
        }
        with open(CONFIG_PATH, mode='w') as f:
            dump_data = {
                "BASE_URL": url,
                "HEADERS": HEADERS
            }
            json.dump(dump_data, f, indent=2)
        print("Success!!")
    else:
        raise Exception("Loggin fail")


@app_get.command(name="node")
def get_node():
    resp = httpx.request(method="get",url=f'{BASE_URL}/api/nodes', headers=HEADERS).json()
    
    data = []
    for task in resp["data"]:
        del task["cpuGen"], task["description"], task["roles"]
        data.append(task)
    
    print(tabulate(data, headers='keys',tablefmt='simple'))


@app_get.command(name="task")
def get_task(page:int =1):
    resp = httpx.request(method="get",url=f'{BASE_URL}/api/tasks', params={"page": page-1},headers=HEADERS).json()
    
    data = []
    for task in resp["data"]:
        task["method"] = method_color(task["method"])
        task["postTime"] = pase_date_short(task["postTime"])
        task["runTime"] = f'{int(0 if task["runTime"] == None else task["runTime"])}s'
        del task["result"], task["log"], task["startTime"], task["updateTime"], task["request"], task["dependenceUuid"], task["uuid"]
        data.append(task)
    
    print(tabulate(data, tablefmt='simple'))


@app_get.command(name="storage")
def get_storage(page:int =1):
    resp = httpx.request(method="get",url=f'{BASE_URL}/api/storages', headers=HEADERS).json()
    data = []
    
    for task in resp["data"]:
        # task["node"] = task["node"]["name"]
        del task["node"]
        data.append(task)
    print(tabulate(data, tablefmt='simple'))
    
    
@app_get.command(name="vm")
def get_vm(page:int =1):
    resp = httpx.request(method="get",url=f'{BASE_URL}/api/vms', headers=HEADERS, params={"admin":True}).json()
    
    data = []
    for task in resp["data"]:
        del task["drives"], task["ownerProject"], task["description"], task["interfaces"]
        data.append(task)
    
    print(tabulate(data, headers='keys', tablefmt='simple'))


@app_get.command(name="user")
def get_user(page:int =1):
    resp = httpx.request(method="get",url=f'{BASE_URL}/api/users', headers=HEADERS, params={"admin":True}).json()
    data = []
    for task in resp["data"]:
        data.append(task)
    print(tabulate(data, headers='keys', tablefmt='simple'))


def complete_node_name(ctx: typer.Context, incomplete: str):
    resp = httpx.request(method="get",url=f'{BASE_URL}/api/nodes', headers=HEADERS).json()
    return [ i["name"] for i in resp["data"] ]
    


@app_delete.command(name="node", help="delete node")
def delete_node(name: str = typer.Option(autocompletion=complete_node_name,)):
    pass
    


@app.command()
def describe(
        username: str = typer.Option(autocompletion=complete_name,)
    ):
    """
    Create a new user with USERNAME.
    """
    print(f"Creating user: {username}")


@app.command()
def delete(
    username: str,
    force: bool = typer.Option(
        ...,
        prompt="Are you sure you want to delete the user?",
        help="Force deletion without confirmation.",
    ),
):
    """
    Delete a user with USERNAME.

    If --force is not used, will ask for confirmation.
    """
    if force:
        print(f"Deleting user: {username}")
    else:
        print("Operation cancelled")



@app.command()
def delete_all(
    force: bool = typer.Option(
        ...,
        prompt="Are you sure you want to delete ALL users?",
        help="Force deletion without confirmation.",
    )
):
    """
    Delete ALL users in the database.

    If --force is not used, will ask for confirmation.
    """
    if force:
        print("Deleting all users")
    else:
        print("Operation cancelled")


@app.command()
def init():
    """
    Initialize the users database.
    """
    print("Initializing user database")


if __name__ == "__main__":
    app()