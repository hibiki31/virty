from pprint import pprint

import pytest
from fastapi.testclient import TestClient

from network.schemas import NetworkForCreate, NetworkNatForCreate, NetworkPage
from tests.conftest import EnvConfig, wait_tasks


@pytest.fixture(scope="function")
def created_network(env, client, nodes):
    create_network(env, client, skipp=True)

    res = client.get("/api/networks")
    yield  NetworkPage.model_validate(res.json())


@pytest.fixture(scope="function")
def deleted_network(env, client, nodes):
    delete_network(env, client, skipp=True)

    res = client.get("/api/networks")
    yield  NetworkPage.model_validate(res.json())


def create_network(env: EnvConfig, client: TestClient, skipp=False):
    reload_networks(env, client)
    
    for server in env.servers:
        req_data = NetworkForCreate(
            name="test-nat",
            node_name=server.name,
            type="nat",
            nat=NetworkNatForCreate(
                bridge_name=None,
                address="192.168.19.254",
                netmask="255.255.255.0",
                dhcp_start="192.168.19.1",
                dhcp_end="192.168.19.200"
            ),
            bridge_device=None
        )
        
        
        # すでにあるか判定
        res_network = client.get("/api/networks", params={"nameLike": "test-nat", "nodeName": server.name})
        page = NetworkPage.model_validate(res_network.json())
        if skipp and page.count == 1:
            continue
        
        res = client.post("/api/tasks/networks", content=req_data.model_dump_json(by_alias=True))
        pprint(res.json())
        assert res.status_code == 200
        assert wait_tasks(res, client) == "finish"
    
    reload_networks(env, client)
            
            
def delete_network(env: EnvConfig, client: TestClient, skipp=False):
    reload_networks(env, client)
    for server in env.servers:
        for network in env.networks:  
            res_network = client.get("/api/networks", params={"nameLike": network.name, "nodeName": server.name})
            
            page = NetworkPage.model_validate(res_network.json())
            if page.count == 0 and skipp:
                continue    
            
            assert page.count == 1
            pool_uuid = page.data[0].uuid
            
            res = client.delete(f'/api/tasks/networks/{pool_uuid}')
            
            assert res.status_code == 200
            assert wait_tasks(res, client) == "finish"
    reload_networks(env, client)
            
            
def reload_networks(env: EnvConfig, client: TestClient):
    put_network = client.put("/api/tasks/networks", params={})
    wait_tasks(put_network, client)