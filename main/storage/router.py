from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from .models import *
from .schemas import *

from auth.router import CurrentUser, get_current_user
from task.models import TaskModel
from task.schemas import TaskSelect
from task.function import PostTask
from node.models import NodeModel
from mixin.database import get_db
from mixin.log import setup_logger

from module import virty
from module import virtlib
from module import xmllib


app = APIRouter()
logger = setup_logger(__name__)


@app.get("/api/storages", tags=["storage"], response_model=List[StorageSelect])
async def get_api_storages(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):

    return db.query(StorageModel).all()


@app.get("/api/images", tags=["storage"], response_model=List[ImageRaw])
async def get_api_images(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):

    return db.query(ImageModel).all()


@app.put("/api/images", tags=["storage"])
async def put_api_images(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    # タスクを追加
    post_task = PostTask(db=db, user=current_user, model=None)
    task_model = post_task.commit("storage","list","update")
   
    return task_model


@app.post("/api/storages", tags=["storage"], response_model=TaskSelect)
async def post_api_storage(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        request_model: StorageInsert = None
    ):
    # タスクを追加
    post_task = PostTask(db=db, user=current_user, model=request_model)
    task_model = post_task.commit("storage","base","add")

    return task_model

@app.delete("/api/storages", tags=["storage"], response_model=TaskSelect)
async def delete_api_storages(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        request_model: StorageDelete = None
    ):
    # タスクを追加
    post_task = PostTask(db=db, user=current_user, model=request_model)
    task_model = post_task.commit("storage","base","delete")

    return task_model