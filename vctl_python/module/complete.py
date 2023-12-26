import typer
import httpx

from module.settings import *


def node_name(ctx: typer.Context, incomplete: str):
    resp = httpx.request(method="get",url=f'{BASE_URL}/api/nodes', headers=HEADERS).json()
    return [ i["name"] for i in resp["data"] ]

def storage_name(ctx: typer.Context, incomplete: str):
    node_name = ctx.params["node_name"]
    resp = httpx.request(method="get",url=f'{BASE_URL}/api/storages',params={"nodeName":node_name} , headers=HEADERS).json()
    return [ i["name"] for i in resp["data"] ]