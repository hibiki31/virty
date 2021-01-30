from fastapi import APIRouter, Depends, Request
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
from mixin.exception import exception_notfund

from module import virtlib
from module import xmllib


app = APIRouter()
logger = setup_logger(__name__)


@app.get("/api/networks", tags=["network"], response_model=List[NetworkSelect])
async def get_api_networks(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    return db.query(NetworkModel).all()


@app.put("/api/networks", tags=["network"])
async def put_api_networks(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    post_task = PostTask(db=db, user=current_user, model=None)
    task_model = post_task.commit("network","list","update")
   
    return task_model

@app.post("/api/networks", tags=["network"], response_model=TaskSelect)
async def post_api_storage(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        request_model: NetworkInsert = None
    ):
    # タスクを追加
    post_task = PostTask(db=db, user=current_user, model=request_model)
    task_model = post_task.commit("network","base","add")

    return task_model

@app.delete("/api/networks", tags=["network"], response_model=TaskSelect)
async def post_api_storage(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        request_model: NetworkDelete = None
    ):
    # タスクを追加
    post_task = PostTask(db=db, user=current_user, model=request_model)
    task_model = post_task.commit("network","base","delete")

    return task_model

@app.get("/api/networks/{uuid}", tags=["network"])
async def get_api_networks_uuid(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        uuid:str = ""
    ):
    try:
        network: NetworkModel = db.query(NetworkModel).filter(NetworkModel.uuid==uuid).one()
    except NoResultFound:
        raise exception_notfund

    editor = virtlib.XmlEditor("network",network.uuid)
    xml = editor.network_pase()

    return {'db':network, 'xml': xml}

@app.post("/api/network/ovs", tags=["network"], response_model=TaskSelect)
async def post_api_networks_uuid_ovs(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        request_model: NetworkOVSAdd = None,
    ):
    # タスクを追加
    post_task = PostTask(db=db, user=current_user, model=request_model)
    task_model = post_task.commit("network","ovs","add")
   
    return task_model

@app.delete("/api/network/ovs", tags=["network"], response_model=TaskSelect)
async def post_api_networks_uuid_ovs(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        request_model: NetworkOVSDelete = None,
    ):
    # タスクを追加
    post_task = PostTask(db=db, user=current_user, model=request_model)
    task_model = post_task.commit("network","ovs","delete")
   
    return task_model