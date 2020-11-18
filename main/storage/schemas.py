from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from fastapi_camelcase import CamelModel


class ImageBase(BaseModel):
    pass

class ImageRaw(ImageBase):
    name:str
    storage_uuid:str = None
    capacity:int
    allocation:int
    path:str
    update_token:str = None

class StorageSelect(CamelModel):
    name: str
    uuid: str
    status: int
    active: bool 
    protocol: str
    available: int
    capacity: int
    node_name: str
    auto_start: bool
    path: str
    update_token:str = None
    class Config:
        orm_mode  =  True