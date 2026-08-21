import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from os.path import join

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import or_
from sqlalchemy.orm import Session

from auth.router import CurrentUser, get_current_user
from mixin.database import get_db
from mixin.log import setup_logger
from module.xmllib import redact_domain_xml_secrets
from project.models import ProjectModel
from settings import DATA_ROOT

from .authorization import get_authorized_domain
from .models import DomainConsoleTicketModel, DomainModel
from .schemas import (
    DomainConsoleTicket,
    DomainDetail,
    DomainForQuery,
    DomainPage,
    DomainXML,
)

app = APIRouter(prefix="/api/vms", tags=["vms"])

logger = setup_logger(__name__)


@app.get("",response_model=DomainPage)
def get_vms(
        param: DomainForQuery = Depends(),
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    current_user.verify_scope(["vm.read"])
    query = db.query(DomainModel)

    if param.admin:
        current_user.verify_scope(scopes=["admin"])
    else:
        query = query.filter(or_(
                DomainModel.owner_user_id==current_user.id,
                DomainModel.owner_project.has(ProjectModel.users.any(username=current_user.id))
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
        uuid: str,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
    current_user.verify_scope(["vm.read"])
    return get_authorized_domain(db, uuid, current_user)


@app.get("/{uuid}/xml",response_model=DomainXML)
def get_vm_xml(
        uuid: str,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    current_user.verify_scope(["vm.read"])
    get_authorized_domain(db, uuid, current_user)
    try:
        with open(join(DATA_ROOT, "xml/domain", f"{uuid}.xml")) as f:
            domain_xml = DomainXML(xml=redact_domain_xml_secrets(f.read()))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Not found domain")

    return domain_xml


@app.post("/{uuid}/console-ticket", response_model=DomainConsoleTicket)
def create_console_ticket(
    uuid: str,
    response: Response,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """noVNC resolverだけが一度消費できる短命opaque ticketを発行する。"""
    current_user.verify_scope(["vm.read"])
    get_authorized_domain(db, uuid, current_user)
    now = datetime.now(UTC)
    expires_in = 60
    token = secrets.token_urlsafe(32)
    db.query(DomainConsoleTicketModel).filter(
        DomainConsoleTicketModel.expires_at <= now,
    ).delete(synchronize_session=False)
    db.add(
        DomainConsoleTicketModel(
            token_hash=hashlib.sha256(token.encode("ascii")).hexdigest(),
            domain_uuid=uuid,
            actor_id=current_user.id,
            created_at=now,
            expires_at=now + timedelta(seconds=expires_in),
        )
    )
    db.commit()
    response.headers["Cache-Control"] = "no-store"
    return DomainConsoleTicket(token=token, expires_in=expires_in)


@app.get("/vnc/{token}", include_in_schema=False)
def get_vnc_address(
        token: str,
        db: Session = Depends(get_db),
):
    now = datetime.now(UTC)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    ticket = db.query(DomainConsoleTicketModel).filter(
        DomainConsoleTicketModel.token_hash == token_hash,
    ).with_for_update().one_or_none()
    if ticket is None or ticket.used_at is not None:
        raise HTTPException(status_code=401, detail="Invalid console ticket")
    expires_at = ticket.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if expires_at <= now:
        raise HTTPException(status_code=401, detail="Invalid console ticket")

    domain_model = db.query(DomainModel).filter(
        DomainModel.uuid == ticket.domain_uuid,
    ).one_or_none()
    if domain_model is None:
        raise HTTPException(status_code=404, detail="VM not found")

    ticket.used_at = now
    db.commit()
    return { "host": domain_model.node.domain, "port": domain_model.vnc_port }
