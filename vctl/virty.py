#!/usr/bin/env python3


import typer
import httpx
import json
import os.path
from typer import Option as tyo
import re
from tabulate import tabulate

CONFIG_PATH = f'{os.environ["HOME"]}/.virty_auth'

if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'r') as f:
        auth_json = json.load(f)
        BASE_URL = auth_json["BASE_URL"]
        HEADERS = auth_json["HEADERS"]


app = typer.Typer(help="Virty CLI")
app_get = typer.Typer()

app.add_typer(app_get, name="get")

def complete_name():
    return ["aa"]



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


@app_get.command()
def get_node():
    resp = httpx.request(method="get",url=f'{BASE_URL}/api/nodes', headers=HEADERS).json()
    
    data = []
    for task in resp["data"]:
        del task["cpuGen"], task["description"], task["roles"]
        data.append(task)
    
    print(tabulate(data, headers='keys',tablefmt='simple'))

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