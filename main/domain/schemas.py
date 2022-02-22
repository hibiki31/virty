from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from fastapi_camelcase import CamelModel

from node.schemas import NodeSelect

class DomainBase(CamelModel):
    uuid: str

class DomainPatchUser(CamelModel):
    uuid: str
    user_id: str

class DomainGroupPatch(CamelModel):
    uuid: str
    group_id: str

class DomainDelete(DomainBase):
    pass

class DomainPatch(DomainBase):
    status: str = None
    path: str = None
    target: str = None

class DomainInsert(DomainBase):
    description: str = None


class DomainSelect(DomainInsert):
    name: str
    core: int
    memory: int
    status: int
    node_name: str
    owner_user_id: str = None
    owner_group_id: str = None
    class Config:
        orm_mode  =  True

class DomainDetailXmlInterface(CamelModel):
    type: str
    mac: str
    target: str
    source: str
    netwrok: str = None
    port: str = None

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

class DomainInsertDisk(CamelModel):
    type: str
    save_pool_uuid: str
    original_pool_uuid: str = None
    original_name: str = None
    size_giga_byte: int = None
    template_name: str = None

class DomainInsertInterface(CamelModel):
    type: str
    mac: str = None
    network_name: str

class CloudInitInsert(CamelModel):
    hostname: str
    userData: str
class DomainInsert(CamelModel):
    name: str
    node_name: str
    memory_mega_byte: int
    cpu: int
    disks: List[DomainInsertDisk]
    interface: List[DomainInsertInterface]
    cloud_init: CloudInitInsert = None

class DomainNetworkChange(CamelModel):
    uuid: str
    mac: str
    network_name: str
    port: str = None