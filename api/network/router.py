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

from module import virtlib


app = APIRouter()
logger = setup_logger(__name__)


@app.get("/api/networks", tags=["network"], response_model=List[GetNetwork])
def get_api_networks(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    return db.query(NetworkModel).all()


@app.put("/api/networks", tags=["network"])
def put_api_networks(
        bg: BackgroundTasks,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    task = TaskManager(db=db, bg=bg)
    task.select('put', 'network', 'list')
    task.commit(user=current_user)
   
    return task.model

@app.post("/api/networks", tags=["network"], response_model=TaskSelect)
def post_api_storage(
        bg: BackgroundTasks,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        request: NetworkInsert = None
    ):
    task = TaskManager(db=db, bg=bg)
    task.select('post', 'network', 'root')
    task.commit(user=current_user, request=request)

    return task.model

@app.delete("/api/networks", tags=["network"], response_model=TaskSelect)
def post_api_storage(
        bg: BackgroundTasks,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        request: NetworkDelete = None
    ):
    task = TaskManager(db=db, bg=bg)
    task.select('delete', 'network', 'root')
    task.commit(user=current_user, request=request)

    return task.model

@app.get("/api/networks/pools", tags=["network"], response_model=List[GetNetworkPool])
def get_api_networks_pools(
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):

    return db.query(NetworkPoolModel).all()


@app.post("/api/networks/pools", tags=["network"])
def post_api_networks_pools(
        model: PostNetworkPool,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):
    pool_model = NetworkPoolModel(name=model.name)
    db.add(pool_model)
    db.commit()
    return True


@app.patch("/api/networks/pools", tags=["network"])
def patch_api_networks_pools(
        model: PatchNetworkPool,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):
    pool_model = db.query(NetworkPoolModel).filter(NetworkPoolModel.id==model.pool_id).one()
    if model.port_name != None:
        port_model = db.query(NetworkPortgroupModel).filter(
            NetworkPortgroupModel.network_uuid==model.network_uuid,
            NetworkPortgroupModel.name==model.port_name).one()
        pool_model.ports.append(port_model)
    else:
        network_model = db.query(NetworkModel).filter(NetworkModel.uuid==model.network_uuid).one()
        pool_model.networks.append(network_model)
    db.commit()
    return True

@app.get("/api/networks/{uuid}", tags=["network"], response_model=GetNetwork)
def get_api_networks_uuid(
        uuid:str,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    try:
        network: NetworkModel = db.query(NetworkModel).filter(NetworkModel.uuid==uuid).one()
    except NoResultFound:
        raise notfound_exception()

    return network

@app.post("/api/networks/ovs", tags=["network"], response_model=TaskSelect)
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

    return main_task.model

@app.delete("/api/networks/ovs", tags=["network"], response_model=TaskSelect)
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

    return main_task.model


