from typing import List

from fastapi_camelcase import CamelModel

from mixin.schemas import GetPagination


class NodeRole(CamelModel):
    role_name: str
    extra_json: dict = None
    class Config:
        orm_mode  =  True


class Node(CamelModel):
    name: str
    description: str
    domain: str
    user_name: str
    port: int
    core: int
    memory: int
    cpu_gen: str
    os_like: str
    os_name: str
    os_version: str
    status: int
    qemu_version: str = None
    libvirt_version: str = None
    roles: List[NodeRole]
    class Config:
        orm_mode  =  True


class NodePage(CamelModel):
    count: int
    data: List[Node]


class NodeForQuery(GetPagination):
    name_like: str = None


class NodeRoleForUpdate(CamelModel):
    node_name: str
    role_name: str
    extra_json: dict = None


class NodeInterfaceIpv4Info(CamelModel):
    address: str
    prefixlen: int
    label: str


class NodeInterfaceIpv6Info(CamelModel):
    address: str
    prefixlen: int


class NodeInterface(CamelModel):
    ifname: str
    operstate: str
    mtu: int
    master: str = None
    link_type: str
    mac_address: str = None
    ipv4_info: List[NodeInterfaceIpv4Info]
    ipv6_info: List[NodeInterfaceIpv6Info]


class SSHKeyPair(CamelModel):
    private_key: str
    public_key: str


class NodeBase(CamelModel):
    name: str


class NodeForDelete(NodeBase):
    pass


class NodeForCreate(NodeBase):
    description: str
    domain: str
    user_name: str
    port: int
    libvirt_role: bool


class NodePoolForUpdate(CamelModel):
    pool_id:int
    node_name:str
    core: int
