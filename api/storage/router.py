from email.mime import image
from pprint import pprint
from fastapi import APIRouter, Depends, BackgroundTasks, Request, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import false, func, true
from domain.models import DomainDriveModel, DomainModel

from flavor.models import FlavorModel

from .models import *
from .schemas import *

from auth.router import CurrentUser, get_current_user
from task.models import TaskModel
from task.schemas import TaskSelect
from task.functions import TaskManager
from node.models import NodeModel
from mixin.database import get_db
from mixin.log import setup_logger

from module import virtlib
from module import xmllib
from module.sshlib import SSHManager


app = APIRouter()
logger = setup_logger(__name__)


@app.get("/api/storages", tags=["storages"], response_model=List[Storage])
def get_api_storages(
        param: StorageQuery = Depends(),
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):

    image_sum = db.query(
        ImageModel.storage_uuid,
        func.sum(ImageModel.capacity).label('sum_capacity'),
        func.sum(ImageModel.allocation).label('sum_allocation')
    ).group_by(ImageModel.storage_uuid).subquery('image_sum')

    query = db.query(
        StorageModel,
        image_sum.c.sum_capacity,
        image_sum.c.sum_allocation
    ).outerjoin(
        image_sum,
        StorageModel.uuid==image_sum.c.storage_uuid
    ).order_by(StorageModel.node_name,StorageModel.name)

    if param.node_name != None:
        query = query.filter(NodeModel.name==param.node_name)

    if param.name != None:
        query = query.filter(StorageModel.name.like(f'%{param.name}%'))


    models = query.all()

    res = []

    for model in models:
        tmp = model[0]
        tmp.capacity_commit = model[1]
        tmp.allocation_commit = model[2]
        res.append(tmp)

    return res


@app.patch("/api/storages", tags=["storages"])
def post_api_storage(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        request_model: StorageMetadataForUpdate = None
    ):
    db.merge(StorageMetadataModel(**request_model.dict()))
    db.commit()
    return db.query(StorageModel).filter(StorageModel.uuid==request_model.uuid).all()


@app.get("/api/storages/pools", tags=["storages"], response_model=List[StoragePool])
def get_api_storages_pools(
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):

    return db.query(StoragePoolModel).all()


@app.post("/api/storages/pools", tags=["storages"])
def post_api_storages_pools(
        request_model: StoragePoolForCreate,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    storage_pool_model = StoragePoolModel(name=request_model.name)
    db.add(storage_pool_model)
    for storage_uuid in request_model.storage_uuids:
        storage_pool_model.storages.append(
            AssociationStoragePoolModel(storage_uuid=storage_uuid, pool_id=storage_pool_model.id)
        )
    db.commit()
    return db.query(StoragePoolModel).filter(StoragePoolModel.id==storage_pool_model.id).one()


@app.patch("/api/storages/pools", tags=["storages"])
def post_api_storages_pools(
        request_model: StoragePoolForUpdate,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    storage_pool_model = db.query(StoragePoolModel).filter(StoragePoolModel.id==request_model.id).one()
    for storage_uuid in request_model.storage_uuids:
        storage_pool_model.storages.append(
            AssociationStoragePoolModel(storage_uuid=storage_uuid, pool_id=storage_pool_model.id)
        )
    db.commit()
    return db.query(StoragePoolModel).filter(StoragePoolModel.id==storage_pool_model.id).one()


@app.get("/api/storages/{uuid}", tags=["storages"], response_model=Storage)
def get_api_storages_uuid(
        uuid: str,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):

    image_sum = db.query(
        ImageModel.storage_uuid,
        func.sum(ImageModel.capacity).label('sum_capacity'),
        func.sum(ImageModel.allocation).label('sum_allocation')
    ).group_by(ImageModel.storage_uuid).subquery('image_sum')

    query = db.query(
        StorageModel,
        image_sum.c.sum_capacity,
        image_sum.c.sum_allocation
    ).outerjoin(
        image_sum,
        StorageModel.uuid==image_sum.c.storage_uuid
    ).order_by(StorageModel.node_name,StorageModel.name)

    model = query.filter(StorageModel.uuid==uuid).one_or_none()

    if model == None:
        raise HTTPException(status_code=404, detail="storage is not found")

    res = model[0]
    res.capacity_commit = model[1]
    res.allocation_commit = model[2]

    return res


@app.post("/api/tasks/storages", tags=["storages-task"], response_model=List[TaskSelect])
def post_api_storage(
        req: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        body: StorageForCreate = None
    ):

    task = TaskManager(db=db)
    task.select(method='post', resource='storage', object='root')
    task.commit(user=cu, req=req, body=body)

    task_put_list = TaskManager(db=db)
    task_put_list.select('put', 'storage', 'list')
    task_put_list.commit(user=cu, req=req)

    return [task.model, task_put_list.model]


@app.delete("/api/tasks/storages/{uuid}", tags=["storages-task"], response_model=List[TaskSelect])
def delete_api_storages(
        uuid: str,
        req: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):

    task = TaskManager(db=db)
    task.select(method='delete', resource='storage', object='root')
    task.commit(user=cu, req=req, param={"uuid": uuid})

    return [task.model]