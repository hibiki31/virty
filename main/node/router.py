from fastapi import APIRouter, Depends, BackgroundTasks, Request
from sqlalchemy.orm import Session

from .models import *
from .schemas import *

from auth.router import CurrentUser, get_current_user
from task.models import TaskModel
from task.schemas import TaskSelect
from task.function import PostTask
from mixin.database import get_db
from mixin.log import setup_logger

from node.models import NodeModel
from module import virty


app = APIRouter()
logger = setup_logger(__name__)


@app.post("/api/nodes", tags=["node"], response_model=TaskSelect)
async def post_api_nodes(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        request_model: NodeInsert = None
    ):
    # タスクを追加
    post_task = PostTask(db=db, user=current_user, model=request_model)
    task_model = post_task.commit("node","base","add")

    return task_model


@app.get("/api/nodes", tags=["node"],response_model=List[NodeSelect])
async def get_api_nodes(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):

    return db.query(NodeModel).all()


@app.delete("/api/nodes", tags=["node"], response_model=List[NodeSelect])
async def delete_api_nodes(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        node: NodeDelete = None,
    ):
    
    model = db.query(NodeModel).filter(NodeModel.name==node.name).all()
    db.query(NodeModel).filter(NodeModel.name==node.name).delete()
    db.commit()

    return model