from pydantic import BaseModel
from typing import List, Optional


class AttributeDict(object):
    def __init__(self, attrs=None):
        if type(attrs) == dict:
            for k, v in attrs.items():
                setattr(self, k, v)
    
    def __repr__(self):
        return str(self.__dict__)
        

class ImageModel(BaseModel):
    xml: str


class StorageModel(BaseModel):
    active: bool
    auto_start: bool
    status: int
    xml: str
    images: List[ImageModel]