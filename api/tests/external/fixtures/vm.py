import os
from pathlib import PurePosixPath
from urllib.parse import urlparse
from xml.etree.ElementTree import Element

import pytest
from fastapi.testclient import TestClient

from domain.schemas import (
    DomainForCreate,
    DomainForCreateDisk,
    DomainForCreateInterface,
    DomainPage,
)
from network.schemas import NetworkPage
from storage.schemas import StoragePage
from tests.external.conftest import EnvConfig, wait_tasks
from tests.external.support.config import derive_resource_name
from tests.external.support.manifest import ManifestEntry, mark_current_entry_created
from tests.external.support.remote_inventory import (
    assert_libvirt_present,
    domain_xml,
    qemu_virtual_size,
    remote_inventory_manager,
)


VM_DISK_BYTES = 64 * 1024**3
VM_MEMORY_BYTES = 4 * 1024**3
MEMORY_UNIT_BYTES = {
    "b": 1,
    "kb": 1000,
    "kib": 1024,
    "mb": 1000**2,
    "mib": 1024**2,
    "gb": 1000**3,
    "gib": 1024**3,
}


def _exact_vms(page: DomainPage, name: str, node_name: str):
    return [
        vm
        for vm in page.data
        if vm.name == name and vm.node_name == node_name
    ]


def vm_resource_name(vm_name: str, server_name: str) -> str:
    return derive_resource_name(
        os.environ["VIRTY_TEST_RUN_ID"],
        vm_name,
        server_name,
    )


@pytest.fixture(scope="session")
def vm_images(env, client, created_storage):
    storage_names = {
        "image": next(
            item.name for item in env.storages if item.name.endswith("test-cloud")
        ),
        "iso": next(
            item.name for item in env.storages if item.name.endswith("test-iso")
        ),
    }
    urls = {"image": env.image_url, "iso": env.iso_url}

    for server_index, server in enumerate(env.servers):
        for kind, storage_name in storage_names.items():
            response = client.get(
                "/api/storages",
                params={"nameLike": storage_name, "nodeName": server.name},
            )
            response.raise_for_status()
            exact = [
                storage
                for storage in StoragePage.model_validate(response.json()).data
                if storage.name == storage_name and storage.node_name == server.name
            ]
            if len(exact) != 1:
                raise AssertionError(
                    "image storage precondition failed: "
                    f"server_index={server_index} count={len(exact)}"
                )
            task_response = client.post(
                "/api/tasks/images/download",
                json={"storage_uuid": exact[0].uuid, "image_url": urls[kind]},
            )
            task_response.raise_for_status()
            assert wait_tasks(task_response, client) == "finish"

    return {
        kind: urlparse(url).path.rsplit("/", 1)[-1]
        for kind, url in urls.items()
    }


@pytest.fixture(scope="session")
def created_vm(
    env,
    client,
    created_network,
    created_storage,
    created_project,
    vm_images,
):
    create_vm(env, client, created_project)

    response = client.get("/api/vms")
    response.raise_for_status()
    return DomainPage.model_validate(response.json())


def _exact_storage(page: StoragePage, name: str, node_name: str):
    return [
        storage
        for storage in page.data
        if storage.name == name and storage.node_name == node_name
    ]


def _exact_network(page: NetworkPage, name: str, node_name: str):
    return [
        network
        for network in page.data
        if network.name == name and network.node_name == node_name
    ]


def _xml_memory_bytes(xml: Element) -> int | None:
    memory = xml.find("memory")
    if memory is None or memory.text is None:
        return None
    multiplier = MEMORY_UNIT_BYTES.get(memory.get("unit", "kib").lower())
    try:
        value = int(memory.text)
    except ValueError:
        return None
    return value * multiplier if multiplier is not None else None


def create_vm(env: EnvConfig, client: TestClient, project_id: str) -> None:
    reload_vms(env, client)
    storage_cloud_name = next(
        item.name for item in env.storages if item.name.endswith("test-cloud")
    )
    storage_img_name = next(
        item.name for item in env.storages if item.name.endswith("test-img")
    )
    image_name = urlparse(env.image_url).path.rsplit("/", 1)[-1]
    if not image_name:
        raise AssertionError("VM image precondition failed: count=0")

    for server_index, server in enumerate(env.servers):
        cloud_response = client.get(
            "/api/storages",
            params={"nameLike": storage_cloud_name, "nodeName": server.name},
        )
        image_response = client.get(
            "/api/storages",
            params={"nameLike": storage_img_name, "nodeName": server.name},
        )
        cloud_response.raise_for_status()
        image_response.raise_for_status()
        cloud = _exact_storage(
            StoragePage.model_validate(cloud_response.json()),
            storage_cloud_name,
            server.name,
        )
        image = _exact_storage(
            StoragePage.model_validate(image_response.json()),
            storage_img_name,
            server.name,
        )
        if len(cloud) != 1 or len(image) != 1:
            raise AssertionError(
                "VM dependency precondition failed: "
                f"server_index={server_index} count=1"
            )

        for vm in env.vms:
            exact_vm_name = vm_resource_name(vm.name, server.name)
            network_response = client.get(
                "/api/networks",
                params={"nameLike": vm.network, "nodeNameLike": server.name},
            )
            network_response.raise_for_status()
            network = _exact_network(
                NetworkPage.model_validate(network_response.json()),
                vm.network,
                server.name,
            )
            if len(network) != 1:
                raise AssertionError(
                    "VM network precondition failed: "
                    f"server_index={server_index} count={len(network)}"
                )
            existing_response = client.get(
                "/api/vms",
                params={
                    "nameLike": exact_vm_name,
                    "nodeNameLike": server.name,
                    "admin": True,
                },
            )
            existing_response.raise_for_status()
            existing = _exact_vms(
                DomainPage.model_validate(existing_response.json()),
                exact_vm_name,
                server.name,
            )
            if existing:
                raise AssertionError(
                    "VM collision precondition failed: "
                    f"server_index={server_index} count={len(existing)}"
                )
            request = DomainForCreate(
                type="manual",
                name=exact_vm_name,
                node_name=server.name,
                project_id=project_id,
                memory_mega_byte=4096,
                cpu=4,
                disks=[
                    DomainForCreateDisk(
                        type="copy",
                        size_giga_byte=64,
                        save_pool_uuid=image[0].uuid,
                        original_pool_uuid=cloud[0].uuid,
                        original_name=image_name,
                    )
                ],
                interface=[
                    DomainForCreateInterface(
                        type="network",
                        network_uuid=network[0].uuid,
                    )
                ],
                cloud_init=None,
            )
            response = client.post(
                "/api/tasks/vms",
                content=request.model_dump_json(by_alias=True),
            )
            response.raise_for_status()
            assert wait_tasks(response, client) == "finish"

    reload_vms(env, client)
    for server_index, server in enumerate(env.servers):
        with remote_inventory_manager(
            user=server.username,
            domain=server.domain,
            server_index=server_index,
        ) as remote:
            for vm in env.vms:
                exact_vm_name = vm_resource_name(vm.name, server.name)
                response = client.get(
                    "/api/vms",
                    params={
                        "nameLike": exact_vm_name,
                        "nodeNameLike": server.name,
                        "admin": True,
                    },
                )
                response.raise_for_status()
                exact = _exact_vms(
                    DomainPage.model_validate(response.json()),
                    exact_vm_name,
                    server.name,
                )
                if len(exact) != 1:
                    raise AssertionError(
                        "VM API postcondition failed: "
                        f"server_index={server_index} count={len(exact)}"
                    )
                if exact[0].core != 4 or exact[0].memory != 4096:
                    raise AssertionError(
                        "VM API sizing postcondition failed: "
                        f"server_index={server_index} count=1"
                    )
                resource_uuid = str(exact[0].uuid)
                assert_libvirt_present(
                    remote,
                    kind="vm",
                    name=exact_vm_name,
                    resource_uuid=resource_uuid,
                    server_index=server_index,
                )
                xml = domain_xml(
                    remote,
                    resource_uuid=resource_uuid,
                    server_index=server_index,
                )
                disks = xml.findall("./devices/disk[@device='disk']")
                interfaces = xml.findall("./devices/interface[@type='network']")
                vcpu = xml.find("vcpu")
                disk_source = disks[0].find("source") if len(disks) == 1 else None
                disk_target = disks[0].find("target") if len(disks) == 1 else None
                interface_source = (
                    interfaces[0].find("source") if len(interfaces) == 1 else None
                )
                disk_path = (
                    disk_source.get("file") if disk_source is not None else None
                )
                expected_disk_parent = next(
                    storage.path
                    for storage in env.storages
                    if storage.name.endswith("test-img")
                )
                if (
                    vcpu is None
                    or vcpu.text is None
                    or vcpu.text.strip() != "4"
                    or _xml_memory_bytes(xml) != VM_MEMORY_BYTES
                    or len(disks) != 1
                    or disk_path is None
                    or str(PurePosixPath(disk_path).parent) != expected_disk_parent
                    or disk_target is None
                    or disk_target.get("dev") != "vda"
                    or qemu_virtual_size(
                        remote,
                        path=disk_path or "",
                        server_index=server_index,
                    )
                    != VM_DISK_BYTES
                    or len(interfaces) != 1
                    or interface_source is None
                    or interface_source.get("network") != vm.network
                ):
                    raise AssertionError(
                        "VM XML postcondition failed: "
                        f"server_index={server_index} count=1"
                    )
                mark_current_entry_created(
                    env,
                    ManifestEntry(
                        kind="vm",
                        node=server.name,
                        name=exact_vm_name,
                    ),
                    resource_uuid=resource_uuid,
                )


def reload_vms(env: EnvConfig, client: TestClient) -> None:
    response = client.put("/api/tasks/vms", params={})
    response.raise_for_status()
    assert wait_tasks(response, client) == "finish"


def delete_vm_target(
    client: TestClient,
    *,
    node_name: str,
    vm_name: str,
    resource_uuid: str | None,
    skip_absent: bool = True,
) -> str | None:
    response = client.get("/api/vms", params={"limit": 0, "admin": True})
    response.raise_for_status()
    page = DomainPage.model_validate(response.json())
    exact = _exact_vms(page, vm_name, node_name)
    if resource_uuid is not None:
        matching_uuid = [vm for vm in page.data if str(vm.uuid) == resource_uuid]
        if any(str(vm.uuid) != resource_uuid for vm in exact):
            raise RuntimeError("manifest VM identity inventory mismatch: count=1")
        exact = matching_uuid
    if not exact and skip_absent:
        return None
    if len(exact) != 1:
        raise RuntimeError(f"VM cleanup inventory mismatch: count={len(exact)}")
    deleted_uuid = str(exact[0].uuid)
    task_response = client.delete(f"/api/tasks/vms/{deleted_uuid}")
    task_response.raise_for_status()
    assert wait_tasks(task_response, client) == "finish"
    confirm = client.get("/api/vms", params={"limit": 0, "admin": True})
    confirm.raise_for_status()
    confirm_page = DomainPage.model_validate(confirm.json())
    remains = _exact_vms(confirm_page, vm_name, node_name)
    remains.extend(vm for vm in confirm_page.data if str(vm.uuid) == deleted_uuid)
    if remains:
        raise RuntimeError(f"VM cleanup API postcondition failed: count={len(remains)}")
    return deleted_uuid
