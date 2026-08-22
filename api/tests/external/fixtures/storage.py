import pytest
from fastapi.testclient import TestClient

from storage.schemas import StoragePage
from tests.external.conftest import EnvConfig, wait_tasks
from tests.external.support.manifest import ManifestEntry, mark_current_entry_created
from tests.external.support.remote_inventory import (
    assert_libvirt_present,
    remote_inventory_manager,
    storage_pool_state,
    storage_pool_xml,
)


def _exact_storages(page: StoragePage, name: str, node_name: str):
    return [
        storage
        for storage in page.data
        if storage.name == name and storage.node_name == node_name
    ]


@pytest.fixture(scope="session")
def created_storage(env, client, nodes):
    create_storage(env, client)
    response = client.get("/api/storages")
    response.raise_for_status()
    return StoragePage.model_validate(response.json())


def create_storage(env: EnvConfig, client: TestClient):
    reload_storage(env, client)
    for server_index, server in enumerate(env.servers):
        for storage in env.storages:
            req_data = {
                "name": storage.name,
                "nodeName": server.name,
                "path": storage.path
            }
            
            # すでにあるか判定
            res_storage = client.get("/api/storages", params={"nameLike": storage.name, "nodeName": server.name})
            page = StoragePage.model_validate(res_storage.json())
            exact_storages = _exact_storages(page, storage.name, server.name)
            if exact_storages:
                raise AssertionError(
                    "storage API collision precondition failed: "
                    f"server_index={server_index} count={len(exact_storages)}"
                )
            
            res = client.post('/api/tasks/storages', json=req_data)
            
            assert res.status_code == 200
            assert wait_tasks(res, client) == "finish"
    
    reload_storage(env, client)
    for server_index, server in enumerate(env.servers):
        with remote_inventory_manager(
            user=server.username,
            domain=server.domain,
            server_index=server_index,
        ) as remote:
            for storage in env.storages:
                response = client.get(
                    "/api/storages",
                    params={"nameLike": storage.name, "nodeName": server.name},
                )
                response.raise_for_status()
                exact = _exact_storages(
                    StoragePage.model_validate(response.json()),
                    storage.name,
                    server.name,
                )
                if len(exact) != 1:
                    raise AssertionError(
                        "storage API postcondition failed: "
                        f"server_index={server_index} count={len(exact)}"
                    )
                if (
                    exact[0].active is not True
                    or exact[0].capacity <= 0
                    or exact[0].available <= 0
                ):
                    raise AssertionError(
                        "storage API state postcondition failed: "
                        f"server_index={server_index} count=1"
                    )
                resource_uuid = str(exact[0].uuid)
                assert_libvirt_present(
                    remote,
                    kind="storage",
                    name=storage.name,
                    resource_uuid=resource_uuid,
                    server_index=server_index,
                )
                xml = storage_pool_xml(
                    remote,
                    resource_uuid=resource_uuid,
                    server_index=server_index,
                )
                target_path = xml.findtext("./target/path")
                state, autostart = storage_pool_state(
                    remote,
                    resource_uuid=resource_uuid,
                    server_index=server_index,
                )
                if target_path != storage.path or state != "running" or not autostart:
                    raise AssertionError(
                        "storage XML/state postcondition failed: "
                        f"server_index={server_index} count=1"
                    )
                mark_current_entry_created(
                    env,
                    ManifestEntry(
                        kind="storage",
                        node=server.name,
                        name=storage.name,
                        path=storage.path,
                    ),
                    resource_uuid=resource_uuid,
                )
            
            
def reload_storage(env: EnvConfig, client: TestClient):
    put_image = client.put("/api/tasks/images", params={})
    wait_tasks(put_image, client)


def delete_storage_target(
    client: TestClient,
    *,
    node_name: str,
    storage_name: str,
    resource_uuid: str | None,
    skip_absent: bool = True,
) -> str | None:
    response = client.get("/api/storages", params={"limit": 0})
    response.raise_for_status()
    page = StoragePage.model_validate(response.json())
    exact = _exact_storages(page, storage_name, node_name)
    if resource_uuid is not None:
        matching_uuid = [
            storage for storage in page.data if str(storage.uuid) == resource_uuid
        ]
        if any(str(storage.uuid) != resource_uuid for storage in exact):
            raise RuntimeError("manifest storage identity inventory mismatch: count=1")
        exact = matching_uuid
    if not exact and skip_absent:
        return None
    if len(exact) != 1:
        raise RuntimeError(f"storage cleanup inventory mismatch: count={len(exact)}")
    deleted_uuid = str(exact[0].uuid)
    task_response = client.delete(f"/api/tasks/storages/{deleted_uuid}")
    task_response.raise_for_status()
    assert wait_tasks(task_response, client) == "finish"
    confirm = client.get("/api/storages", params={"limit": 0})
    confirm.raise_for_status()
    confirm_page = StoragePage.model_validate(confirm.json())
    remains = _exact_storages(confirm_page, storage_name, node_name)
    remains.extend(
        storage for storage in confirm_page.data if str(storage.uuid) == deleted_uuid
    )
    if remains:
        raise RuntimeError(
            f"storage cleanup API postcondition failed: count={len(remains)}"
        )
    return deleted_uuid
