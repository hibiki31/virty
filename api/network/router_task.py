from time import sleep
from fastapi import APIRouter, Depends, Request, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from .models import *
from .schemas import *

from auth.router import CurrentUser, get_current_user
from task.models import TaskModel
from task.schemas import TaskSelect
from task.functions import TaskManager
from node.models import NodeModel
from mixin.database import get_db
from mixin.log import setup_logger
from mixin.exception import notfound_exception


app = APIRouter(prefix="/api/tasks/networks", tags=["network-task"])
logger = setup_logger(__name__)


@app.put("", response_model=List[TaskSelect])
def put_api_networks(
        req: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    
    task = TaskManager(db=db)
    task.select(method='put', resource='network', object='list')
    task.commit(user=cu, req=req)
   
    return [task.model]


@app.post("", response_model=List[TaskSelect])
def post_api_storage(
        req: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        body: NetworkInsert = None
    ):

    task = TaskManager(db=db)
    task.select(method='post', resource='network', object='root')
    task.commit(user=cu, req=req, body=body)

    task_put_list = TaskManager(db=db)
    task_put_list.select('put', 'network', 'list')
    task_put_list.commit(user=cu, dep_uuid=task.model.uuid)


    return [ task.model, task_put_list.model ]


@app.delete("/{uuid}", response_model=List[TaskSelect])
def delete_api_storage(
        uuid: str,
        req: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):

    task = TaskManager(db=db)
    task.select(method='delete', resource='network', object='root')
    task.commit(user=cu, req=req, param={"uuid": uuid})

    task_put_list = TaskManager(db=db)
    task_put_list.select('put', 'network', 'list')
    task_put_list.commit(user=cu, dep_uuid=task.model.uuid)

    return [ task.model, task_put_list.model ]


@app.post("/ovs", response_model=List[TaskSelect])
def post_api_networks_uuid_ovs(
        bg: BackgroundTasks,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        request: NetworkOVSAdd = None,
    ):

    main_task = TaskManager(db=db, bg=bg)
    main_task.select('post', 'network', 'ovs')
    main_task.commit(user=current_user, request=request)

    reload_task = TaskManager(db=db, bg=bg)
    reload_task.select('put', 'network', 'list')
    reload_task.commit(user=current_user, dependence_uuid=main_task.model.uuid)

    return [main_task.model, reload_task.model ]


@app.delete("/ovs", response_model=List[TaskSelect])
def post_api_networks_uuid_ovs(
        bg: BackgroundTasks,
        request: NetworkOVSDelete,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user),
    ):

    main_task = TaskManager(db=db, bg=bg)
    main_task.select('delete', 'network', 'ovs')
    main_task.commit(user=current_user, request=request)

    reload_task = TaskManager(db=db, bg=bg)
    reload_task.select('put', 'network', 'list')
    reload_task.commit(user=current_user, dependence_uuid=main_task.model.uuid)

    return [ main_task.model, reload_task.model ]