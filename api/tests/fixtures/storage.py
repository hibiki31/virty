import pytest
from fastapi.testclient import TestClient

from storage.schemas import StoragePage
from tests.conftest import EnvConfig, wait_tasks


@pytest.fixture(scope="function")
def created_storage(env, client, nodes):
    create_storage(env, client, skipp=True)

    res = client.get("/api/storages")
    yield  StoragePage.model_validate(res.json())


@pytest.fixture(scope="function")
def deleted_storage(env, client, nodes):
    delete_storage(env, client, skipp=True)

    res = client.get("/api/storages")
    yield  StoragePage.model_validate(res.json())


def create_storage(env: EnvConfig, client: TestClient, skipp=False):
    reload_storage(env, client)
    
    for server in env.servers:
        for storage in env.storages:  
            req_data = {
                "name": storage.name,
                "nodeName": server.name,
                "path": storage.path
            }
            
            # すでにあるか判定
            res_storage = client.get("/api/storages", params={"nameLike": storage.name, "nodeName": server.name})
            page = StoragePage.model_validate(res_storage.json())
            if page.count == 1:
                continue
            
            res = client.post('/api/tasks/storages', json=req_data)
            
            assert res.status_code == 200
            assert wait_tasks(res, client) == "finish"
    
    reload_storage(env, client)
            
            
def delete_storage(env: EnvConfig, client: TestClient, skipp=False):
    reload_storage(env, client)
    for server in env.servers:
        for storage in env.storages:  
            res_storage = client.get("/api/storages", params={"nameLike": storage.name, "nodeName": server.name})
            
            page = StoragePage.model_validate(res_storage.json())
            if page.count == 0 and skipp:
                continue
            
            assert page.count == 1
            pool_uuid = page.data[0].uuid
            
            res = client.delete(f'/api/tasks/storages/{pool_uuid}')
            
            assert res.status_code == 200
            assert wait_tasks(res, client) == "finish"
    reload_storage(env, client)
            
            
def reload_storage(env: EnvConfig, client: TestClient):
    put_image = client.put("/api/tasks/images", params={})
    wait_tasks(put_image, client)