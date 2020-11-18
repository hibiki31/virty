from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from fastapi_camelcase import CamelModel

from node.schemas import NodeSelect

class DomainBase(CamelModel):
    uuid: str


class DomainDelete(DomainBase):
    pass


class DomainInsert(DomainBase):
    description: str = None


class DomainSelect(DomainInsert):
    name: str
    core: int
    memory: int
    status: int
    user_id: str = None
    group_id: str = None
    class Config:
        orm_mode  =  True

class DomainDetailXmlInterface(CamelModel):
    type: str
    mac: str
    target: str
    source: str
    netwrok: str = None

class DomainDetailXmlDrive(CamelModel):
    device: str
    type: str
    file: str = None
    target: str

class DomainDetailXml(CamelModel):
    name:str
    memory: int
    vcpu: int
    uuid: str
    vnc_port: int = None
    disk: List[DomainDetailXmlDrive]
    interface: List[DomainDetailXmlInterface]
    boot: List[list]
    selinux: bool

class DomainDetailSelect(CamelModel):
    db: DomainSelect
    node: NodeSelect
    xml: DomainDetailXml
    class Config:
        orm_mode  =  True