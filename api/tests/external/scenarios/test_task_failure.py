import os
import time
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
from tests.external.fixtures.vm import _exact_vms, vm_resource_name
from tests.external.support.remote_inventory import (
    assert_libvirt_absent,
    remote_inventory_manager,
)
from tests.external.support.scenario import write_checkpoint
from tests.external.support.task_poller import (
    TERMINAL_FAILURES,
    TaskPollingError,
    TaskSnapshot,
    wait_for_tasks,
)


pytestmark = pytest.mark.skipif(
    os.getenv("VIRTY_INFRA_SCENARIO", "happy") != "task-failure",
    reason="task-failure scenarioだけで実行します",
)


def test_vm_copy_failure_blocks_dependent_backends_and_is_cleanup_safe(
    env,
    client,
    created_network,
    created_storage,
) -> None:
    cloud_name = next(
        storage.name for storage in env.storages if storage.name.endswith("test-cloud")
    )
    image_name = next(
        storage.name for storage in env.storages if storage.name.endswith("test-img")
    )
    server = env.servers[0]
    vm = env.vms[0]
    cloud_response = client.get(
        "/api/storages",
        params={"nameLike": cloud_name, "nodeName": server.name},
    )
    image_response = client.get(
        "/api/storages",
        params={"nameLike": image_name, "nodeName": server.name},
    )
    network_response = client.get(
        "/api/networks",
        params={"nameLike": vm.network, "nodeNameLike": server.name},
    )
    cloud_response.raise_for_status()
    image_response.raise_for_status()
    network_response.raise_for_status()
    cloud = [
        storage
        for storage in StoragePage.model_validate(cloud_response.json()).data
        if storage.name == cloud_name and storage.node_name == server.name
    ]
    image = [
        storage
        for storage in StoragePage.model_validate(image_response.json()).data
        if storage.name == image_name and storage.node_name == server.name
    ]
    network = [
        item
        for item in NetworkPage.model_validate(network_response.json()).data
        if item.name == vm.network and item.node_name == server.name
    ]
    assert len(cloud) == len(image) == len(network) == 1
    exact_vm_name = vm_resource_name(vm.name, server.name)
    with remote_inventory_manager(
        user=server.username,
        domain=server.domain,
        server_index=0,
    ) as remote:
        assert_libvirt_absent(
            remote,
            kind="vm",
            name=exact_vm_name,
            resource_uuid=None,
            server_index=0,
        )
    write_checkpoint("resource-created")

    request = DomainForCreate(
        type="manual",
        name=exact_vm_name,
        node_name=server.name,
        memory_mega_byte=4096,
        cpu=4,
        disks=[
            DomainForCreateDisk(
                type="copy",
                size_giga_byte=64,
                save_pool_uuid=image[0].uuid,
                original_pool_uuid=cloud[0].uuid,
                original_name=f"{os.environ['VIRTY_TEST_RUN_ID']}-missing-source.qcow2",
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
    queued = client.post(
        "/api/tasks/vms",
        content=request.model_dump_json(by_alias=True),
    )
    queued.raise_for_status()
    try:
        task_uuids = [str(UUID(item["uuid"])) for item in queued.json()]
    except (KeyError, TypeError, ValueError):
        pytest.fail("task-failure enqueue identityが不正です")
    assert len(task_uuids) == 3
    write_checkpoint("task-queued")

    with pytest.raises(TaskPollingError) as caught:
        wait_for_tasks(queued, client, timeout_seconds=120)

    assert caught.value.snapshots
    assert any(
        snapshot.status in TERMINAL_FAILURES
        and (snapshot.message is not None or snapshot.log is not None)
        for snapshot in caught.value.snapshots.values()
    )

    snapshots: dict[str, TaskSnapshot] = {}
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        for task_uuid in task_uuids:
            task_response = client.get(f"/api/tasks/{task_uuid}")
            task_response.raise_for_status()
            snapshots[task_uuid] = TaskSnapshot.model_validate(task_response.json())
        if all(snapshot.status in TERMINAL_FAILURES for snapshot in snapshots.values()):
            break
        time.sleep(0.2)
    else:
        pytest.fail("dependent taskが有限時間内にfailureへ収束しませんでした")

    parent = snapshots[task_uuids[0]]
    dependents = [snapshots[task_uuid] for task_uuid in task_uuids[1:]]
    assert parent.status == "error"
    assert parent.message is not None or parent.log is not None
    assert all(snapshot.status == "error" for snapshot in dependents)
    assert all(snapshot.message == "depended task faile" for snapshot in dependents)

    inventory_response = client.get(
        "/api/vms",
        params={
            "nameLike": exact_vm_name,
            "nodeNameLike": server.name,
            "admin": True,
        },
    )
    inventory_response.raise_for_status()
    assert not _exact_vms(
        DomainPage.model_validate(inventory_response.json()),
        exact_vm_name,
        server.name,
    )
    with remote_inventory_manager(
        user=server.username,
        domain=server.domain,
        server_index=0,
    ) as remote:
        assert_libvirt_absent(
            remote,
            kind="vm",
            name=exact_vm_name,
            resource_uuid=None,
            server_index=0,
        )
    write_checkpoint("task-failure-observed")
