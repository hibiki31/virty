from pydantic import BaseModel
from typing import List, Optional


class ImageModel(BaseModel):
    xml: str


class StorageModel(BaseModel):
    active: bool
    auto_start: bool
    status: int
    xml: str
    images: List[ImageModel]