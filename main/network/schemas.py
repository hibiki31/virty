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