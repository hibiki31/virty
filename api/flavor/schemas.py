from typing import List

from fastapi_camelcase import CamelModel

from mixin.schemas import GetPagination


class FlavorForCreate(CamelModel):
    name: str
    os: str
    manual_url: str
    icon: str
    cloud_init_ready: bool
    description: str
    class Config:
        orm_mode  =  True

        
class Flavor(FlavorForCreate):
    id: int
    class Config:
        orm_mode  =  True
        

class FlavorPage(CamelModel):
    count: int
    data: List[Flavor]
    

class FlavorForQuery(GetPagination):
    name_like: str = None