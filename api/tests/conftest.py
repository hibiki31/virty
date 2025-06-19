
import json
import time
from typing import List

import httpx
import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel

from main import app


class User(BaseModel):
    username: str
    password: str
class Project(BaseModel):
    name: str
class Server(BaseModel):
    name: str
    domain: str
    username: str
class Storage(BaseModel):
    name: str
    path: str
class EnvConfig(BaseModel):
    base_url: str
    username: str
    password: str
    users: List[User]
    projects: List[Project]
    key: str
    pub: str
    servers: List[Server]
    storages: List[Storage]
    image_url: str
    iso_url: str


@pytest.fixture(scope="session")
def env():
    return EnvConfig.model_validate(json.load(open('./tests/env.json', 'r')))


@pytest.fixture(scope="session")
def BASE_URL(env):
    return env.base_url


@pytest.fixture(scope="session")
def HEADERS(env):
    req_data = {
        "username": str(env.username),
        "password": str(env.password)
    }
    
    if not httpx.get(f'{BASE_URL}/api/version').json()["initialized"]:
        httpx.post(f'{BASE_URL}/api/auth/setup', json=req_data)


    resp = httpx.post(f'{BASE_URL}/api/auth', data=req_data)


    token = resp.json()["access_token"]
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'    
    }
    
    return headers

@pytest.fixture(scope="session")
def gust_client():
    return TestClient(app)


@pytest.fixture(scope="session")
def client(env, gust_client):
    req_data = {
        "username": str(env.username),
        "password": str(env.password)
    }
    
    
    if not gust_client.get('/api/version').json()["initialized"]:
        gust_client.post('/api/auth/setup', json=req_data)
        
    resp = gust_client.post('/api/auth', data=req_data)

    token = resp.json()["access_token"]
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'    
    }
    
    return TestClient(app, headers=headers)

def _wait_tasks(resp, client: TestClient) -> str :
    for task in resp.json():
        uuid = task["uuid"]
        counter = 0
        while True:
            resp = client.request(method="get",url=f'/api/tasks/{uuid}').json()
            # print(f"wait {uuid} {resp['resource']} {resp['object']} {counter}s")
            if resp["status"] in[ "error", "lost"] :
                return resp["status"]
            if resp["status"] in[ "finish" ] :
                break
            time.sleep(0.5)
            counter += 0.5
    return "finish"
            
@pytest.fixture(scope="session")
def wait_tasks() -> _wait_tasks:
    return _wait_tasks


pytest_plugins = [
    "tests.fixtures.node",
]