
from fastapi.testclient import TestClient

from storage.schemas import StoragePage
from tests.external.conftest import wait_tasks


def test_image_download(env, client, created_storage):
    cloud_name = next(item.name for item in env.storages if item.name.endswith("test-cloud"))
    iso_name = next(item.name for item in env.storages if item.name.endswith("test-iso"))
    for server in env.servers:
        
        image_download(node_name=server.name, storage_name=cloud_name, image_url=env.image_url, client=client)
        image_download(node_name=server.name, storage_name=iso_name, image_url=env.iso_url, client=client)
        

def image_download(client:TestClient, node_name, storage_name, image_url):    
    res = client.get('/api/storages', params={"nameLike": storage_name, "nodeName": node_name})
    
    assert res.status_code == 200
    res_model = StoragePage.model_validate(res.json())


    assert res_model.data != []

    req_data={
        "storage_uuid": res_model.data[0].uuid,
        "image_url": image_url
    }
    res_images = client.post('/api/tasks/images/download', json=req_data)

    assert wait_tasks(res_images, client) == "finish"

