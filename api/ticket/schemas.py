from datetime import datetime
from decimal import Clamped
from fastapi_camelcase import CamelModel
from typing import List, Optional
from pydantic import BaseModel

from network.schemas import NetworkPool
from storage.schemas import StoragePool
from flavor.schemas import Flavor


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
    network_pools: List[NetworkPool]
    storage_pools: List[StoragePool]
    flavors: List[Flavor]
    class Config:
        orm_mode  =  True

class PostIssuance(CamelModel):
    project_id: str
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
