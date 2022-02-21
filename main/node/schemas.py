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


class NodeSelect(NodeInsert):
    core: int
    memory: int
    cpu_gen: str
    os_like: str
    os_name: str
    os_version: str
    status: int
    qemu_version: str
    libvirt_version: str
    roles: List[Any]
    class Config:
        orm_mode  =  True

class NodeRolePatch(CamelModel):
    node_name: str
    role_name: str