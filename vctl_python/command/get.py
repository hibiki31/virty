import typer
import httpx
from tabulate import tabulate

from module.common import *
from module.settings import *


app = typer.Typer()


@app.command(name="task")
def get_task(
        page:int =1
    ):
    resp = httpx.request(method="get",url=f'{BASE_URL}/api/tasks', params={"page": page-1, "limit": 15},headers=HEADERS).json()
    
    data = []
    for task in resp["data"]:
        task["method"] = method_color(task["method"])
        task["postTime"] = pase_date_short(task["postTime"])
        task["runTime"] = f'{int(0 if task["runTime"] == None else task["runTime"])}s'
        del task["result"], task["log"], task["startTime"], task["updateTime"], task["request"], task["dependenceUuid"], task["uuid"]
        data.append(task)
    print(f"Find {resp['count']} tasks. Page: {page}")
    print(tabulate(data, tablefmt='simple'))


@app.command(name="storage")
def get_storage(page:int =1):
    resp = httpx.request(method="get",url=f'{BASE_URL}/api/storages', headers=HEADERS).json()
    data = []
    
    for task in resp["data"]:
        # task["node"] = task["node"]["name"]
        del task["node"]
        data.append(task)
    print(tabulate(data, tablefmt='simple'))
    
    
@app.command(name="vm")
def get_vm(page:int =1):
    resp = httpx.request(method="get",url=f'{BASE_URL}/api/vms', headers=HEADERS, params={"admin":True}).json()
    
    data = []
    for task in resp["data"]:
        del task["drives"], task["ownerProject"], task["description"], task["interfaces"]
        data.append(task)
    
    print(tabulate(data, headers='keys', tablefmt='simple'))


@app.command(name="user")
def get_user(page:int =1):
    resp = httpx.request(method="get",url=f'{BASE_URL}/api/users', headers=HEADERS, params={"admin":True}).json()
    data = []
    for task in resp["data"]:
        data.append(task)
    print(tabulate(data, headers='keys', tablefmt='simple'))


@app.command(name="node")
def get_node():
    resp = httpx.request(method="get",url=f'{BASE_URL}/api/nodes', headers=HEADERS).json()
    
    data = []
    for task in resp["data"]:
        del task["cpuGen"], task["description"], task["roles"]
        data.append(task)
    
    print(tabulate(data, headers='keys',tablefmt='simple'))