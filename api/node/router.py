from os import name, chmod, makedirs
import string
from tkinter import N
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
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


app = APIRouter(prefix="/api", tags=["nodes"])
logger = setup_logger(__name__)


@app.post("/nodes/key")
def post_ssh_key_pair(
        model: SSHKeyPair,
        current_user: CurrentUser = Depends(get_current_user)
    ):
    makedirs('/root/.ssh/', exist_ok=True)
    
    with open("/root/.ssh/id_rsa", "w") as f:
        f.write(model.key.rstrip('\r\n') + '\n')
    with open("/root/.ssh/id_rsa.pub", "w") as f:
        f.write(model.pub)
    
    chmod('/root/.ssh/', 0o700)
    chmod('/root/.ssh/id_rsa', 0o600)
    chmod('/root/.ssh/id_rsa.pub', 0o600)

    return {}


@app.get("/nodes/key", response_model=SSHKeyPair)
def get_ssh_key_pair(current_user: CurrentUser = Depends(get_current_user)):
    private_key = ""
    publick_key = ""
    try: 
        with open("/root/.ssh/id_rsa") as f:
            private_key = f.read()
        with open("/root/.ssh/id_rsa.pub") as f:
            publick_key = f.read()
    except:
        pass

    return SSHKeyPair(private_key=private_key, publick_key=publick_key)


@app.post("/tasks/nodes", response_model=TaskSelect)
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


@app.get("/nodes", response_model=List[GetNode])
def get_api_nodes(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):

    return db.query(NodeModel).all()


@app.delete("")
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








@app.patch("/roles", response_model=TaskSelect)
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


@app.get("/pools")
def get_api_nodes_pools(
        db: Session = Depends(get_db)
    ):

    return db.query(PoolCpu).all()


@app.post("/pools")
def post_api_nodes_pools(
        model: NodeBase,
        db: Session = Depends(get_db),
    ):
    pool_model = PoolCpu(name=model.name)
    db.add(pool_model)
    db.commit()
    return True


@app.patch("/pools")
def patch_api_nodes_pools(
        model: PatchNodePool,
        db: Session = Depends(get_db),
    ):
    ass = AssociationPoolsCpu(pool_id=model.pool_id, node_name=model.node_name, core=model.core)
    db.add(ass)
    db.commit()
    return True


@app.get("/{node_name}/facts")
def get_node_name_facts(
        node_name: str,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):

    node = db.query(NodeModel).filter(NodeModel.name == node_name).one_or_none()
    
    if node == None:
        raise HTTPException(status_code=404, detail="Node not found")

    return node.ansible_facts["result"]