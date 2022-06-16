from os import name
from fastapi import APIRouter, Depends, BackgroundTasks, Request
from sqlalchemy import true
from sqlalchemy.orm import Session

from .models import *
from .schemas import *

from auth.router import CurrentUser, get_current_user
from task.models import TaskModel
from task.schemas import TaskSelect
from task.functions import TaskManager
from mixin.database import get_db
from mixin.log import setup_logger

from node.models import NodeModel


app = APIRouter()
logger = setup_logger(__name__)


@app.post("/api/nodes", tags=["node"], response_model=TaskSelect)
def post_api_nodes(
        bg: BackgroundTasks,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        request: NodeInsert = None
    ):
    # ノード追加タスク
    task = TaskManager(db=db, bg=bg)
    task.select(method="post", resource="node", object="root")
    task.commit(request=request, user=current_user)

    dependence_uuid = task.model.uuid

    if request.libvirt_role:
        libvirt_request = NodeRolePatch(node_name=request.name, role_name="libvirt")
        libvirt_task = TaskManager(db=db, bg=bg)
        libvirt_task.select(method="patch", resource="node", object="role")
        libvirt_task.commit(request=libvirt_request, user=current_user, dependence_uuid=dependence_uuid)
        dependence_uuid = libvirt_task.model.uuid


    post_task = TaskManager(db=db, bg=bg)
    post_task.select("put", "vm", "list")
    post_task.commit(user=current_user, dependence_uuid=dependence_uuid)

    post_task = TaskManager(db=db, bg=bg)
    post_task.select("put", "network", "list")
    post_task.commit(user=current_user, dependence_uuid=dependence_uuid)

    post_task = TaskManager(db=db, bg=bg)
    post_task.select("put", "storage", "list")
    post_task.commit(user=current_user, dependence_uuid=dependence_uuid)

    return task.model


@app.get("/api/nodes", tags=["node"],response_model=List[GetNode])
def get_api_nodes(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):

    return db.query(NodeModel).all()


@app.delete("/api/nodes", tags=["node"])
def delete_api_nodes(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        node: NodeDelete = None,
    ):
    
    db.query(AssociationNodeToRole).filter(AssociationNodeToRole.node_name==node.name).delete()
    db.query(AssociationPoolsCpu).filter(AssociationPoolsCpu.node_name==node.name).delete()
    db.commit()
    db.query(NodeModel).filter(NodeModel.name==node.name).delete()
    db.commit()

    return node


@app.patch("/api/nodes/role", tags=["node"], response_model=TaskSelect)
def patch_api_node_role(
        model: NodeRolePatch,
        bg: BackgroundTasks,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    task = TaskManager(db=db, bg=bg)
    task.select('patch', 'node', 'role')
    task.commit(user=current_user,request=model)
    
    return task.model


@app.get("/api/nodes/pools", tags=["node"])
def get_api_nodes_pools(
        db: Session = Depends(get_db)
    ):

    return db.query(PoolCpu).all()


@app.post("/api/nodes/pools", tags=["node"])
def post_api_nodes_pools(
        model: NodeBase,
        db: Session = Depends(get_db),
    ):
    pool_model = PoolCpu(name=model.name)
    db.add(pool_model)
    db.commit()
    return True

@app.patch("/api/nodes/pools", tags=["node"])
def patch_api_nodes_pools(
        model: PatchNodePool,
        db: Session = Depends(get_db),
    ):
    ass = AssociationPoolsCpu(pool_id=model.pool_id, node_name=model.node_name, core=model.core)
    db.add(ass)
    db.commit()
    return True