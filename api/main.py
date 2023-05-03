import uvicorn

from fastapi import FastAPI, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.router import app as auth_router
from node.router import app as node_router
from task.router import app as task_router
from domain.router import app as domain_router
from storage.router import app as storage_router
from network.router import app as network_router
from network.router_task import app as network_task_router
from user.router import app as user_router
from project.router import app as project_router
from flavor.router import app as flavor_router
from exporter.router import app as exporter_router
from mixin.router import app as mixin_router

from mixin.log import setup_logger
from settings import API_VERSION


logger = setup_logger(__name__)


tags_metadata = [
    {"name": "mixin", "description": ""},
    {"name": "auth", "description": "トークン関係のリクエストはRFCの関係でスネークケース"},
    {"name": "users", "description": ""},
    {"name": "nodes", "description": ""},
    {"name": "tasks-nodes", "description": ""},
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
app.include_router(network_task_router)
app.include_router(user_router)
app.include_router(project_router)
app.include_router(flavor_router)
app.include_router(exporter_router)
app.include_router(mixin_router)



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8765, reload=True)