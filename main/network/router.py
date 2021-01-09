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

from module import virtlib
from module import xmllib


app = APIRouter()
logger = setup_logger(__name__)


@app.get("/api/networks", tags=["network"], response_model=List[NetworkSelect])
async def get_api_networks(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    return db.query(NetworkModel).all()


@app.put("/api/networks", tags=["network"])
async def put_api_networks(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    post_task = PostTask(db=db, user=current_user, model=None)
    task_model = post_task.commit("network","list","update")
   
    return task_model

@app.post("/api/networks", tags=["network"], response_model=TaskSelect)
async def post_api_storage(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        request_model: NetworkInsert = None
    ):
    # タスクを追加
    post_task = PostTask(db=db, user=current_user, model=request_model)
    task_model = post_task.commit("network","base","add")

    return task_model

@app.delete("/api/networks", tags=["network"], response_model=TaskSelect)
async def post_api_storage(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        request_model: NetworkDelete = None
    ):
    # タスクを追加
    post_task = PostTask(db=db, user=current_user, model=request_model)
    task_model = post_task.commit("network","base","delete")

    return task_model