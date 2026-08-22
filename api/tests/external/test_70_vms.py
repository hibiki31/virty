from urllib.parse import urlparse

from domain.schemas import DomainPage
from network.schemas import NetworkPage
from tests.external.conftest import wait_tasks
from tests.external.fixtures.vm import (
    _exact_vms,
    reload_vms,
    vm_resource_name,
)
from tests.external.support.remote_inventory import (
    domain_state,
    domain_xml,
    remote_inventory_manager,
)


def _read_vm(client, *, name: str, node_name: str, server_index: int):
    response = client.get(
        "/api/vms",
        params={"nameLike": name, "nodeNameLike": node_name, "admin": True},
    )
    response.raise_for_status()
    exact = _exact_vms(DomainPage.model_validate(response.json()), name, node_name)
    if len(exact) != 1:
        raise AssertionError(
            f"VM API inventory failed: server_index={server_index} count={len(exact)}"
        )
    return exact[0]


def test_vm_inventory(env, created_vm) -> None:
    expected = {
        (vm_resource_name(vm.name, server.name), server.name)
        for server in env.servers
        for vm in env.vms
    }
    actual = {
        (vm.name, vm.node_name)
        for vm in created_vm.data
        if (vm.name, vm.node_name) in expected
    }
    if actual != expected:
        raise AssertionError(
            f"VM inventory mismatch: count={len(actual.symmetric_difference(expected))}"
        )


def test_change_power_vm(env, client, created_vm) -> None:
    for server_index, server in enumerate(env.servers):
        with remote_inventory_manager(
            user=server.username,
            domain=server.domain,
            server_index=server_index,
        ) as remote:
            for configured_vm in env.vms:
                name = vm_resource_name(configured_vm.name, server.name)
                vm = _read_vm(
                    client,
                    name=name,
                    node_name=server.name,
                    server_index=server_index,
                )
                powered_on = client.patch(
                    f"/api/tasks/vms/{vm.uuid}/power",
                    json={"status": "on"},
                )
                powered_on.raise_for_status()
                assert wait_tasks(powered_on, client) == "finish"
                reload_vms(env, client)
                on_inventory = _read_vm(
                    client,
                    name=name,
                    node_name=server.name,
                    server_index=server_index,
                )
                if on_inventory.status != 1 or domain_state(
                    remote,
                    resource_uuid=str(vm.uuid),
                    server_index=server_index,
                ) != "running":
                    raise AssertionError(
                        "VM power-on postcondition failed: "
                        f"server_index={server_index} count=1"
                    )

                powered_off = client.patch(
                    f"/api/tasks/vms/{vm.uuid}/power",
                    json={"status": "off"},
                )
                powered_off.raise_for_status()
                assert wait_tasks(powered_off, client) == "finish"
                reload_vms(env, client)
                off_inventory = _read_vm(
                    client,
                    name=name,
                    node_name=server.name,
                    server_index=server_index,
                )
                if off_inventory.status != 5 or domain_state(
                    remote,
                    resource_uuid=str(vm.uuid),
                    server_index=server_index,
                ) != "shut":
                    raise AssertionError(
                        "VM power-off postcondition failed: "
                        f"server_index={server_index} count=1"
                    )


def test_change_vm_cdrom(env, client, created_vm) -> None:
    iso_storage = next(
        item for item in env.storages if item.name.endswith("test-iso")
    )
    iso_name = urlparse(env.iso_url).path.rsplit("/", 1)[-1]
    if not iso_name:
        raise AssertionError("VM CD-ROM precondition failed: count=0")
    iso_path = f"{iso_storage.path}/{iso_name}"

    for server_index, server in enumerate(env.servers):
        with remote_inventory_manager(
            user=server.username,
            domain=server.domain,
            server_index=server_index,
        ) as remote:
            for configured_vm in env.vms:
                vm = _read_vm(
                    client,
                    name=vm_resource_name(configured_vm.name, server.name),
                    node_name=server.name,
                    server_index=server_index,
                )
                inserted = client.patch(
                    f"/api/tasks/vms/{vm.uuid}/cdrom",
                    json={"target": "hda", "path": iso_path},
                )
                inserted.raise_for_status()
                assert wait_tasks(inserted, client) == "finish"
                inserted_xml = domain_xml(
                    remote,
                    resource_uuid=str(vm.uuid),
                    server_index=server_index,
                )
                inserted_cdroms = inserted_xml.findall(
                    "./devices/disk[@device='cdrom']"
                )
                inserted_sources = [
                    disk.find("source")
                    for disk in inserted_cdroms
                    if disk.find("target") is not None
                    and disk.find("target").get("dev") == "hda"
                ]
                if (
                    len(inserted_sources) != 1
                    or inserted_sources[0] is None
                    or inserted_sources[0].get("file") != iso_path
                ):
                    raise AssertionError(
                        "VM CD-ROM insert postcondition failed: "
                        f"server_index={server_index} count={len(inserted_sources)}"
                    )

                ejected = client.patch(
                    f"/api/tasks/vms/{vm.uuid}/cdrom",
                    json={"target": "hda", "path": None},
                )
                ejected.raise_for_status()
                assert wait_tasks(ejected, client) == "finish"
                ejected_xml = domain_xml(
                    remote,
                    resource_uuid=str(vm.uuid),
                    server_index=server_index,
                )
                ejected_cdroms = ejected_xml.findall(
                    "./devices/disk[@device='cdrom']"
                )
                ejected_sources = [
                    disk.find("source")
                    for disk in ejected_cdroms
                    if disk.find("target") is not None
                    and disk.find("target").get("dev") == "hda"
                ]
                if len(ejected_sources) != 1 or (
                    ejected_sources[0] is not None
                    and ejected_sources[0].get("file") not in {None, ""}
                ):
                    raise AssertionError(
                        "VM CD-ROM eject postcondition failed: "
                        f"server_index={server_index} count={len(ejected_sources)}"
                    )


def test_change_vm_network(env, client, created_vm) -> None:
    for server_index, server in enumerate(env.servers):
        with remote_inventory_manager(
            user=server.username,
            domain=server.domain,
            server_index=server_index,
        ) as remote:
            for configured_vm in env.vms:
                network_response = client.get(
                    "/api/networks",
                    params={
                        "nameLike": configured_vm.network,
                        "nodeNameLike": server.name,
                    },
                )
                network_response.raise_for_status()
                exact_networks = [
                    network
                    for network in NetworkPage.model_validate(
                        network_response.json()
                    ).data
                    if network.name == configured_vm.network
                    and network.node_name == server.name
                ]
                if len(exact_networks) != 1:
                    raise AssertionError(
                        "VM network precondition failed: "
                        f"server_index={server_index} count={len(exact_networks)}"
                    )
                name = vm_resource_name(configured_vm.name, server.name)
                vm = _read_vm(
                    client,
                    name=name,
                    node_name=server.name,
                    server_index=server_index,
                )
                interfaces = vm.interfaces or []
                if len(interfaces) != 1 or not interfaces[0].mac:
                    raise AssertionError(
                        "VM network API precondition failed: "
                        f"server_index={server_index} count={len(interfaces)}"
                    )
                patched = client.patch(
                    f"/api/tasks/vms/{vm.uuid}/network",
                    json={
                        "mac": interfaces[0].mac,
                        "networkUuid": exact_networks[0].uuid,
                        "port": None,
                    },
                )
                patched.raise_for_status()
                assert wait_tasks(patched, client) == "finish"
                reload_vms(env, client)
                updated = _read_vm(
                    client,
                    name=name,
                    node_name=server.name,
                    server_index=server_index,
                )
                updated_interfaces = updated.interfaces or []
                xml = domain_xml(
                    remote,
                    resource_uuid=str(vm.uuid),
                    server_index=server_index,
                )
                sources = [
                    interface.find("source")
                    for interface in xml.findall("./devices/interface")
                    if interface.find("mac") is not None
                    and interface.find("mac").get("address") == interfaces[0].mac
                ]
                if (
                    len(updated_interfaces) != 1
                    or updated_interfaces[0].network_uuid
                    != str(exact_networks[0].uuid)
                    or len(sources) != 1
                    or sources[0] is None
                    or sources[0].get("network") != configured_vm.network
                ):
                    raise AssertionError(
                        "VM network postcondition failed: "
                        f"server_index={server_index} count=1"
                    )
