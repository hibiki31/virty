import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from os.path import join
from typing import Any

from fastapi import APIRouter, Depends, Response
from sqlalchemy import or_
from sqlalchemy.orm import Session

from auth.router import CurrentUser, get_current_user
from mixin.database import get_db
from mixin.exception import ApiError, ApiErrorCode
from mixin.log import setup_logger
from module.xmllib import redact_domain_xml_secrets
from network.models import NetworkModel
from resource_authorization import (
    get_authorized_project,
    get_member_project,
    is_global_inventory,
)
from settings import DATA_ROOT
from storage.models import ImageModel, StorageModel

from .authorization import can_access_domain, get_authorized_domain
from .models import DomainConsoleTicketModel, DomainModel
from .service import (
    DomainProjectMoveConflictError,
    DomainProjectMoveNotFoundError,
    move_domain_to_project,
)
from .schemas import (
    DomainConsoleTicket,
    DomainDetail,
    DomainForQuery,
    DomainPage,
    DomainProjectForUpdate,
    DomainXML,
)

app = APIRouter(prefix="/api/vms", tags=["vms"])

logger = setup_logger(__name__)


def _get_domain_detail(domain: DomainModel, db: Session) -> DomainDetail:
    detail = DomainDetail.model_validate(domain)

    networks = db.query(NetworkModel).filter(
        NetworkModel.node_name == domain.node_name,
    ).all()
    networks_by_name = {network.name: network for network in networks}
    networks_by_bridge = {
        network.bridge: network for network in networks if network.bridge
    }
    interfaces = []
    for interface in detail.interfaces or []:
        network = None
        if interface.network:
            network = networks_by_name.get(interface.network)
        if network is None and interface.bridge:
            network = networks_by_bridge.get(interface.bridge)

        if network is not None:
            interface = interface.model_copy(update={
                "network": network.name,
                "network_uuid": network.uuid,
            })
        interfaces.append(interface)

    drive_sources = {
        drive.source for drive in detail.drives or [] if drive.source is not None
    }
    images_by_path: dict[str, ImageModel] = {}
    if drive_sources:
        images = db.query(ImageModel).join(
            StorageModel,
            ImageModel.storage_uuid == StorageModel.uuid,
        ).filter(
            StorageModel.node_name == domain.node_name,
            ImageModel.path.in_(drive_sources),
        ).all()
        images_by_path = {image.path: image for image in images}

    drives = []
    for drive in detail.drives or []:
        image = images_by_path.get(drive.source) if drive.source else None
        if image is not None:
            drive = drive.model_copy(update={"capacity_gb": image.capacity})
        drives.append(drive)

    return detail.model_copy(update={
        "interfaces": interfaces if detail.interfaces is not None else None,
        "drives": drives if detail.drives is not None else None,
    })


@app.get("",response_model=DomainPage)
def get_vms(
        param: DomainForQuery = Depends(),
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
) -> dict[str, Any]:
    current_user.verify_scope(["vm.read"])
    query = db.query(DomainModel)

    if not is_global_inventory(current_user, admin=param.admin, project_id=param.project_id):
        query = query.filter(or_(
            DomainModel.owner_user_id == current_user.id,
            DomainModel.owner_project_id.in_(current_user.projects),
        ))
    if param.project_id is not None:
        get_authorized_project(db, param.project_id, current_user)
        query = query.filter(DomainModel.owner_project_id == param.project_id)
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
        admin: bool = False,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> DomainDetail:
    current_user.verify_scope(["vm.read"])
    domain = get_authorized_domain(db, uuid, current_user, admin=admin)
    return _get_domain_detail(domain, db)


@app.patch("/{uuid}/project", response_model=DomainDetail)
def update_vm_project(
        uuid: str,
        request: DomainProjectForUpdate,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    """VMを、接続済みresourceを利用できるprojectへ移動する。"""
    current_user.verify_scope(["vm.project"])
    get_authorized_domain(db, uuid, current_user)
    get_member_project(db, request.project_id, current_user)
    try:
        domain = move_domain_to_project(
            db,
            domain_uuid=uuid,
            destination_project_id=request.project_id,
            authorize_locked=lambda locked_domain, destination: (
                can_access_domain(current_user, locked_domain)
                and destination.id in current_user.projects
            ),
        )
    except DomainProjectMoveNotFoundError as error:
        raise ApiError(
            404,
            ApiErrorCode.VM_OR_PROJECT_NOT_FOUND,
            "The VM or project was not found.",
        ) from error
    except DomainProjectMoveConflictError as error:
        raise ApiError(
            409,
            ApiErrorCode.VM_PROJECT_RESOURCE_CONFLICT,
            "VM resources are outside the destination project grants.",
        ) from error
    db.commit()
    db.refresh(domain)
    return _get_domain_detail(domain, db)


@app.get("/{uuid}/xml",response_model=DomainXML)
def get_vm_xml(
        uuid: str,
        admin: bool = False,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
) -> DomainXML:
    current_user.verify_scope(["vm.read"])
    get_authorized_domain(db, uuid, current_user, admin=admin)
    try:
        with open(join(DATA_ROOT, "xml/domain", f"{uuid}.xml")) as f:
            domain_xml = DomainXML(xml=redact_domain_xml_secrets(f.read()))
    except FileNotFoundError:
        raise ApiError(
            404,
            ApiErrorCode.VM_XML_NOT_FOUND,
            "The VM XML was not found.",
        )

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
        raise ApiError(
            401,
            ApiErrorCode.INVALID_CONSOLE_TICKET,
            "The console ticket is invalid or has already been used.",
        )
    expires_at = ticket.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if expires_at <= now:
        raise ApiError(
            401,
            ApiErrorCode.INVALID_CONSOLE_TICKET,
            "The console ticket is invalid or has expired.",
        )

    domain_model = db.query(DomainModel).filter(
        DomainModel.uuid == ticket.domain_uuid,
    ).one_or_none()
    if domain_model is None:
        raise ApiError(404, ApiErrorCode.VM_NOT_FOUND, "The VM was not found.")

    ticket.used_at = now
    db.commit()
    return { "host": domain_model.node.domain, "port": domain_model.vnc_port }
