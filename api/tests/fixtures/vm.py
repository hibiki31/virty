
import pytest
from fastapi.testclient import TestClient

from domain.schemas import (
    CloudInitInsert,
    DomainForCreate,
    DomainForCreateDisk,
    DomainForCreateInterface,
    DomainPage,
)
from network.schemas import NetworkPage
from storage.schemas import StoragePage
from tests.conftest import EnvConfig, wait_tasks


@pytest.fixture(scope="function")
def created_vm(env, client, created_network, created_storage):
    create_vm(env, client, skipp=True)

    res = client.get("/api/vms")
    yield  DomainPage.model_validate(res.json())


@pytest.fixture(scope="function")
def deleted_vm(env, client, created_network, created_storage):
    delete_vm(env, client, skipp=True)

    res = client.get("/api/vms")
    yield  DomainPage.model_validate(res.json())


def create_vm(env: EnvConfig, client: TestClient, skipp=False):
    reload_vms(env, client)
    for server in env.servers:
        for vm in env.vms:
            res_storage_cloud = StoragePage.model_validate(client.get("/api/storages", params={"nameLike": "test-cloud", "nodeName": server.name}).json())
            res_storage_img = StoragePage.model_validate(client.get("/api/storages", params={"nameLike": "test-img", "nodeName": server.name}).json())
            res_network = NetworkPage.model_validate(client.get("/api/networks", params={"nameLike": "test-nat", "nodeName": server.name}).json())
            
            req_data = DomainForCreate(
                type="manual",
                name=f"{vm.name}-{server.name}",
                node_name=server.name,
                memory_mega_byte=4096,
                cpu=4,
                disks=[
                    DomainForCreateDisk(
                        type="copy",
                        size_giga_byte=64,
                        save_pool_uuid=res_storage_img.data[0].uuid,
                        original_pool_uuid=res_storage_cloud.data[0].uuid,
                        original_name="noble-server-cloudimg-amd64.img",),
                    # DomainForCreateDisk(
                    #     type="empty",
                    #     size_giga_byte=128,
                    #     save_pool_uuid=res_storage_img.data[0].uuid,),
                ],
                interface=[
                    DomainForCreateInterface(
                        type="network",
                        network_uuid=res_network.data[0].uuid
                    )
                    ],
                cloud_init=CloudInitInsert(
                    hostname=f"{vm.name}-{server.name}-cloud",
                    userData="""#cloud-config
password: password
user: virty_user
chpasswd: {expire: False}
ssh_pwauth: True
ssh_authorized_keys:
  - ssh-rsa AAA...fHQ== sample@example.com
                """
                )
            )
        
            # すでにあるか判定
            res_vm = client.get("/api/vms", params={"nameLike": f"{vm.name}-{server.name}", "nodeNameLike": server.name, "admin": True})
            # pprint(res_vm.json())
            page = DomainPage.model_validate(res_vm.json())
            if skipp and page.count >= 1:
                continue
            
            res = client.post("/api/tasks/vms", content=req_data.model_dump_json(by_alias=True))
            assert res.status_code == 200
            assert wait_tasks(res, client) == "finish"
 
            
            
def delete_vm(env: EnvConfig, client: TestClient, skipp=False):
    reload_vms(env, client)
    for server in env.servers:
        for vm in env.vms:
            res_vm = client.get("/api/vms", params={"nameLike": f"{vm.name}-{server.name}", "nodeNameLike": server.name, "admin": True})
            # pprint(res_vm.json())
            
            page = DomainPage.model_validate(res_vm.json())
            if page.count == 0 and skipp:
                continue    
            
            assert page.count >= 1
            for vm_data in page.data:
                pool_uuid = vm_data.uuid
                
                res = client.delete(f'/api/tasks/vms/{pool_uuid}')
                
                assert res.status_code == 200
                assert wait_tasks(res, client) == "finish"
            
            
def reload_vms(env: EnvConfig, client: TestClient):
    put_vm = client.put("/api/tasks/vms", params={})
    wait_tasks(put_vm, client)