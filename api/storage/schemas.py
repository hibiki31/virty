from datetime import datetime
from importlib.resources import path
from time import strftime
from typing import Any, List, Optional

from fastapi_camelcase import CamelModel
from flavor.models import FlavorModel

from node.schemas import NodePage
from flavor.schemas import Flavor


class ImageBase(CamelModel):
    pass


class StorageQuery(CamelModel):
    name: str = None
    node_name: str = None


class StorageMetadata(CamelModel):
    rool: str = None
    protocol: str = None
    device_type: str = None
    class Config:
        orm_mode  =  True

class StorageMetadataForUpdate(CamelModel):
    uuid: str
    rool: str
    protocol: str
    device_type: str
    class Config:
        orm_mode  =  True

class ImageForUpdateImageFlavor(CamelModel):
    storage_uuid: str
    path: str
    node_name: str
    flavor_id: int
    class Config:
        orm_mode  =  True

class StoragePage(CamelModel):
    name: str
    uuid: str
    status: int
    active: bool
    available: int = None
    capacity: int = None
    node_name: str
    node: NodePage
    auto_start: bool
    path: str = None
    meta_data: StorageMetadata = None
    update_token:str = None
    allocation_commit: int = None
    capacity_commit: int = None
    class Config:
        orm_mode  =  True
    

class Storage(CamelModel):
    count: int
    data: List[StoragePage]
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

class ImageDomain(CamelModel):
    owner_user_id: str = None
    issuance_id: int = None
    name: str
    uuid: str

class Image(ImageBase):
    name:str
    storage_uuid:str = None
    capacity:int
    storage: Storage
    flavor: Flavor = None
    allocation:int
    path:str
    update_token:str = None
    domain: ImageDomain = None
    class Config:
        orm_mode  =  True

class StorageForCreate(CamelModel):
    name: str
    node_name: str
    path: str
    class Config:
        orm_mode  =  True

class StorageForDelete(CamelModel):
    uuid: str
    node_name: str

class ImageSCP(CamelModel):
    from_node_name: str
    to_node_name: str
    from_file_path: str
    to_file_path: str

class StoragePoolForCreate(CamelModel):
    name:str
    storage_uuids: List[str]


class StoragePoolForUpdate(CamelModel):
    id:str
    storage_uuids: List[str]


class StorageForStorageContainer(CamelModel):
    name: str
    uuid: str
    node_name: str
    class Config:
        orm_mode  =  True

class StorageContainerForStoragePool(CamelModel):
    storage: StorageForStorageContainer
    class Config:
        orm_mode  =  True

class StoragePool(CamelModel):
    id: int
    name: str
    storages: List[StorageContainerForStoragePool]
    class Config:
        orm_mode  =  True