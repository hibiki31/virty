from __future__ import annotations

from typing import List

from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str


class Project(BaseModel):
    name: str


class Server(BaseModel):
    name: str
    domain: str
    username: str


class Storage(BaseModel):
    name: str
    path: str


class TestEnviroment(BaseModel):
    base_url: str
    username: str
    password: str
    users: List[User]
    projects: List[Project]
    key: str
    pub: str
    servers: List[Server]
    storages: List[Storage]
    image_url: str
