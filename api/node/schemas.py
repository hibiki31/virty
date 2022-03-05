from fastapi_camelcase import CamelModel
from pydantic import BaseModel
from typing import List, Optional, Any


class NodeBase(CamelModel):
    name: str


class NodeDelete(NodeBase):
    pass


class NodeInsert(NodeBase):
    description: str
    domain: str
    user_name: str
    port: int
    libvirt_role: bool


class NodeSelect(CamelModel):
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
    roles: List[Any]
    class Config:
        orm_mode  =  True

class NodeRolePatch(CamelModel):
    node_name: str
    role_name: str