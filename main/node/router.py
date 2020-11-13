from fastapi import APIRouter, Depends, BackgroundTasks, Request
from sqlalchemy.orm import Session

from .models import *
from .schemas import *

from auth.router import CurrentUser, get_current_user
from task.models import TaskModel
from mixin.database import get_db
from mixin.log import setup_logger

from node.models import NodeModel
from module import virty


app = APIRouter()
logger = setup_logger(__name__)


@app.post("/api/nodes", tags=["node"])
async def post_api_nodes(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        node: NodeInsert = None,
        background_tasks: BackgroundTasks = None
    ):
    # タスクを追加
    task_model = post_node_base(bg=background_tasks, db=db, cu=current_user, model=node)
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