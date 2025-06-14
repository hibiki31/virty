import uuid
from typing import Union

from fastapi import Depends, FastAPI
from pymongo.database import Database

from mixins.database import get_mongo_client
from mixins.schema import BaseSchema
from settings import API_VERSION

tags_metadata = [
    {
        "name": "auth",
        "description": "トークン関係のリクエストはRFCの関係でスネークケース",
    },
]

app = FastAPI(
    title="VirtyAPI",
    description="",
    version=API_VERSION,
    openapi_tags=tags_metadata,
    docs_url="/api",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    servers=[{"url": "", "description": "Default"}],
)


@app.get("/api/v2/resource/hello")
def read_root():
    return {"Hello": "World"}


@app.get("/api/v2/resource/nodes")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


class Resouce(BaseSchema):
    spec: dict = None


@app.post("/api/v2/resource/{resouce}")
def post_api_domain_uuid(
    resouce: str, data: dict, db: get_mongo_client = Depends(get_mongo_client)
):
    data["_id"] = str(uuid.uuid4())
    db[resouce].insert_one(data)
    return {"resouce": resouce}


@app.get("/api/v2/resource/{resouce}")
def get_api_domain_uuid(resouce: str, db: Database = Depends(get_mongo_client)):
    resouces = db[resouce].find({})

    return resouces.to_list(1000)


@app.post("/api/v2/resource/{resouce}/find")
def post_resouce(
    resouce: str, data: dict, db: get_mongo_client = Depends(get_mongo_client)
):
    resouces = db[resouce].find(data)

    return resouces.to_list(1000)
