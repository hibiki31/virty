from typing import Union, Any

from fastapi import FastAPI, Depends
from settings import API_VERSION
from mixins.schema import BaseSchema, GetPagination
from mixins.database import get_mongo_client
from pymongo.database import Database
from bson.json_util import dumps, loads

tags_metadata = [
    {
        "name": "auth", 
        "description": "トークン関係のリクエストはRFCの関係でスネークケース"
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
    servers=[{"url": "", "description": "Default"}]
)


@app.get("/api/v2/resource/hello")
def read_root():
    return {"Hello": "World"}


@app.get("/api/v2/resource/nodes")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}



class Resouce(BaseSchema):
    spec: dict


@app.post("/api/v2/resource/{resouce}")
def post_api_domain_uuid(
        resouce: str,
        data: Resouce,
        db: get_mongo_client = Depends(get_mongo_client)
    ):

    db[resouce].insert_one(data.model_dump())
    return {"resouce": resouce}

@app.get("/api/v2/resource/{resouce}")
def get_api_domain_uuid(
        resouce: str,
        db: Database = Depends(get_mongo_client)
    ):
    res = db[resouce].find({})

    return dict(res.to_list(1000))