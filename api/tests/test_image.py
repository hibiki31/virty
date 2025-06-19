
from fastapi.testclient import TestClient

from storage.schemas import StoragePage


def test_image_download(env, client, wait_tasks):
    for server in env.servers:
        
        image_download(wait_tasks, node_name=server.name, storage_name="test-cloud", image_url=env.image_url, client=client)
        # image_download(wait_tasks, node_name=server.name, storage_name="test-iso", image_url=env.iso_url, client=client)
        

def image_download(wait_tasks, client:TestClient, node_name, storage_name, image_url):    
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
    
    