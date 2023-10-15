from urllib import request
from fastapi import APIRouter, Depends, Request
from fastapi import HTTPException
from sqlalchemy import or_, desc
from sqlalchemy.orm import Session

from .models import *
from .schemas import *

from auth.router import CurrentUser, get_current_user
from task.schemas import Task, TaskRequest
from task.functions import TaskManager
from user.models import UserModel
from project.models import ProjectModel
from mixin.database import get_db
from mixin.log import setup_logger
from mixin.exception import notfound_exception

from celery import chain, group

from module.virtlib import VirtManager


app = APIRouter(
    tags=["vms"]
)

logger = setup_logger(__name__)


@app.get("/api/vms",response_model=DomainPagenation)
def get_api_domain(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        admin: bool = False,
        limit: int = 25,
        page: int = 0,
        name_like: str = None,
        node_name_like: str = None
    ):

    query = db.query(DomainModel).order_by(DomainModel.node_name,DomainModel.name)

    if admin:
        current_user.verify_scope(scopes=["admin"])
    else:
        query = query.filter(or_(
                DomainModel.owner_user_id==current_user.id,
                DomainModel.project.has(ProjectModel.users.any(username=current_user.id))
        ))
    if name_like:
        query = query.filter(DomainModel.name.like(f'%{name_like}%'))
    if node_name_like:
        query = query.filter(DomainModel.node_name.like(f'%{node_name_like}%'))

    count = query.count()

    query = query.order_by(desc(DomainModel.name))
    vms = query.limit(limit).offset(int(limit*page)).all()

    return {"count": count, "data": vms}


@app.get("/api/vms/{uuid}",response_model=DomainDetail)
def get_api_domain_uuid(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        uuid:str = None
    ):
    try:
        domain:DomainModel = db.query(DomainModel).filter(DomainModel.uuid==uuid).one()
    except:
        raise HTTPException(status_code=404, detail="Not found domain")

    return domain


@app.get("/api/vms/vnc/{token}")
def get_api_domain(
        token: str,
        db: Session = Depends(get_db),
    ):

    domain_model = db.query(DomainModel).filter(DomainModel.uuid==token).one()

    return { "host": domain_model.node.domain, "port": domain_model.vnc_port }