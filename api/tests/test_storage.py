from storage.schemas import StoragePage


def test_delete_storage(env, client, wait_tasks):
    for server in env.servers:
        for storage in env.storages:  
            res_storage = client.get("/api/storages", params={"name": storage.name, "nodeName": server.name})
            
            page = StoragePage.model_validate(res_storage.json())
            if page.count == 0:
                continue
            
            pool_uuid = page.data[0].uuid
            
            res = client.delete(f'/api/tasks/storages/{pool_uuid}')
            
            assert res.status_code in 200
            assert wait_tasks(res, client) == "finish"


def test_post_storage_ok(env, client, wait_tasks):
    for server in env.servers:
        for storage in env.storages:  
            req_data = {
                "name": storage.name,
                "nodeName": server.name,
                "path": storage.path
            }
            res = client.post('/api/tasks/storages', json=req_data)
            
            assert res.status_code == 200
            assert wait_tasks(res, client) == "finish"