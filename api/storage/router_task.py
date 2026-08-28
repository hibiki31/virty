from typing import List

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from auth.router import CurrentUser, get_current_user
from mixin.database import get_db
from mixin.exception import ApiError, ApiErrorCode
from mixin.log import setup_logger
from resource_deletion import (
    ResourceDeletionConflictError,
    ResourceDeletionNotFoundError,
    ensure_image_deletable,
    ensure_storage_deletable,
)
from resource_authorization import get_authorized_storage, require_admin
from task.functions import TaskManager
from task.schemas import Task

from .schemas import (
    StorageForCreate,
)

app = APIRouter(prefix="/api/tasks/storages", tags=["storages-task"])
logger = setup_logger(__name__)


@app.post("", response_model=List[Task])
def create_storage(
        req: Request,
        body: StorageForCreate,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    cu.verify_scope(["storage.manage"])
    require_admin(cu)
    task = TaskManager(db=db)
    task.select(method='post', resource='storage', object='root')
    task.commit(user=cu, req=req, body=body)

    task_put_list = TaskManager(db=db)
    task_put_list.select('put', 'storage', 'list')
    task_put_list.commit(user=cu, dep_uuid=task.model.uuid)

    return [task.model, task_put_list.model]


@app.delete("/{uuid}", response_model=List[Task])
def delete_storage(
        uuid: str,
        req: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    cu.verify_scope(["storage.manage"])
    require_admin(cu)
    try:
        ensure_storage_deletable(db, uuid)
    except ResourceDeletionNotFoundError as exc:
        raise ApiError(
            404,
            ApiErrorCode.STORAGE_NOT_FOUND,
            "The storage was not found.",
        ) from exc
    except ResourceDeletionConflictError as exc:
        raise ApiError(
            409,
            ApiErrorCode.RESOURCE_IN_USE,
            "The storage is still in use.",
        ) from exc
    task = TaskManager(db=db)
    task.select(method='delete', resource='storage', object='root')
    task.commit(user=cu, req=req, param={"uuid": uuid})

    return [task.model]


@app.delete("/{uuid}/images/{name}", response_model=List[Task])
def delete_image(
        uuid: str,
        name: str,
        req: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    cu.verify_scope(["image.manage"])
    get_authorized_storage(db, uuid, cu)
    try:
        ensure_image_deletable(db, uuid, name)
    except ResourceDeletionNotFoundError as exc:
        raise ApiError(
            404,
            ApiErrorCode.IMAGE_NOT_FOUND,
            "The image was not found.",
        ) from exc
    except ResourceDeletionConflictError as exc:
        raise ApiError(
            409,
            ApiErrorCode.RESOURCE_IN_USE,
            "The image is still in use.",
        ) from exc
    task = TaskManager(db=db)
    task.select(method='delete', resource='image', object='root')
    task.commit(user=cu, req=req, param={"uuid": uuid, "name": name})

    return [task.model]
