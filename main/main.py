import subprocess
import time
import uvicorn

from fastapi import status, FastAPI, Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.requests import Request
from mixin.database import SessionLocal, Engine, Base
from typing import List, Optional

from auth.router import app as auth_router
from node.router import app as node_router
from task.router import app as task_router
from domain.router import app as domain_router
from storage.router import app as storage_router
from network.router import app as network_router

from mixin.log import setup_logger
from settings import APP_ROOT, API_VERSION


logger = setup_logger(__name__)

worker_pool = []

tags_metadata = [
    {"name": "auth", "description": ""},
    {"name": "user", "description": ""},
    {"name": "node", "description": ""},
]

app = FastAPI(
    title="VirtyAPI",
    description="",
    version=API_VERSION,
    openapi_tags=tags_metadata,
    docs_url="/api",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(task_router)
app.include_router(auth_router)
app.include_router(node_router)
app.include_router(domain_router)
app.include_router(storage_router)
app.include_router(network_router)


def worker_up():
    worker_pool.append(subprocess.Popen(["python3", APP_ROOT + "/worker.py"]))


def worker_down():
    for w in worker_pool:
        w.terminate()


@app.on_event("startup")
async def startup_event():
    worker_up()

@app.on_event("shutdown")
async def shutdown_event():
    worker_down()
    

# 全てのリクエストで同じ処理が書ける
@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    # 処理前のログ記述
    start_time = time.time()
    
    # セッションを各リクエストに載せる
    request.state.db = SessionLocal()

    # 各関数で処理を行って結果を受け取る
    response = await call_next(request)

    # 処理後のログ
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = '{0:.2f}'.format(process_time)
    logger.info(f"{request.method} {request.client.host} {response.status_code} {request.url.path} {formatted_process_time}ms")

    # 結果を返す
    return response

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, access_log=False)