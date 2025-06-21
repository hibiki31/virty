from os.path import join

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from auth.router import CurrentUser, get_current_user
from mixin.database import get_db
from mixin.log import setup_logger
from project.models import ProjectModel
from settings import DATA_ROOT

from .models import DomainModel
from .schemas import DomainDetail, DomainForQuery, DomainPage, DomainXML

app = APIRouter(prefix="/api/vms", tags=["vms"])

logger = setup_logger(__name__)


@app.get("",response_model=DomainPage)
def get_vms(
        param: DomainForQuery = Depends(),
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):

    query = db.query(DomainModel)

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

    query = query.order_by(DomainModel.name)
    count = query.count()
    
    if param.limit > 0:
        query = query.limit(param.limit).offset(int(param.limit*param.page))
    vms = query.all()

    return {"count": count, "data": vms}


@app.get("/{uuid}",response_model=DomainDetail, operation_id="get_vm")
def get_vm(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        uuid:str = None
    ):
    try:
        domain:DomainModel = db.query(DomainModel).filter(DomainModel.uuid==uuid).one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Not found domain")

    return domain


@app.get("/{uuid}/xml",response_model=DomainXML)
def get_vm_xml(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        uuid:str = None
    ):
    try:
        with open(join(DATA_ROOT, "xml/domain", f"{uuid}.xml")) as f:
            domain_xml = DomainXML(xml=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Not found domain")

    return domain_xml


@app.get("/vnc/{token}")
def get_vnc_address(
        token: str,
        db: Session = Depends(get_db),
    ):

    domain_model = db.query(DomainModel).filter(DomainModel.uuid==token).one()

    return { "host": domain_model.node.domain, "port": domain_model.vnc_port }