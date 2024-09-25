import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.router import app as auth_router
from log import setup_logger
from node.router import app as node_router
from settings import API_VERSION
from user.router import app as user_router

logger = setup_logger(__name__)


tags_metadata = [
    {"name": "mixin", "description": ""},
    {
        "name": "auth", 
        "description": "トークン関係のリクエストはRFCの関係でスネークケース"
    },
    {"name": "users", "description": ""}
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

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(node_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8765, reload=True)