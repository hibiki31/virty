from decimal import Clamped
from fastapi_camelcase import CamelModel
from typing import List, Optional
from pydantic import BaseModel

class PostTicket(CamelModel):
    core:int
    memory:int
    network_pools: List[int]
    storage_pools: List[int]
    flavors: List[int]
    user_installable: bool
    isolated_networks: int