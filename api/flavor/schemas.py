from typing import List

from mixin.schemas import BaseSchema, GetPagination


class FlavorForCreate(BaseSchema):
    name: str
    os: str
    manual_url: str
    icon: str
    cloud_init_ready: bool
    description: str
    

        
class Flavor(FlavorForCreate):
    id: int
    
        

class FlavorPage(BaseSchema):
    count: int
    data: List[Flavor]
    

class FlavorForQuery(GetPagination):
    name_like: str| None = None 