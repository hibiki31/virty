from typing import List, Literal

from pydantic.networks import IPvAnyAddress

from mixin.schemas import BaseSchema, GetPagination


class PaseNetworkPortgroup(BaseSchema):
    name: str
    vlan_id: str | None = None
    is_default: bool
    


class NetworkPortgroup(PaseNetworkPortgroup):
    pass


class PaseNetwork(BaseSchema):
    name: str
    uuid: str
    type: str
    dhcp: bool | None = None
    description: str | None = None
    active: bool | None = None
    bridge: str | None = None
    auto_start: bool | None = None
    portgroups: List[NetworkPortgroup]
    


class Network(PaseNetwork):
    node_name: str
    description: str | None = None
    update_token: str | None = None
    


class NetworkForQuery(GetPagination):
    name_like: str | None = None
    node_name_like: str | None = None
    type: str | None = None


class NetworkPage(BaseSchema):
    count: int
    data: List[Network]

class NetworkDHCPForCreate(BaseSchema):
    start: IPvAnyAddress
    end: IPvAnyAddress

class NetworkIPForCreate(BaseSchema):
    address: IPvAnyAddress
    netmask: IPvAnyAddress

class NetworkForCreate(BaseSchema):
    name: str
    node_name: str
    title: str | None = None
    description: str | None = None
    forward_mode: Literal[ 'bridge', 'ovs', 'nat', 'route', 'isorated']
    bridge_name: str | None = None
    dhcp: NetworkDHCPForCreate | None = None
    ip: NetworkIPForCreate | None = None
    

class NetworkForDelete(BaseSchema):
    uuid: str
    


class NetworkOVSForCreate(BaseSchema):
    default: bool
    name: str
    vlan_id: int | None = None
    


class NetworkProviderForCreate(BaseSchema):
    name: str | None = None
    dns_domain: str | None = None
    network_address: str | None = None
    network_prefix: str | None = None
    gateway_address: str | None = None
    dhcp_start: str | None = None
    dhcp_end: str | None = None
    network_node: str | None = None
    

class NetworkXML(BaseSchema):
    xml: str 


class NetworkOVSForDelete(BaseSchema):
    uuid: str
    name: str
    


class NetworkPoolForCreate(BaseSchema):
    name: str


class NetworkPoolForUpdate(BaseSchema):
    pool_id: int
    network_uuid: str
    port_name:str | None = None


class NetworkForNetworkPool(BaseSchema):
    name: str
    uuid: str
    node_name: str
    bridge: str
    type: str
    


class NetworkPoolPort(BaseSchema):
    name: str= None
    vlan_id: int | None = None
    network: NetworkForNetworkPool
    


class NetworkPool(BaseSchema):
    id: int | None = None
    name: str | None = None
    networks: List[NetworkForNetworkPool] | None = None
    ports: List[NetworkPoolPort] | None = None
    

class PostVXLANInternal(BaseSchema):
    project_id: str