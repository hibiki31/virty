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
    bridge_device: str
    class Config:
        orm_mode  =  True

class NetworkDelete(CamelModel):
    uuid: str