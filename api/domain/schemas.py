from enum import Enum
from typing import Any, Dict, List, Literal

from mixin.schemas import BaseSchema, GetPagination
from node.schemas import Node


class DomainDrive(BaseSchema):
    device: str | None = None
    type: str | None = None
    source: str | None = None
    target: str | None = None


class DomainInterface(BaseSchema):
    type: str  | None = None
    mac: str  | None = None
    target: str  | None = None
    bridge: str  | None = None
    network: str  | None = None
    port: str  | None = None


class DomainProject(BaseSchema):
    id: str
    name: str



class DomainStatus(int, Enum):
    POWER_ON = 1
    POWER_OFF = 5
    MAINTENANCE_MODE = 7
    DELETED_DOMAIN = 10
    LOST_NODE = 20

    @classmethod
    def __modify_schema__(cls, schema: Dict[str, Any]):
        schema["x-enum-varnames"] = [choice.name for choice in cls]


class Domain(BaseSchema):
    uuid: str
    name: str
    core: int
    memory: int
    status: int # TODO: DomainStatusに置き換える
    description: str  | None = None
    node_name: str
    owner_user_id: str  | None = None
    owner_project_id: str  | None = None
    owner_project: DomainProject  | None = None
    vnc_port: int  | None = None
    vnc_password: str  | None = None
    drives: list[DomainDrive] | None  | None = None
    interfaces: list[DomainInterface] | None  | None = None


class DomainForQuery(GetPagination):
    name_like: str  | None = None
    node_name_like: str  | None = None


class DomainPage(BaseSchema):
    count: int
    data: List[Domain]


class DomainDetail(Domain):
    node: Node


class DomainXML(BaseSchema):
    xml: str

class DomainBase(BaseSchema):
    uuid: str


class DomainPatchUser(BaseSchema):
    uuid: str
    user_id: str


class DomainPatchName(BaseSchema):
    uuid: str
    name: str


class DomainPatchCore(BaseSchema):
    uuid: str
    core: int


class DomainProjectForUpdate(BaseSchema):
    uuid: str
    project_id: str


class DomainForDelete(DomainBase):
    pass


class DomainPatch(DomainBase):
    status: str  | None = None
    path: str  | None = None
    target: str  | None = None


class DomainPowerStatus(str, Enum):
    ON = "on"
    OFF = "off"


class PowerStatusForUpdateDomain(BaseSchema):
    status: str  | None = None # TODO: DomainPowerStatusに置き換える


class CdromForUpdateDomain(BaseSchema):
    path: str  | None = None
    target: str


class DomainDetailXmlInterface(BaseSchema):
    type: str
    mac: str
    target: str  | None = None
    bridge: str  | None = None
    network: str  | None = None
    port: str  | None = None


class DomainDetailXmlDrive(BaseSchema):
    device: str
    type: str
    source: str  | None = None
    target: str  | None = None


class DomainDetailXml(BaseSchema):
    name:str
    memory: int
    memoryUnit: str
    vcpu: int
    uuid: str
    vnc_port: int  | None = None
    disk: List[DomainDetailXmlDrive]
    interface: List[DomainDetailXmlInterface]
    boot: List[str]
    selinux: bool


class DomainDetailSelect(BaseSchema):
    db: Domain
    node: Node
    xml: DomainDetailXml
    token: str


class DomainForCreateDisk(BaseSchema):
    type: str
    save_pool_uuid: str
    original_pool_uuid: str  | None = None
    original_name: str  | None = None
    size_giga_byte: int  | None = None
    template_name: str  | None = None


class DomainForCreateInterface(BaseSchema):
    type: str
    mac: str  | None = None
    network_uuid: str
    port: str  | None = None


class CloudInitInsert(BaseSchema):
    hostname: str
    userData: str


class DomainForCreate(BaseSchema):
    type: Literal['manual', 'project']
    name: str
    node_name: str
    memory_mega_byte: int
    cpu: int
    disks: List[DomainForCreateDisk]
    interface: List[DomainForCreateInterface]
    cloud_init: CloudInitInsert  | None = None


class NetworkForUpdateDomain(BaseSchema):
    mac: str
    network_uuid: str
    port: str  | None = None


class InterfaceForDomainTicket(BaseSchema):
    id: int
    mac: str  | None = None


class DomainInProjectForCreate(BaseSchema):
    project_id: str
    name: str
    memory: int
    core: int
    flavor_id: int
    flavor_size_g: int
    storage_pool_id: int
    interfaces: list[InterfaceForDomainTicket]
    cloud_init: CloudInitInsert  | None = None
