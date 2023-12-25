from typing import List, Literal

from fastapi_camelcase import CamelModel
from pydantic import Field

from mixin.schemas import GetPagination


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


class Network(PaseNetwork):
    node_name: str
    description: str = None
    update_token: str = None
    class Config:
        orm_mode  =  True


class NetworkForQuery(GetPagination):
    name_like: str = None
    node_name_like: str = None
    type: str = None


class NetworkPage(CamelModel):
    count: int
    data: List[Network]
    
    class Config:
        orm_mode  =  True

class NetworkForCreate(CamelModel):
    name: str
    node_name: str
    type: Literal['bridge', 'ovs'] = Field( description='brdige or ovs')
    bridge_device: str = None
    class Config:
        orm_mode  =  True

class NetworkForDelete(CamelModel):
    uuid: str

class NetworkOVSForCreate(CamelModel):
    default: bool
    name: str
    vlan_id: int = None
    class Config:
        orm_mode  =  True


class NetworkProviderForCreate(CamelModel):
    name: str = None
    dns_domain: str = None
    network_address: str = None
    network_prefix: str = None
    gateway_address: str = None
    dhcp_start: str = None
    dhcp_end: str = None
    network_node: str = None
    

    class Config:
        orm_mode  =  True


class NetworkOVSForDelete(CamelModel):
    uuid: str
    name: str
    class Config:
        orm_mode  =  True


class NetworkPoolForCreate(CamelModel):
    name: str


class NetworkPoolForUpdate(CamelModel):
    pool_id: int
    network_uuid: str
    port_name:str = None


class NetworkForNetworkPool(CamelModel):
    name: str
    uuid: str
    node_name: str
    bridge: str
    type: str
    class Config:
        orm_mode  =  True


class NetworkPoolPort(CamelModel):
    name: str= None
    vlan_id: int = None
    network: NetworkForNetworkPool
    class Config:
        orm_mode  =  True


class NetworkPool(CamelModel):
    id: int = None
    name: str = None
    networks: List[NetworkForNetworkPool] = None
    ports: List[NetworkPoolPort] = None
    class Config:
        orm_mode  =  True

class PostVXLANInternal(CamelModel):
    project_id: str