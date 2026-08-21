
import pytest
from fastapi.testclient import TestClient

from network.schemas import (
    NetworkDHCPForCreate,
    NetworkForCreate,
    NetworkIPForCreate,
    NetworkPage,
)
from tests.external.conftest import EnvConfig, wait_tasks


def _exact_networks(page: NetworkPage, name: str, node_name: str):
    return [
        network
        for network in page.data
        if network.name == name and network.node_name == node_name
    ]


@pytest.fixture(scope="function")
def created_network(env, client, nodes):
    create_network(env, client)

    res = client.get("/api/networks")
    try:
        yield NetworkPage.model_validate(res.json())
    finally:
        delete_network(env, client, skipp=True)


@pytest.fixture(scope="function")
def deleted_network(env, client, nodes):
    delete_network(env, client, skipp=True)

    res = client.get("/api/networks")
    try:
        yield NetworkPage.model_validate(res.json())
    finally:
        delete_network(env, client, skipp=True)


def create_network(env: EnvConfig, client: TestClient):
    reload_networks(env, client)
    
    for server in env.servers:
        for network in env.networks:  
            # すでにあるか判定
            res_network = client.get("/api/networks", params={"nameLike": network.name, "nodeNameLike": server.name})
            page = NetworkPage.model_validate(res_network.json())
            exact_networks = _exact_networks(page, network.name, server.name)
            assert not exact_networks, (
                f"既存networkは再利用できません: {server.name}/{network.name}"
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
            
            
def delete_network(env: EnvConfig, client: TestClient, skipp=False):
    reload_networks(env, client)
    for server in env.servers:
        for network in env.networks:  
            res_network = client.get("/api/networks", params={"nameLike": network.name, "nodeNameLike": server.name})
            
            page = NetworkPage.model_validate(res_network.json())
            exact_networks = _exact_networks(page, network.name, server.name)
            if not exact_networks and skipp:
                continue    
            
            assert len(exact_networks) == 1
            pool_uuid = exact_networks[0].uuid
            
            res = client.delete(f'/api/tasks/networks/{pool_uuid}')
            
            assert res.status_code == 200
            assert wait_tasks(res, client) == "finish"
    reload_networks(env, client)
            
            
def reload_networks(env: EnvConfig, client: TestClient):
    put_network = client.put("/api/tasks/networks", params={})
    wait_tasks(put_network, client)
