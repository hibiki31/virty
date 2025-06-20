
from typing import List

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from auth.router import CurrentUser, get_current_user
from mixin.database import get_db
from mixin.log import setup_logger
from task.functions import TaskManager
from task.schemas import Task

from .schemas import NodeForCreate, NodeRoleForUpdate

app = APIRouter(prefix="/api/tasks/nodes", tags=["nodes-task"])
logger = setup_logger(__name__)


@app.post("", response_model=List[Task], operation_id="create_node")
def post_tasks_nodes(
        req: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        body: NodeForCreate = None
    ):
    
    res_task = []
    
    task = TaskManager(db=db)
    task.select(method='post', resource='node', object='root')
    task.commit(user=cu, req=req, body=body)
    res_task.append(task.model)

    if body.libvirt_role:
        body_libvirt = NodeRoleForUpdate(node_name=body.name, role_name="libvirt")
        task_libvirt = TaskManager(db=db)
        task_libvirt.select(method="patch", resource="node", object="role")
        task_libvirt.commit(user=cu, req=req, body=body_libvirt, dep_uuid=task.model.uuid)
        res_task.append(task_libvirt.model)
        
    # リストのリロード
    task_list = TaskManager(db=db)
    task_list.select('put', 'vm', 'list')
    task_list.commit(user=cu, dep_uuid=task.model.uuid)
    res_task.append(task_list.model)

    task_storage = TaskManager(db=db)
    task_storage.select('put', 'storage', 'list')
    task_storage.commit(user=cu, dep_uuid=task.model.uuid)
    res_task.append(task_storage.model)

    task_network = TaskManager(db=db)
    task_network.select('put', 'network', 'list')
    task_network.commit(user=cu, dep_uuid=task.model.uuid)
    res_task.append(task_network.model)

    return res_task


@app.delete("/{name}", response_model=List[Task], operation_id="delete_node")
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


@app.patch("/roles", response_model=Task, operation_id="update_node_role")
def patch_api_node_role(
        body: NodeRoleForUpdate,
        req: Request,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    task = TaskManager(db=db)
    task.select('patch', 'node', 'role')
    task.commit(user=current_user, req=req, body=body)
    
    return [ task.model ]
