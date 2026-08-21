
import pytest
from fastapi.testclient import TestClient
from urllib.parse import urlparse

from domain.schemas import (
    DomainForCreate,
    DomainForCreateDisk,
    DomainForCreateInterface,
    DomainPage,
)
from network.schemas import NetworkPage
from storage.schemas import StoragePage
from tests.external.conftest import EnvConfig, wait_tasks


def _exact_vms(page: DomainPage, name: str, node_name: str):
    return [
        vm
        for vm in page.data
        if vm.name == name and vm.node_name == node_name
    ]


@pytest.fixture(scope="function")
def vm_images(env, client, created_storage):
    storage_names = {
        "image": next(item.name for item in env.storages if item.name.endswith("test-cloud")),
        "iso": next(item.name for item in env.storages if item.name.endswith("test-iso")),
    }
    urls = {"image": env.image_url, "iso": env.iso_url}

    for server in env.servers:
        for kind, storage_name in storage_names.items():
            response = client.get(
                "/api/storages",
                params={"nameLike": storage_name, "nodeName": server.name},
            )
            page = StoragePage.model_validate(response.json())
            assert page.count == 1
            task_response = client.post(
                "/api/tasks/images/download",
                json={"storage_uuid": page.data[0].uuid, "image_url": urls[kind]},
            )
            assert task_response.status_code == 200
            assert wait_tasks(task_response, client) == "finish"

    return {
        kind: urlparse(url).path.rsplit("/", 1)[-1]
        for kind, url in urls.items()
    }


@pytest.fixture(scope="function")
def created_vm(env, client, created_network, created_storage, vm_images):
    create_vm(env, client)

    res = client.get("/api/vms")
    try:
        yield DomainPage.model_validate(res.json())
    finally:
        delete_vm(env, client, skipp=True)


@pytest.fixture(scope="function")
def deleted_vm(env, client, created_network, created_storage, vm_images):
    delete_vm(env, client, skipp=True)

    res = client.get("/api/vms")
    try:
        yield DomainPage.model_validate(res.json())
    finally:
        delete_vm(env, client, skipp=True)


def create_vm(env: EnvConfig, client: TestClient):
    reload_vms(env, client)
    storage_cloud_name = next(item.name for item in env.storages if item.name.endswith("test-cloud"))
    storage_img_name = next(item.name for item in env.storages if item.name.endswith("test-img"))
    network_name = next(item.name for item in env.networks if item.name.endswith("test-nat"))
    image_name = urlparse(env.image_url).path.rsplit("/", 1)[-1]
    assert image_name
    for server in env.servers:
        for vm in env.vms:
            res_storage_cloud = StoragePage.model_validate(client.get("/api/storages", params={"nameLike": storage_cloud_name, "nodeName": server.name}).json())
            res_storage_img = StoragePage.model_validate(client.get("/api/storages", params={"nameLike": storage_img_name, "nodeName": server.name}).json())
            res_network = NetworkPage.model_validate(client.get("/api/networks", params={"nameLike": network_name, "nodeName": server.name}).json())

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
                        original_name=image_name,),
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
                # cloud-init ISOは製品側が共有固定pathへ残すためexternalでは作らない。
                cloud_init=None,
            )

            # すでにあるか判定
            res_vm = client.get("/api/vms", params={"nameLike": f"{vm.name}-{server.name}", "nodeNameLike": server.name, "admin": True})
            # pprint(res_vm.json())
            page = DomainPage.model_validate(res_vm.json())
            exact_vms = _exact_vms(page, f"{vm.name}-{server.name}", server.name)
            assert not exact_vms, (
                f"既存VMは再利用できません: {server.name}/{vm.name}"
            )

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
            exact_vms = _exact_vms(page, f"{vm.name}-{server.name}", server.name)
            if not exact_vms and skipp:
                continue

            assert exact_vms
            for vm_data in exact_vms:
                pool_uuid = vm_data.uuid

                res = client.delete(f'/api/tasks/vms/{pool_uuid}')

                assert res.status_code == 200
                assert wait_tasks(res, client) == "finish"


def reload_vms(env: EnvConfig, client: TestClient):
    put_vm = client.put("/api/tasks/vms", params={})
    wait_tasks(put_vm, client)
