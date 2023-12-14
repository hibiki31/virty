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

from module.common import *
from module.settings import *
from command.get import app as app_get
from command.delete import app as app_delete
from command.update import app as app_update
from module import complete


app = typer.Typer(help="Virty CLI")


app.add_typer(app_get, name="get")
app.add_typer(app_delete, name="delete")
app.add_typer(app_update, name="update")


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


if __name__ == "__main__":
    app()