from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from auth.router import CurrentUser, get_current_user
from mixin.database import get_db
from mixin.log import setup_logger
from resource_deletion import (
    ResourceDeletionConflictError,
    ResourceDeletionNotFoundError,
    ensure_network_deletable,
    ensure_network_port_deletable,
)
from resource_authorization import require_admin
from task.functions import TaskManager
from task.schemas import Task

from .models import NetworkModel
from .schemas import NetworkForCreate, NetworkOVSForCreate

app = APIRouter(prefix="/api/tasks/networks", tags=["networks-task"])
logger = setup_logger(__name__)


@app.put("", response_model=List[Task])
def refresh_networks(
        req: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    cu.verify_scope(["network.manage"])
    require_admin(cu)
    task = TaskManager(db=db)
    task.select(method='put', resource='network', object='list')
    task.commit(user=cu, req=req)
   
    return [task.model]


@app.post("", response_model=List[Task])
def create_network(
        req: Request,
        body: NetworkForCreate,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    cu.verify_scope(["network.manage"])
    require_admin(cu)
    task = TaskManager(db=db)
    task.select(method='post', resource='network', object='root')
    task.commit(user=cu, req=req, body=body)

    task_put_list = TaskManager(db=db)
    task_put_list.select('put', 'network', 'list')
    task_put_list.commit(user=cu, dep_uuid=task.model.uuid)


    return [ task.model, task_put_list.model ]


@app.post("/{uuid}/ovs", response_model=List[Task])
def create_network_ovs(
        uuid: str,
        req: Request,
        body: NetworkOVSForCreate,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    cu.verify_scope(["network.manage"])
    require_admin(cu)
    if db.get(NetworkModel, uuid) is None:
        raise HTTPException(status_code=404, detail="network not found")
    task = TaskManager(db=db)
    task.select(method='post', resource='network', object='ovs')
    task.commit(user=cu, req=req, param={"uuid": uuid}, body=body)

    task_put_list = TaskManager(db=db)
    task_put_list.select('put', 'network', 'list')
    task_put_list.commit(user=cu, dep_uuid=task.model.uuid)

    return [task.model, task_put_list.model ]


@app.delete("/{uuid}/ovs/{name}", response_model=List[Task])
def delete_network_ovs(
        uuid: str,
        name: str,
        req: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    cu.verify_scope(["network.manage"])
    require_admin(cu)
    try:
        ensure_network_port_deletable(db, uuid, name)
    except ResourceDeletionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ResourceDeletionConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    task = TaskManager(db=db)
    task.select(method='delete', resource='network', object='ovs')
    task.commit(user=cu, req=req, param={"uuid": uuid, "name": name})

    task_put_list = TaskManager(db=db)
    task_put_list.select('put', 'network', 'list')
    task_put_list.commit(user=cu, dep_uuid=task.model.uuid)

    return [ task.model, task_put_list.model ]


@app.delete("/{uuid}", response_model=List[Task])
def delete_network(
        uuid: str,
        req: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    cu.verify_scope(["network.manage"])
    require_admin(cu)
    try:
        ensure_network_deletable(db, uuid)
    except ResourceDeletionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ResourceDeletionConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    task = TaskManager(db=db)
    task.select(method='delete', resource='network', object='root')
    task.commit(user=cu, req=req, param={"uuid": uuid})

    task_put_list = TaskManager(db=db)
    task_put_list.select('put', 'network', 'list')
    task_put_list.commit(user=cu, dep_uuid=task.model.uuid)

    return [ task.model, task_put_list.model ]
