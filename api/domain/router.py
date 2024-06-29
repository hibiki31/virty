from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from auth.router import CurrentUser, get_current_user
from mixin.database import get_db
from mixin.log import setup_logger
from project.models import ProjectModel

from .models import DomainModel
from .schemas import DomainDetail, DomainForQuery, DomainPage

app = APIRouter(
    tags=["vms"]
)

logger = setup_logger(__name__)


@app.get("/api/vms",response_model=DomainPage, operation_id="get_vms")
def get_api_domain(
        param: DomainForQuery = Depends(),
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):

    query = db.query(DomainModel).order_by(DomainModel.node_name,DomainModel.name)

    if param.admin:
        current_user.verify_scope(scopes=["admin"])
    else:
        query = query.filter(or_(
                DomainModel.owner_user_id==current_user.id,
                DomainModel.project.has(ProjectModel.users.any(username=current_user.id))
        ))
    if param.name_like:
        query = query.filter(DomainModel.name.like(f'%{param.name_like}%'))
    if param.node_name_like:
        query = query.filter(DomainModel.node_name.like(f'%{param.node_name_like}%'))

    count = query.count()

    query = query.order_by(desc(DomainModel.name))
    
    if param.limit > 0:
        query.limit(param.limit).offset(int(param.limit*param.page))
    vms = query.all()

    return {"count": count, "data": vms}


@app.get("/api/vms/{uuid}",response_model=DomainDetail, operation_id="get_vm")
def get_api_domain_uuid(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        uuid:str = None
    ):
    try:
        domain:DomainModel = db.query(DomainModel).filter(DomainModel.uuid==uuid).one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Not found domain")

    return domain


@app.get("/api/vms/vnc/{token}", operation_id="get_vnc_address")
def get_api_domain_vnc_token(
        token: str,
        db: Session = Depends(get_db),
    ):

    domain_model = db.query(DomainModel).filter(DomainModel.uuid==token).one()

    return { "host": domain_model.node.domain, "port": domain_model.vnc_port }