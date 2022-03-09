from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from fastapi_camelcase import CamelModel


class PostNetworkPool(CamelModel):
    name: str

class PatchNetworkPool(CamelModel):
    pool_id: int
    network_uuid: str
    port_name: str

class PaseNetworkPortgroup(CamelModel):
    name: str
    vlan_id: str = None
    is_default: bool
    class Config:
        orm_mode  =  True


class PaseNetwork(CamelModel):
    name: str
    uuid: str
    type: str
    dhcp: bool = None
    description: str = None
    active: bool = None
    bridge: str = None
    auto_start: bool = None
    portgroups: List[PaseNetworkPortgroup]
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
    type: str
    bridge_device: str = None
    class Config:
        orm_mode  =  True

class NetworkDelete(CamelModel):
    uuid: str

class NetworkOVSAdd(CamelModel):
    default: bool
    uuid: str
    name: str
    vlan_id: int = None
    class Config:
        orm_mode  =  True

class NetworkOVSDelete(CamelModel):
    uuid: str
    name: str
    class Config:
        orm_mode  =  True