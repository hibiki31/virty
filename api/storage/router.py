from typing import Any, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from auth.router import CurrentUser, get_current_user
from mixin.database import get_db
from mixin.exception import ApiError, ApiErrorCode
from mixin.log import setup_logger
from project.service import (
    ProjectConflictError,
    ProjectGrantNotFoundError,
    ensure_storage_pool_deletable,
    ensure_storage_pool_update_allowed,
    remove_storage_pool,
)
from resource_authorization import (
    allowed_storage_ids,
    allowed_storage_pool_ids,
    get_authorized_storage,
    is_global_inventory,
    require_admin,
)

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
    StoragePoolDeleteResponse,
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
) -> dict[str, Any]:
    current_user.verify_scope(["storage.read"])
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
    if not is_global_inventory(current_user, admin=param.admin, project_id=param.project_id):
        allowed_storages = allowed_storage_ids(db, current_user, param.project_id)
        query = query.filter(StorageModel.uuid.in_(allowed_storages))

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


@app.patch("", response_model=None)
def update_storage_metadata(
        request_model: StorageMetadataForUpdate,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        admin: bool = False,
) -> list[StorageModel]:
    current_user.verify_scope(["storage.manage"])
    get_authorized_storage(db, request_model.uuid, current_user, admin=admin)
    db.merge(StorageMetadataModel(**request_model.model_dump()))
    db.commit()
    return db.query(StorageModel).filter(StorageModel.uuid==request_model.uuid).all()


@app.get("/pools", response_model=List[StoragePool])
def get_storage_pools(
        project_id: str | None = Query(default=None, alias="projectId"),
        admin: bool = False,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
) -> list[StoragePoolModel]:
    current_user.verify_scope(["storage.read"])
    query = db.query(StoragePoolModel)
    if not is_global_inventory(current_user, admin=admin, project_id=project_id):
        allowed_pools = allowed_storage_pool_ids(db, current_user, project_id)
        query = query.filter(StoragePoolModel.id.in_(allowed_pools))
    return query.all()


@app.post("/pools", response_model=StoragePool)
def create_storage_pool(
        request_model: StoragePoolForCreate,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
) -> StoragePoolModel:
    current_user.verify_scope(["storage.manage"])
    require_admin(current_user)
    storage_pool_model = StoragePoolModel(name=request_model.name)
    db.add(storage_pool_model)
    for storage_uuid in request_model.storage_uuids:
        if db.get(StorageModel, storage_uuid) is None:
            raise ApiError(
                404,
                ApiErrorCode.STORAGE_NOT_FOUND,
                "The storage was not found.",
            )
        storage_pool_model.storages.append(
            AssociationStoragePoolModel(storage_uuid=storage_uuid, pool_id=storage_pool_model.id)
        )
    db.commit()
    return db.query(StoragePoolModel).filter(StoragePoolModel.id==storage_pool_model.id).one()


@app.patch("/pools", response_model=StoragePool)
def update_storage_pool(
        request_model: StoragePoolForUpdate,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
) -> StoragePoolModel:
    current_user.verify_scope(["storage.manage"])
    require_admin(current_user)
    storage_uuids = set(request_model.storage_uuids)
    for storage_uuid in storage_uuids:
        if db.get(StorageModel, storage_uuid) is None:
            raise ApiError(
                404,
                ApiErrorCode.STORAGE_NOT_FOUND,
                "The storage was not found.",
            )
    try:
        storage_pool_model = ensure_storage_pool_update_allowed(
            db,
            request_model.id,
            storage_uuids,
        )
    except ProjectGrantNotFoundError as exc:
        raise ApiError(
            404,
            ApiErrorCode.STORAGE_POOL_NOT_FOUND,
            "The storage pool was not found.",
        ) from exc
    except ProjectConflictError as exc:
        raise ApiError(
            409,
            ApiErrorCode.STORAGE_POOL_IN_USE,
            "The storage pool is still in use.",
        ) from exc

    db.query(AssociationStoragePoolModel).filter(
        AssociationStoragePoolModel.pool_id == storage_pool_model.id,
    ).delete(synchronize_session=False)
    for storage_uuid in sorted(storage_uuids):
        db.add(
            AssociationStoragePoolModel(storage_uuid=storage_uuid, pool_id=storage_pool_model.id)
        )
    db.commit()
    return db.query(StoragePoolModel).filter(StoragePoolModel.id==storage_pool_model.id).one()


@app.delete("/pools/{pool_id}", response_model=StoragePoolDeleteResponse)
def delete_storage_pool(
    pool_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StoragePoolDeleteResponse:
    current_user.verify_scope(["storage.manage"])
    require_admin(current_user)
    try:
        pool = ensure_storage_pool_deletable(db, pool_id)
    except ProjectGrantNotFoundError as exc:
        raise ApiError(
            404,
            ApiErrorCode.STORAGE_POOL_NOT_FOUND,
            "The storage pool was not found.",
        ) from exc
    except ProjectConflictError as exc:
        raise ApiError(
            409,
            ApiErrorCode.STORAGE_POOL_IN_USE,
            "The storage pool is still in use.",
        ) from exc
    remove_storage_pool(db, pool)
    db.commit()
    return StoragePoolDeleteResponse(deleted=True, id=pool_id)


@app.get("/{uuid}", response_model=Storage)
def get_storage(
        uuid: str,
        admin: bool = False,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
) -> StorageModel:
    cu.verify_scope(["storage.read"])
    get_authorized_storage(db, uuid, cu, admin=admin)
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

    if model is None:
        raise ApiError(
            404,
            ApiErrorCode.STORAGE_NOT_FOUND,
            "The storage was not found.",
        )

    res = model[0]
    res.capacity_commit = model[1]
    res.allocation_commit = model[2]

    return res
