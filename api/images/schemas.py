from datetime import datetime
from importlib.resources import path
from time import strftime
from typing import Any, List, Optional

from fastapi_camelcase import CamelModel
from flavor.models import FlavorModel

from node.schemas import GetNode
from flavor.schemas import GetFlavor


from storage.schemas import StorageSelect


class ImageBase(CamelModel):
    pass


class PatchImageFlavor(CamelModel):
    storage_uuid: str
    path: str
    node_name: str
    flavor_id: int
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