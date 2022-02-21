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


app = APIRouter()
logger = setup_logger(__name__)


@app.post("/api/nodes", tags=["node"], response_model=TaskSelect)
async def post_api_nodes(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        request_model: NodeInsert = None
    ):
    # ノード追加タスク
    node_post_task = PostTask(db=db, user=current_user, model=request_model)
    node_task_model = node_post_task.commit("node","base","add")

    dependence_uuid = node_task_model.uuid

    # ドメインリスト更新タスク
    post_task = PostTask(db=db, user=current_user, model=None)
    task_model = post_task.commit("vm","list","update", status="wait",dependence_uuid=dependence_uuid)

    # ネットワーク更新タスク
    post_task = PostTask(db=db, user=current_user, model=None)
    task_model = post_task.commit("network","list","update",dependence_uuid=dependence_uuid)

    # ストレージ更新タスク
    post_task = PostTask(db=db, user=current_user, model=None)
    task_model = post_task.commit("storage","list","update",dependence_uuid=dependence_uuid)

    return node_task_model


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


@app.patch("/api/node/role", tags=["node"], response_model=TaskSelect)
async def patch_api_node_role(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        model: NodeRolePatch = None
    ):
    post_task = PostTask(db=db, user=current_user, model=model)
    task_model = post_task.commit("node","role","change")

    return task_model