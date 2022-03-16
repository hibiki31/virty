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


class PatchNodePool(CamelModel):
    pool_id:int
    node_name:str
    core: int

class GetNodeRole(CamelModel):
    role_name: str
    extra_json: dict = None
    class Config:
        orm_mode  =  True

class GetNode(CamelModel):
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
    roles: List[GetNodeRole]
    class Config:
        orm_mode  =  True

class NodeRolePatch(CamelModel):
    node_name: str
    role_name: str
    extra_json: dict = None