from typing import List

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from auth.router import CurrentUser, get_current_user
from mixin.database import get_db
from mixin.log import setup_logger
from task.functions import TaskManager
from task.schemas import Task

from .schemas import (
    ImageDownloadForCreate,
)

app = APIRouter(prefix="/api/tasks/images", tags=["images-task"])
logger = setup_logger(__name__)


@app.put("", response_model=List[Task])
def refresh_images(
        req: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    task = TaskManager(db=db)
    task.select(method='put', resource='storage', object='list')
    task.commit(user=cu, req=req)

    return [task.model]


@app.post("/download", response_model=List[Task])
def download_image(
        req: Request,
        body: ImageDownloadForCreate,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):

    task = TaskManager(db=db)
    task.select(method='post', resource='image', object='download')
    task.commit(user=cu, req=req, body=body)

    return [task.model]
