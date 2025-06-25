from typing import List

from flavor.schemas import Flavor
from mixin.schemas import BaseSchema, GetPagination
from storage.schemas import Storage


class ImageBase(BaseSchema):
    pass


class ImageForUpdateImageFlavor(BaseSchema):
    storage_uuid: str
    path: str
    node_name: str
    flavor_id: int
    


class ImageDomain(BaseSchema):
    owner_user_id: str | None = None
    issuance_id: int | None = None
    name: str
    uuid: str


class Image(ImageBase):
    name:str
    storage_uuid:str
    capacity:int
    storage: Storage
    flavor: Flavor | None = None
    allocation:int
    path:str
    update_token:str | None = None
    domain: ImageDomain | None = None
    


class ImagePage(BaseSchema):
    count: int
    data: List[Image]
    


class ImageForQuery(GetPagination):
    node_name: str | None = None
    pool_uuid: str | None = None
    name:str | None = None
    name_like:str | None = None
    rool:str | None = None


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


class ImageDownloadForCreate(BaseSchema):
    storage_uuid: str
    image_url: str


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
    