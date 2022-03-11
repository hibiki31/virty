from datetime import datetime
from decimal import Clamped
from fastapi_camelcase import CamelModel
from typing import List, Optional
from pydantic import BaseModel

from network.schemas import GetNetworkPool
from storage.schemas import GetStoragePool
from flavor.schemas import GetFlavor


class PostTicket(CamelModel):
    name: str
    core:int
    memory:int
    storage_capacity_g:int = None
    network_pools: List[int]
    storage_pools: List[int]
    flavors: List[int]
    user_installable: bool
    isolated_networks: int
    class Config:
        orm_mode  =  True

class GetTicket(PostTicket):
    id: int
    network_pools: List[GetNetworkPool]
    storage_pools: List[GetStoragePool]
    flavors: List[GetFlavor]
    class Config:
        orm_mode  =  True

class PostIssuance(CamelModel):
    user_id: str
    ticket_id: str
    class Config:
        orm_mode  =  True


class GetIssuance(PostIssuance):
    id: int
    issued_by: str
    issued_date: datetime
    ticket: GetTicket
    class Config:
        orm_mode  =  True
