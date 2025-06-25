from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from auth.router import CurrentUser, get_current_user
from mixin.database import get_db
from mixin.log import setup_logger

from .models import (
    AssociationStoragePoolModel,
    ImageModel,
    StorageMetadataModel,
    StorageModel,
    StoragePoolModel,
)
from .schemas import (
    Storage,
    StorageForQuery,
    StorageMetadataForUpdate,
    StoragePage,
    StoragePool,
    StoragePoolForCreate,
    StoragePoolForUpdate,
)

app = APIRouter(prefix="/api/storages", tags=["storages"])
logger = setup_logger(__name__)


@app.get("", response_model=StoragePage)
def get_storages(
        param: StorageForQuery = Depends(),
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
    ).order_by(StorageModel.name,StorageModel.node_name)

    if param.node_name:
        query = query.filter(StorageModel.node_name==param.node_name)

    if param.name_like:
        query = query.filter(StorageModel.name.like(f'%{param.name_like}%'))

    count = query.count()
    if param.limit > 0:
        query = query.limit(param.limit).offset(int(param.limit*param.page))
    models = query.all()

    res = []

    for model in models:
        tmp = model[0]
        tmp.capacity_commit = model[1]
        tmp.allocation_commit = model[2]
        res.append(tmp)


    return {"count": count, "data": res}


@app.patch("")
def update_storage_metadata(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        request_model: StorageMetadataForUpdate = None
    ):
    db.merge(StorageMetadataModel(**request_model.dict()))
    db.commit()
    return db.query(StorageModel).filter(StorageModel.uuid==request_model.uuid).all()


@app.get("/pools", response_model=List[StoragePool])
def get_storage_pools(
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):

    return db.query(StoragePoolModel).all()


@app.post("/pools")
def create_storage_pool(
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


@app.patch("/pools")
def update_storage_pool(
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


@app.get("/{uuid}", response_model=Storage)
def get_storage(
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


