import os
import time
from urllib.parse import urlparse
from uuid import UUID

import pytest

from domain.schemas import (
    DomainForCreate,
    DomainForCreateDisk,
    DomainForCreateInterface,
    DomainPage,
)
from network.schemas import NetworkPage
from storage.schemas import StoragePage
from tests.external.fixtures.vm import _exact_vms, reload_vms, vm_resource_name
from tests.external.support.manifest import ManifestEntry, mark_current_entry_created
from tests.external.support.scenario import wait_for_control, write_checkpoint


pytestmark = pytest.mark.skipif(
    os.getenv("VIRTY_INFRA_SCENARIO", "happy") != "worker-stop",
    reason="worker-stop scenarioだけで実行します",
)


def test_running_task_becomes_lost_after_worker_restart(
    env,
    client,
    created_network,
    created_storage,
    vm_images,
) -> None:
    server = env.servers[0]
    vm = env.vms[0]
    cloud_name = next(
        storage.name for storage in env.storages if storage.name.endswith("test-cloud")
    )
    image_pool_name = next(
        storage.name for storage in env.storages if storage.name.endswith("test-img")
    )
    cloud_page = StoragePage.model_validate(
        client.get(
            "/api/storages",
            params={"nameLike": cloud_name, "nodeName": server.name},
        ).json()
    )
    image_page = StoragePage.model_validate(
        client.get(
            "/api/storages",
            params={"nameLike": image_pool_name, "nodeName": server.name},
        ).json()
    )
    network_page = NetworkPage.model_validate(
        client.get(
            "/api/networks",
            params={"nameLike": vm.network, "nodeNameLike": server.name},
        ).json()
    )
    assert len(cloud_page.data) == len(image_page.data) == len(network_page.data) == 1
    image_name = urlparse(env.image_url).path.rsplit("/", 1)[-1]
    request = DomainForCreate(
        type="manual",
        name=vm_resource_name(vm.name, server.name),
        node_name=server.name,
        memory_mega_byte=4096,
        cpu=4,
        disks=[
            DomainForCreateDisk(
                type="copy",
                size_giga_byte=64,
                save_pool_uuid=image_page.data[0].uuid,
                original_pool_uuid=cloud_page.data[0].uuid,
                original_name=image_name,
            )
        ],
        interface=[
            DomainForCreateInterface(
                type="network",
                network_uuid=network_page.data[0].uuid,
            )
        ],
        cloud_init=None,
    )
    queued = client.post(
        "/api/tasks/vms",
        content=request.model_dump_json(by_alias=True),
    )
    queued.raise_for_status()
    try:
        task_uuid = str(UUID(queued.json()[0]["uuid"]))
    except (KeyError, IndexError, TypeError, ValueError):
        pytest.fail("worker-stop enqueue identityが不正です")
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        task_response = client.get(f"/api/tasks/{task_uuid}")
        task_response.raise_for_status()
        status = task_response.json()["status"]
        if status == "start":
            break
        if status in {"finish", "error", "lost"}:
            pytest.fail("worker-stop対象taskが停止checkpoint前に終了しました")
        time.sleep(0.1)
    else:
        pytest.fail("worker-stop対象taskがstartへ遷移しませんでした")

    write_checkpoint("worker-task-started")
    wait_for_control("worker-restarted", timeout_seconds=120)

    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        task_response = client.get(f"/api/tasks/{task_uuid}")
        task_response.raise_for_status()
        if task_response.json()["status"] == "lost":
            reload_vms(env, client)
            vm_name = vm_resource_name(vm.name, server.name)
            inventory_response = client.get(
                "/api/vms",
                params={
                    "nameLike": vm_name,
                    "nodeNameLike": server.name,
                    "admin": True,
                },
            )
            inventory_response.raise_for_status()
            exact = _exact_vms(
                DomainPage.model_validate(inventory_response.json()),
                vm_name,
                server.name,
            )
            if len(exact) > 1:
                pytest.fail(
                    "worker-stop VM inventoryが不正です: count="
                    f"{len(exact)}"
                )
            if exact:
                mark_current_entry_created(
                    env,
                    ManifestEntry(kind="vm", node=server.name, name=vm_name),
                    resource_uuid=str(exact[0].uuid),
                )
            write_checkpoint("worker-lost-observed")
            return
        time.sleep(0.2)
    pytest.fail("worker再起動後にtaskがlostへ遷移しませんでした")
