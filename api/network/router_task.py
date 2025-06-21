from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from auth.router import CurrentUser, get_current_user
from mixin.database import get_db
from mixin.log import setup_logger
from task.functions import TaskManager
from task.schemas import Task

from .models import *
from .schemas import *

app = APIRouter(prefix="/api/tasks/networks", tags=["networks-task"])
logger = setup_logger(__name__)


@app.put("", response_model=List[Task])
def refresh_networks(
        req: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    
    task = TaskManager(db=db)
    task.select(method='put', resource='network', object='list')
    task.commit(user=cu, req=req)
   
    return [task.model]


@app.post("", response_model=List[Task])
def create_network(
        req: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        body: NetworkForCreate = None
    ):

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
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        body: NetworkOVSForCreate = None
    ):

    task = TaskManager(db=db)
    task.select(method='post', resource='network', object='ovs')
    task.commit(user=cu, req=req, param={"uuid": uuid}, body=body)

    task_put_list = TaskManager(db=db)
    task_put_list.select('put', 'network', 'list')
    task_put_list.commit(user=cu, dep_uuid=task.model.uuid)

    return [task.model, task_put_list.model ]


@app.post("/providers", response_model=List[Task])
def create_network_providers(
        req: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        body: NetworkProviderForCreate = None
    ):

    task = TaskManager(db=db)
    task.select(method='post', resource='network', object='provider')
    task.commit(user=cu, req=req, body=body)

    return [ task.model ]


@app.delete("/{uuid}/ovs/{name}", response_model=List[Task])
def delete_network_ovs(
        uuid: str,
        name: str,
        req: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):

    try:
        db.query(NetworkModel).filter(NetworkModel.uuid == uuid).one()
        db.query(
            NetworkPortgroupModel).filter(
            NetworkPortgroupModel.network_uuid==uuid
            ).filter(NetworkPortgroupModel.name==name).one()
    except:
        raise HTTPException(status_code=404, detail="network or port is not found")

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

    task = TaskManager(db=db)
    task.select(method='delete', resource='network', object='root')
    task.commit(user=cu, req=req, param={"uuid": uuid})

    task_put_list = TaskManager(db=db)
    task_put_list.select('put', 'network', 'list')
    task_put_list.commit(user=cu, dep_uuid=task.model.uuid)

    return [ task.model, task_put_list.model ]