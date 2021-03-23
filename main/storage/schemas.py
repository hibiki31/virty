from datetime import datetime
from typing import List, Optional

from fastapi_camelcase import CamelModel

from node.schemas import NodeSelect


class ImageBase(CamelModel):
    pass




class StorageMetadataSelect(CamelModel):
    rool: str
    class Config:
        orm_mode  =  True

class StorageMetadataPatch(CamelModel):
    uuid: str
    rool: str
    class Config:
        orm_mode  =  True

class StorageSelect(CamelModel):
    name: str
    uuid: str
    status: int
    active: bool 
    protocol: str = None
    available: int = None
    capacity: int = None
    node_name: str
    node: NodeSelect
    auto_start: bool
    path: str = None
    meta_data: StorageMetadataSelect = None
    update_token:str = None
    class Config:
        orm_mode  =  True

class ImageRaw(ImageBase):
    name:str
    storage_uuid:str = None
    capacity:int
    allocation:int
    path:str
    update_token:str = None
    class Config:
        orm_mode  =  True

class ImageSelect(ImageBase):
    name:str
    storage_uuid:str = None
    capacity:int
    storage: StorageSelect
    allocation:int
    path:str
    update_token:str = None
    class Config:
        orm_mode  =  True

class StorageInsert(CamelModel):
    name: str
    node_name: str
    path: str
    class Config:
        orm_mode  =  True

class StorageDelete(CamelModel):
    uuid: str
    node_name: str