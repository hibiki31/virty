from enum import Enum
from typing import Any, Dict, List, Literal

from fastapi_camelcase import CamelModel

from mixin.schemas import GetPagination
from node.schemas import Node


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


class DomainStatus(int, Enum):
    POWER_ON = 1
    POWER_OFF = 5
    MAINTENANCE_MODE = 7
    DELETED_DOMAIN = 10
    LOST_NODE = 20

    @classmethod
    def __modify_schema__(cls, schema: Dict[str, Any]):
        schema["x-enum-varnames"] = [choice.name for choice in cls]


class Domain(CamelModel):
    uuid: str
    name: str
    core: int
    memory: int
    status: int # TODO: DomainStatusに置き換える
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


class DomainForQuery(GetPagination):
    name_like: str = None
    node_name_like: str = None


class DomainPage(CamelModel):
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

class DomainProjectForUpdate(CamelModel):
    uuid: str
    project_id: str

class DomainForDelete(DomainBase):
    pass

class DomainPatch(DomainBase):
    status: str = None
    path: str = None
    target: str = None

class DomainPowerStatus(str, Enum):
    ON = "on"
    OFF = "off"

class PowerStatusForUpdateDomain(CamelModel):
    status: str = None # TODO: DomainPowerStatusに置き換える


class CdromForUpdateDomain(CamelModel):
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

class DomainForCreateDisk(CamelModel):
    type: str
    save_pool_uuid: str
    original_pool_uuid: str = None
    original_name: str = None
    size_giga_byte: int = None
    template_name: str = None
    class Config:
        orm_mode  =  True

class DomainForCreateInterface(CamelModel):
    type: str
    mac: str = None
    network_uuid: str
    port: str = None
    class Config:
        orm_mode  =  True

class CloudInitInsert(CamelModel):
    hostname: str
    userData: str

class DomainForCreate(CamelModel):
    type: Literal['manual', 'project']
    name: str
    node_name: str
    memory_mega_byte: int
    cpu: int
    disks: List[DomainForCreateDisk]
    interface: List[DomainForCreateInterface]
    cloud_init: CloudInitInsert = None
    class Config:
        orm_mode  =  True

class NetworkForUpdateDomain(CamelModel):
    mac: str
    network_uuid: str
    port: str = None


class InterfaceForDomainTicket(CamelModel):
    id: int
    mac: str = None


class DomainInProjectForCreate(CamelModel):
    project_id: str
    name: str
    memory: int
    core: int
    flavor_id: int
    flavor_size_g: int
    storage_pool_id: int
    interfaces: list[InterfaceForDomainTicket]
    cloud_init: CloudInitInsert = None
    class Config:
        orm_mode  =  True
