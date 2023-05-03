from os import name, chmod, makedirs

from fastapi import APIRouter, Depends, Request
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
from mixin.exception import *

from node.models import NodeModel


app = APIRouter(prefix="/api/tasks/nodes", tags=["node-task"])
logger = setup_logger(__name__)


@app.post("", response_model=List[TaskSelect])
def post_tasks_nodes(
        req: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        body: NodeInsert = None
    ):
    
    task = TaskManager(db=db)
    task.select(method='post', resource='node', object='root')
    task.commit(user=cu, req=req, body=body)

    if body.libvirt_role:
        body_libvirt = NodeRolePatch(node_name=body.name, role_name="libvirt")
        task_libvirt = TaskManager(db=db)
        task_libvirt.select(method="patch", resource="node", object="role")
        task_libvirt.commit(user=cu, req=req, body=body_libvirt,dep_uuid=task.model.uuid)
        dependence_uuid = task_libvirt.model.uuid

        return [task.model, task_libvirt.model]

    return [task.model]


@app.delete("/{name}", response_model=List[TaskSelect])
def delete_tasks_nodes_name(
        name: str,
        req: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):

    task = TaskManager(db=db)
    task.select(method='delete', resource='node', object='root')
    task.commit(user=cu, req=req, param={"name": name})

    return [task.model]


@app.patch("/roles", response_model=TaskSelect)
def patch_api_node_role(
        request: NodeRolePatch,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    task = TaskManager(db=db)
    task.select('patch', 'node', 'role')
    task.commit(user=current_user, request=request)
    
    return task.model
