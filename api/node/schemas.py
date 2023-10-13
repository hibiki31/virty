from fastapi_camelcase import CamelModel
from pydantic import BaseModel, Field
from typing import List, Optional, Any

# Model schemas
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


# API schemas
class NodeRoleForUpdate(CamelModel):
    node_name: str
    role_name: str
    extra_json: dict = None


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