from typing import List

from flavor.schemas import Flavor
from mixin.schemas import BaseSchema, GetPagination
from node.schemas import Node


class ImageBase(BaseSchema):
    pass


class StorageForQuery(GetPagination):
    name_like: str | None = None
    node_name: str | None = None


class StorageMetadata(BaseSchema):
    rool: str | None = None
    protocol: str | None = None
    device_type: str | None = None
    


class StorageMetadataForUpdate(BaseSchema):
    uuid: str
    rool: str
    protocol: str
    device_type: str
    


class ImageForUpdateImageFlavor(BaseSchema):
    storage_uuid: str
    path: str
    node_name: str
    flavor_id: int
    


class Storage(BaseSchema):
    name: str
    uuid: str
    status: int
    active: bool
    available: int | None = None
    capacity: int | None = None
    node_name: str
    node: Node
    auto_start: bool
    path: str | None = None
    meta_data: StorageMetadata | None = None
    update_token:str | None = None
    allocation_commit: int | None = None
    capacity_commit: int | None = None
    

class StoragePage(BaseSchema):
    count: int
    data: List[Storage]


class PaseImage(ImageBase):
    name:str
    storage_uuid:str | None = None
    capacity: float
    allocation: float
    path:str
    update_token:str | None = None


class PaseStorage(BaseSchema):
    uuid: str
    name: str
    node_name: str | None = None
    capacity: int | None = None
    available: int | None = None
    path: str | None = None
    active: bool
    auto_start: bool
    status: int
    update_token:str | None = None
    images: List[PaseImage]


class ImageDomain(BaseSchema):
    owner_user_id: str | None = None
    issuance_id: int | None = None
    name: str
    uuid: str


class Image(ImageBase):
    name:str
    storage_uuid:str | None = None
    capacity:int
    storage: Storage
    flavor: Flavor | None = None
    allocation:int
    path:str
    update_token:str | None = None
    domain: ImageDomain | None = None


class StorageForCreate(BaseSchema):
    name: str
    node_name: str
    path: str


class StorageForDelete(BaseSchema):
    uuid: str
    node_name: str


class ImageSCP(BaseSchema):
    from_node_name: str
    to_node_name: str
    from_file_path: str
    to_file_path: str


class StoragePoolForCreate(BaseSchema):
    name:str
    storage_uuids: List[str]


class StoragePoolForUpdate(BaseSchema):
    id:str
    storage_uuids: List[str]


class StorageForStorageContainer(BaseSchema):
    name: str
    uuid: str
    node_name: str


class StorageContainerForStoragePool(BaseSchema):
    storage: StorageForStorageContainer


class StoragePool(BaseSchema):
    id: int
    name: str
    storages: List[StorageContainerForStoragePool]