from typing import List

from fastapi_camelcase import CamelModel

from flavor.schemas import Flavor
from mixin.schemas import GetPagination
from storage.schemas import Storage


class ImageBase(CamelModel):
    pass


class ImageForUpdateImageFlavor(CamelModel):
    storage_uuid: str
    path: str
    node_name: str
    flavor_id: int
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


class ImagePage(CamelModel):
    count: int
    data: List[Image]
    class Config:
        orm_mode  =  True


class ImageForQuery(GetPagination):
    node_name: str = None
    pool_uuid: str = None
    name:str = None
    name_like:str = None
    rool:str = None


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


class ImageDownloadForCreate(CamelModel):
    storage_uuid: str
    image_url: str


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