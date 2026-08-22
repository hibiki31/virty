import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from prometheus_fastapi_instrumentator import Instrumentator

from auth.router import app as auth_router
from dashboard.router import app as dashboard_router
from domain.router import app as domain_router
from domain.router_task import app as domain_task_router
from exporter.router import app as exporter_router
from flavor.router import app as flavor_router
from images.router import app as image_router
from images.router_task import app as image_task_router
from mixin.log import setup_logger
from mixin.prometheus import install_prometheus_route_compatibility
from mixin.router import app as mixin_router
from network.router import app as network_router
from network.router_task import app as network_task_router
from node.router import app as node_router
from node.router_task import app as node_task_router
from project.router import app as project_router
from project.router_task import app as project_task_router
from settings import API_VERSION
from storage.router import app as storage_router
from storage.router_task import app as storage_task_router
from task.router import app as task_router
from user.router import app as user_router

logger = setup_logger(__name__)


def operation_id_from_route_name(route: APIRoute) -> str:
    """生成clientとの互換性を保つためroute名をoperation IDにする。"""

    return route.name


tags_metadata = [
    {"name": "mixin", "description": ""},
    {
        "name": "auth", 
        "description": "トークン関係のリクエストはRFCの関係でスネークケース"
    },
    {"name": "users", "description": ""},
    {"name": "projects", "description": ""},
    {"name": "dashboard", "description": ""},
    {"name": "tasks", "description": ""},
    {"name": "nodes", "description": ""},
    {"name": "nodes-task", "description": ""},
    {"name": "vms", "description": ""},
    {"name": "vms-task", "description": ""},
    {"name": "storages", "description": ""},
    {"name": "storages-task", "description": ""},
    {"name": "images", "description": ""},
    {"name": "images-task", "description": ""},
    {"name": "networks", "description": ""},
    {"name": "networks-task", "description": ""},
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
    generate_unique_id_function=operation_id_from_route_name,
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
app.include_router(dashboard_router)
app.include_router(node_router)
app.include_router(node_task_router)
app.include_router(domain_router)
app.include_router(domain_task_router)
app.include_router(storage_router)
app.include_router(storage_task_router)
app.include_router(image_router)
app.include_router(image_task_router)
app.include_router(network_router)
app.include_router(network_task_router)
app.include_router(user_router)
app.include_router(project_router)
app.include_router(project_task_router)
app.include_router(flavor_router)
app.include_router(exporter_router)
app.include_router(mixin_router)

install_prometheus_route_compatibility()
Instrumentator(
    excluded_handlers=["/metrics"],
).instrument(app).expose(app=app, endpoint="/api/metrics-fastapi", tags=["metrics"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=7799, reload=True)
