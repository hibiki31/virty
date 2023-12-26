import typer
import httpx
from tabulate import tabulate
from virty import VirtyClinet

from module.common import *
from module.settings import *
from module import complete


app = typer.Typer()


@app.command(name="node", help="delete node")
def delete_node(
        name: str = typer.Option(
            ...,
            autocompletion=complete.node_name,
        )
    ):
    delete = typer.confirm(f"Are you sure you want to delete node {name}?")
    if not delete:
        print("Not deleting")
        raise typer.Abort()
    
    resp = httpx.request(method="delete",url=f'{BASE_URL}/api/tasks/nodes/{name}', headers=HEADERS)
    print_resp(resp=resp, allow_not_found=True)
    wait_tasks(resp)


@app.command(name="storage")
def delete_storage(
        node_name: str = typer.Option(
            ...,
            autocompletion=complete.node_name,
        ),
        name: str = typer.Option(
            ...,
            autocompletion=complete.storage_name,
        )
    ):
    delete = typer.confirm(f"Are you sure you want to delete node {name}?")
    if not delete:
        print("Not deleting")
        raise typer.Abort()
    
    clinet = VirtyClinet(url=BASE_URL, headers=HEADERS)
    clinet.api_delete_storage(pool_name=name, node_name=node_name)
    clinet.wait_task()
