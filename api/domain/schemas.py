from datetime import datetime
from typing import List, Optional, Any, Literal
from pydantic import BaseModel, Field

from fastapi_camelcase import CamelModel
from pyparsing import str_type

from node.schemas import Node

# Model schemas
class DomainDrive(CamelModel):
    device: str = None
    type: str = None
    source: str = None
    target: str = None
    class Config:
        orm_mode  =  True

class DomainInterface(CamelModel):
    type: str =None
    mac: str = None
    target: str = None
    bridge: str = None
    network: str = None
    port: str = None
    class Config:
        orm_mode  =  True


class DomainProject(CamelModel):
    id: str
    name: str
    class Config:
        orm_mode  =  True


class Domain(CamelModel):
    uuid: str
    name: str
    core: int
    memory: int
    status: int
    description: str = None
    node_name: str
    owner_user_id: str = None
    owner_project_id: str = None
    owner_project: DomainProject = None
    vnc_port: int = None
    vnc_password: str = None
    drives: list[DomainDrive] | None = None
    interfaces: list[DomainInterface] | None = None
    class Config:
        orm_mode  =  True


# API schemas
class DomainPagenation(CamelModel):
    count: int
    data: List[Domain]


class DomainDetail(Domain):
    node: Node


class DomainBase(CamelModel):
    uuid: str
    class Config:
        orm_mode  =  True

class DomainPatchUser(CamelModel):
    uuid: str
    user_id: str

class DomainPatchName(CamelModel):
    uuid: str
    name: str

class DomainPatchCore(CamelModel):
    uuid: str
    core: int

class DomainProjectPatch(CamelModel):
    uuid: str
    project_id: str

class DomainDelete(DomainBase):
    pass

class DomainPatch(DomainBase):
    status: str = None
    path: str = None
    target: str = None


class PatchDomainPower(CamelModel):
    status: str = None


class PatchDominCdrom(CamelModel):
    path: str = None
    target: str = None


class DomainDetailXmlInterface(CamelModel):
    type: str
    mac: str
    target: str = None
    bridge: str = None
    network: str = None
    port: str = None

class DomainDetailXmlDrive(CamelModel):
    device: str
    type: str
    source: str = None
    target: str = None

class DomainDetailXml(CamelModel):
    name:str
    memory: int
    memoryUnit: str
    vcpu: int
    uuid: str
    vnc_port: int = None
    disk: List[DomainDetailXmlDrive]
    interface: List[DomainDetailXmlInterface]
    boot: List[str]
    selinux: bool

class DomainDetailSelect(CamelModel):
    db: Domain
    node: Node
    xml: DomainDetailXml
    token: str
    class Config:
        orm_mode  =  True

class DomainInsertDisk(CamelModel):
    type: str
    save_pool_uuid: str
    original_pool_uuid: str = None
    original_name: str = None
    size_giga_byte: int = None
    template_name: str = None
    class Config:
        orm_mode  =  True

class DomainInsertInterface(CamelModel):
    type: str
    mac: str = None
    network_uuid: str
    port: str = None
    class Config:
        orm_mode  =  True

class CloudInitInsert(CamelModel):
    hostname: str
    userData: str

class DomainInsert(CamelModel):
    type: Literal['manual', 'project']
    name: str
    node_name: str
    memory_mega_byte: int
    cpu: int
    disks: List[DomainInsertDisk]
    interface: List[DomainInsertInterface]
    cloud_init: CloudInitInsert = None
    class Config:
        orm_mode  =  True

class DomainNetworkChange(CamelModel):
    mac: str
    network_uuid: str
    port: str = None


class PostDomainTicketInterface(CamelModel):
    id: int
    mac: str = None


class PostDomainTicket(CamelModel):
    type: str
    issuance_id: int
    name: str
    memory: int
    core: int
    flavor_id: int
    flavor_size_g: int
    storage_pool_id: int
    interfaces: list[PostDomainTicketInterface]
    cloud_init: CloudInitInsert = None
    class Config:
        orm_mode  =  True
