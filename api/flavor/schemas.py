from fastapi_camelcase import CamelModel
from typing import List, Optional
from pydantic import BaseModel

class PostFlavor(CamelModel):
    name: str
    os: str
    manual_url: str
    icon: str
    cloud_init_ready: bool
    description: str
    class Config:
        orm_mode  =  True
        
class GetFlavor(PostFlavor):
    id: int
    class Config:
        orm_mode  =  True