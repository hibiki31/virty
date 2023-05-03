from datetime import datetime
from typing import Any, List, Literal
import uuid
from pydantic import BaseModel, Field

from fastapi_camelcase import CamelModel


class PaseNetworkPortgroup(CamelModel):
    name: str
    vlan_id: str = None
    is_default: bool
    class Config:
        orm_mode  =  True


class NetworkPortgroup(PaseNetworkPortgroup):
    pass


class PaseNetwork(CamelModel):
    name: str
    uuid: str
    type: str
    dhcp: bool = None
    description: str = None
    active: bool = None
    bridge: str = None
    auto_start: bool = None
    portgroups: List[NetworkPortgroup]
    class Config:
        orm_mode  =  True


class GetNetwork(PaseNetwork):
    node_name: str
    description: str = None
    update_token: str = None
    class Config:
        orm_mode  =  True


class NetworkInsert(CamelModel):
    name: str
    node_name: str
    type: Literal['bridge', 'ovs'] = Field( description='brdige or ovs')
    bridge_device: str = None
    class Config:
        orm_mode  =  True

class NetworkDelete(CamelModel):
    uuid: str

class NetworkOVSAdd(CamelModel):
    default: bool
    name: str
    vlan_id: int = None
    class Config:
        orm_mode  =  True

class NetworkOVSDelete(CamelModel):
    uuid: str
    name: str
    class Config:
        orm_mode  =  True


class PostNetworkPool(CamelModel):
    name: str


class PatchNetworkPool(CamelModel):
    pool_id: int
    network_uuid: str
    port_name:str = None


class GetNEtworkPoolNetworksNetwork(CamelModel):
    name: str
    uuid: str
    node_name: str
    bridge: str
    type: str
    class Config:
        orm_mode  =  True


class GetNetworkPoolPort(CamelModel):
    name: str= None
    vlan_id: int = None
    network: GetNEtworkPoolNetworksNetwork
    class Config:
        orm_mode  =  True


class GetNetworkPool(CamelModel):
    id: int = None
    name: str = None
    networks: List[GetNEtworkPoolNetworksNetwork] = None
    ports: List[GetNetworkPoolPort] = None
    class Config:
        orm_mode  =  True

class PostVXLANInternal(CamelModel):
    project_id: str