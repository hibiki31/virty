from fastapi import APIRouter, Depends, BackgroundTasks, Request
from sqlalchemy.orm import Session

from .models import *
from .schemas import *

from auth.router import CurrentUser, get_current_user
from task.models import TaskModel
from node.models import NodeModel
from mixin.database import get_db
from mixin.log import setup_logger

from module import virty
from module import virtlib
from module import xmllib


app = APIRouter()
logger = setup_logger(__name__)


@app.put("/api/vms", tags=["vm"])
async def put_api_domains(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        background_tasks: BackgroundTasks = None
    ):
    # タスクを追加
    post_task = PostTask(db=db, user=current_user, model=None)
    task_model = post_task.commit("domain","list","update")
   
    return task_model


@app.get("/api/vms", tags=["vm"],response_model=List[DomainSelect])
async def get_api_domain(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):

    return db.query(DomainModel).all()


@app.delete("/api/vms", tags=["vm"], response_model=List[DomainSelect])
async def delete_api_domains(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        node: DomainDelete = None,
    ):
    model = db.query(DomainModel).filter(DomainModel.name==node.name).all()
    db.query(DomainModel).filter(DomainModel.name==node.name).delete()
    db.commit()

    return model