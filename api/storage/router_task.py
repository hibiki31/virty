from typing import List

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from auth.router import CurrentUser, get_current_user
from mixin.database import get_db
from mixin.log import setup_logger
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


@app.delete("/{uuid}", response_model=List[Task])
def delete_storage(
        uuid: str,
        req: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):

    task = TaskManager(db=db)
    task.select(method='delete', resource='storage', object='root')
    task.commit(user=cu, req=req, param={"uuid": uuid})

    return [task.model]