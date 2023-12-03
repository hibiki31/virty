from fastapi_camelcase import CamelModel
from typing import List, Optional
from pydantic import BaseModel

class FlavorForCreate(CamelModel):
    name: str
    os: str
    manual_url: str
    icon: str
    cloud_init_ready: bool
    description: str
    class Config:
        orm_mode  =  True

        
class FlavorPage(FlavorForCreate):
    id: int
    class Config:
        orm_mode  =  True
        

class Flavor(CamelModel):
    count: int
    data: List[FlavorPage]