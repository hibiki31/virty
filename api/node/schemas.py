from typing import List

from mixin.schemas import GetPagination, BaseSchema


class NodeRole(BaseSchema):
    role_name: str
    extra_json: dict | None = None
    


class Node(BaseSchema):
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
    qemu_version: str | None = None
    libvirt_version: str | None = None
    roles: List[NodeRole]
    


class NodePage(BaseSchema):
    count: int
    data: List[Node]


class NodeForQuery(GetPagination):
    name_like: str | None = None


class NodeRoleForUpdate(BaseSchema):
    node_name: str
    role_name: str
    extra_json: dict | None = None


class NodeInterfaceIpv4Info(BaseSchema):
    address: str
    prefixlen: int
    label: str


class NodeInterfaceIpv6Info(BaseSchema):
    address: str
    prefixlen: int


class NodeInterface(BaseSchema):
    ifname: str
    operstate: str
    mtu: int
    master: str | None = None
    link_type: str
    mac_address: str | None = None
    ipv4_info: List[NodeInterfaceIpv4Info]
    ipv6_info: List[NodeInterfaceIpv6Info]


class SSHKeyPair(BaseSchema):
    private_key: str
    public_key: str


class NodeBase(BaseSchema):
    name: str


class NodeForDelete(NodeBase):
    pass


class NodeForCreate(NodeBase):
    description: str
    domain: str
    user_name: str
    port: int
    libvirt_role: bool


class NodePoolForUpdate(BaseSchema):
    pool_id:int
    node_name:str
    core: int
