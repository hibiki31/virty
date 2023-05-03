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


app = APIRouter(prefix="/api/networks", tags=["networks"])
logger = setup_logger(__name__)


@app.get("", response_model=List[GetNetwork])
def get_api_networks(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    return db.query(NetworkModel).all()


@app.get("/pools", response_model=List[GetNetworkPool])
def get_api_networks_pools(
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):

    return db.query(NetworkPoolModel).all()


@app.post("/pools")
def post_api_networks_pools(
        model: PostNetworkPool,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):
    pool_model = NetworkPoolModel(name=model.name)
    db.add(pool_model)
    db.commit()
    return True


@app.patch("/pools")
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


@app.get("/{uuid}", response_model=GetNetwork)
def get_api_networks_uuid(
        uuid: str,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    try:
        network: NetworkModel = db.query(NetworkModel).filter(NetworkModel.uuid==uuid).one()
    except NoResultFound:
        raise notfound_exception(msg="Network not found")

    return network