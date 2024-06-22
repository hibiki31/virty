from typing import Any, List

from pydantic import BaseModel

class Meta(BaseModel):
    auto_added: bool
    managed_by_apps: bool
    managed_by_argo_tunnel: bool


class Result(BaseModel):
    id: str
    zone_id: str
    zone_name: str
    name: str
    type: str
    content: str
    proxiable: bool
    proxied: bool
    ttl: int
    locked: bool
    meta: Meta
    comment: Any
    tags: List
    created_on: str
    modified_on: str


class Model(BaseModel):
    result: Result
    success: bool
    errors: List
    messages: List