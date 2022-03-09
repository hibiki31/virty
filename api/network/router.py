from time import sleep
from fastapi import APIRouter, Depends, Request, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from .models import *
from .schemas import *

from auth.router import CurrentUser, get_current_user
from task.models import TaskModel
from task.schemas import TaskSelect
from task.function import PostTask
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
    post_task = PostTask(db=db, user=current_user, model=None)
    task_model = post_task.commit("network","list","update", bg)
   
    return task_model

@app.post("/api/networks", tags=["network"], response_model=TaskSelect)
def post_api_storage(
        bg: BackgroundTasks,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        request_model: NetworkInsert = None
    ):
    # タスクを追加
    post_task = PostTask(db=db, user=current_user, model=request_model)
    task_model = post_task.commit("network","base","add", bg)

    return task_model

@app.delete("/api/networks", tags=["network"], response_model=TaskSelect)
def post_api_storage(
        bg: BackgroundTasks,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        request_model: NetworkDelete = None
    ):
    # タスクを追加
    post_task = PostTask(db=db, user=current_user, model=request_model)
    task_model = post_task.commit("network","base","delete", bg)

    return task_model

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
    ass = AssociationNetworkPool(pool_id=model.pool_id, network_uuid=model.network_uuid, port_name=model.port_name)
    db.add(ass)
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
        request_model: NetworkOVSAdd = None,
    ):
    # タスクを追加
    post_task = PostTask(db=db, user=current_user, model=request_model)
    task_model = post_task.commit("network","ovs","add", bg)

    post_task = PostTask(db=db, user=current_user, model=None)
    task_model = post_task.commit("network","list","update", bg=bg, status="wait", dependence_uuid=task_model.uuid)
   
    return task_model

@app.delete("/api/networks/ovs", tags=["network"], response_model=TaskSelect)
def post_api_networks_uuid_ovs(
        bg: BackgroundTasks,
        request_model: NetworkOVSDelete,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user),
    ):
    # タスクを追加
    post_task = PostTask(db=db, user=current_user, model=request_model)
    task_model = post_task.commit("network","ovs","delete", bg=bg)

    post_task = PostTask(db=db, user=current_user, model=None)
    task_model = post_task.commit("network","list","update", bg=bg, status="wait", dependence_uuid=task_model.uuid)
   
    return task_model


