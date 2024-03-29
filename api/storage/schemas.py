from datetime import datetime
from importlib.resources import path
from time import strftime
from typing import Any, List, Optional

from fastapi_camelcase import CamelModel
from flavor.models import FlavorModel

from node.schemas import GetNode
from flavor.schemas import GetFlavor


class ImageBase(CamelModel):
    pass




class StorageMetadataSelect(CamelModel):
    rool: str = None
    protocol: str = None
    device_type: str = None
    class Config:
        orm_mode  =  True

class StorageMetadataPatch(CamelModel):
    uuid: str
    rool: str
    protocol: str
    device_type: str
    class Config:
        orm_mode  =  True

class PatchImageFlavor(CamelModel):
    storage_uuid: str
    path: str
    node_name: str
    flavor_id: int
    class Config:
        orm_mode  =  True

class StorageSelect(CamelModel):
    name: str
    uuid: str
    status: int
    active: bool
    available: int = None
    capacity: int = None
    node_name: str
    node: GetNode
    auto_start: bool
    path: str = None
    meta_data: StorageMetadataSelect = None
    update_token:str = None
    allocation_commit: int = None
    capacity_commit: int = None
    class Config:
        orm_mode  =  True


class PaseImage(ImageBase):
    name:str
    storage_uuid:str = None
    capacity:int
    allocation:int
    path:str
    update_token:str = None
    class Config:
        orm_mode  =  True


class PaseStorage(CamelModel):
    uuid: str
    name: str
    node_name: str = None
    capacity: int = None
    available: int = None
    path: str = None
    active: bool
    auto_start: bool
    status: int
    update_token:str = None
    images: List[PaseImage]
    class Config:
        orm_mode  =  True

class GetImageDomain(CamelModel):
    owner_user_id: str = None
    issuance_id: int = None
    name: str
    uuid: str

class ImageSelect(ImageBase):
    name:str
    storage_uuid:str = None
    capacity:int
    storage: StorageSelect
    flavor: GetFlavor = None
    allocation:int
    path:str
    update_token:str = None
    domain: GetImageDomain = None
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

class ImageSCP(CamelModel):
    from_node_name: str
    to_node_name: str
    from_file_path: str
    to_file_path: str

class PostStoragePool(CamelModel):
    name:str
    storage_uuids: List[str]


class PatchStoragePool(CamelModel):
    id:str
    storage_uuids: List[str]


class GetStoragePoolStoragesStorage(CamelModel):
    name: str
    uuid: str
    node_name: str
    class Config:
        orm_mode  =  True

class GetStoragePoolStorages(CamelModel):
    storage: GetStoragePoolStoragesStorage
    class Config:
        orm_mode  =  True

class GetStoragePool(CamelModel):
    id: int
    name: str
    storages: List[GetStoragePoolStorages]
    class Config:
        orm_mode  =  True