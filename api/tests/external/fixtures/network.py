
import pytest
from fastapi.testclient import TestClient

from network.schemas import (
    NetworkDHCPForCreate,
    NetworkForCreate,
    NetworkIPForCreate,
    NetworkPage,
)
from tests.external.conftest import EnvConfig, wait_tasks
from tests.external.support.manifest import ManifestEntry, mark_current_entry_created
from tests.external.support.remote_inventory import (
    assert_libvirt_present,
    network_xml,
    remote_inventory_manager,
)


def _exact_networks(page: NetworkPage, name: str, node_name: str):
    return [
        network
        for network in page.data
        if network.name == name and network.node_name == node_name
    ]


@pytest.fixture(scope="session")
def created_network(env, client, nodes):
    create_network(env, client)
    response = client.get("/api/networks")
    response.raise_for_status()
    return NetworkPage.model_validate(response.json())


def create_network(env: EnvConfig, client: TestClient):
    reload_networks(env, client)
    for server_index, server in enumerate(env.servers):
        for network in env.networks:
            # すでにあるか判定
            res_network = client.get("/api/networks", params={"nameLike": network.name, "nodeNameLike": server.name})
            page = NetworkPage.model_validate(res_network.json())
            exact_networks = _exact_networks(page, network.name, server.name)
            if exact_networks:
                raise AssertionError(
                    "network API collision precondition failed: "
                    f"server_index={server_index} count={len(exact_networks)}"
                )
            req_data = NetworkForCreate(
                name=network.name,
                node_name=server.name,
                forward_mode=network.type,
                ip=NetworkIPForCreate(address=f"10.144.{int(network.octet)}.254", netmask="255.255.255.0"),
                dhcp=NetworkDHCPForCreate(start=f"10.144.{int(network.octet)}.1", end=f"10.144.{int(network.octet)}.200"),
                bridge_name=None
            )
            res = client.post("/api/tasks/networks", content=req_data.model_dump_json(by_alias=True))

            assert res.status_code == 200
            assert wait_tasks(res, client) == "finish"
    
    reload_networks(env, client)
    for server_index, server in enumerate(env.servers):
        with remote_inventory_manager(
            user=server.username,
            domain=server.domain,
            server_index=server_index,
        ) as remote:
            for network in env.networks:
                response = client.get(
                    "/api/networks",
                    params={"nameLike": network.name, "nodeNameLike": server.name},
                )
                response.raise_for_status()
                exact = _exact_networks(
                    NetworkPage.model_validate(response.json()),
                    network.name,
                    server.name,
                )
                if len(exact) != 1:
                    raise AssertionError(
                        "network API postcondition failed: "
                        f"server_index={server_index} count={len(exact)}"
                    )
                if (
                    exact[0].type != "nat"
                    or exact[0].dhcp is not True
                    or exact[0].active is not True
                    or exact[0].auto_start is not True
                ):
                    raise AssertionError(
                        "network API state postcondition failed: "
                        f"server_index={server_index} count=1"
                    )
                resource_uuid = str(exact[0].uuid)
                assert_libvirt_present(
                    remote,
                    kind="network",
                    name=network.name,
                    resource_uuid=resource_uuid,
                    server_index=server_index,
                )
                xml = network_xml(
                    remote,
                    resource_uuid=resource_uuid,
                    server_index=server_index,
                )
                forward = xml.find("forward")
                ip = xml.find("ip")
                dhcp_range = ip.find("./dhcp/range") if ip is not None else None
                if (
                    forward is None
                    or forward.get("mode") != "nat"
                    or ip is None
                    or ip.get("address") != f"10.144.{int(network.octet)}.254"
                    or ip.get("netmask") != "255.255.255.0"
                    or dhcp_range is None
                    or dhcp_range.get("start")
                    != f"10.144.{int(network.octet)}.1"
                    or dhcp_range.get("end")
                    != f"10.144.{int(network.octet)}.200"
                ):
                    raise AssertionError(
                        "network XML postcondition failed: "
                        f"server_index={server_index} count=1"
                    )
                mark_current_entry_created(
                    env,
                    ManifestEntry(
                        kind="network",
                        node=server.name,
                        name=network.name,
                    ),
                    resource_uuid=resource_uuid,
                )


def reload_networks(env: EnvConfig, client: TestClient):
    put_network = client.put("/api/tasks/networks", params={})
    wait_tasks(put_network, client)


def delete_network_target(
    client: TestClient,
    *,
    node_name: str,
    network_name: str,
    resource_uuid: str | None,
    skip_absent: bool = True,
) -> str | None:
    response = client.get("/api/networks", params={"limit": 0})
    response.raise_for_status()
    page = NetworkPage.model_validate(response.json())
    exact = _exact_networks(page, network_name, node_name)
    if resource_uuid is not None:
        matching_uuid = [
            network for network in page.data if str(network.uuid) == resource_uuid
        ]
        if any(str(network.uuid) != resource_uuid for network in exact):
            raise RuntimeError("manifest network identity inventory mismatch: count=1")
        exact = matching_uuid
    if not exact and skip_absent:
        return None
    if len(exact) != 1:
        raise RuntimeError(f"network cleanup inventory mismatch: count={len(exact)}")
    deleted_uuid = str(exact[0].uuid)
    task_response = client.delete(f"/api/tasks/networks/{deleted_uuid}")
    task_response.raise_for_status()
    assert wait_tasks(task_response, client) == "finish"
    confirm = client.get("/api/networks", params={"limit": 0})
    confirm.raise_for_status()
    confirm_page = NetworkPage.model_validate(confirm.json())
    remains = _exact_networks(confirm_page, network_name, node_name)
    remains.extend(
        network for network in confirm_page.data if str(network.uuid) == deleted_uuid
    )
    if remains:
        raise RuntimeError(
            f"network cleanup API postcondition failed: count={len(remains)}"
        )
    return deleted_uuid
