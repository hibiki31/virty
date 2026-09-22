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
    project_id: str | None = None


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
    forward_mode: Literal["bridge", "ovs", "nat", "route", "isolated"]
    bridge_name: str | None = None
    dhcp: NetworkDHCPForCreate | None = None
    ip: NetworkIPForCreate | None = None
    

class NetworkForDelete(BaseSchema):
    uuid: str
    


class NetworkOVSForCreate(BaseSchema):
    default: bool
    name: str
    vlan_id: int | None = None
    


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


class NetworkPoolPortSelection(BaseSchema):
    network_uuid: str
    port_name: str


class NetworkPoolForReplace(BaseSchema):
    network_uuids: list[str]
    ports: list[NetworkPoolPortSelection]


class NetworkForNetworkPool(BaseSchema):
    name: str
    uuid: str
    node_name: str
    bridge: str
    type: str
    


class NetworkPoolPort(BaseSchema):
    name: str = None  # type: ignore[assignment]
    vlan_id: int | None = None
    network: NetworkForNetworkPool
    


class NetworkPool(BaseSchema):
    id: int
    name: str | None
    networks: List[NetworkForNetworkPool]
    ports: List[NetworkPoolPort]


class NetworkPoolDeleteResponse(BaseSchema):
    deleted: Literal[True]
    id: int
