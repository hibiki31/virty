from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from fastapi_camelcase import CamelModel


class NetworkSelect(CamelModel):
    name: str
    uuid: str
    node_name: str
    type: str
    dhcp: bool = None
    description: str = None
    active: bool = None
    host_interface: str = None
    auto_start: bool = None
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