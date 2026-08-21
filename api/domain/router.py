from os.path import join

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from auth.router import CurrentUser, get_current_user
from mixin.database import get_db
from mixin.log import setup_logger
from network.models import NetworkModel
from project.models import ProjectModel
from settings import DATA_ROOT
from storage.models import ImageModel, StorageModel

from .models import DomainModel
from .schemas import DomainDetail, DomainForQuery, DomainPage, DomainXML

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
    ):

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
    try:
        domain:DomainModel = db.query(DomainModel).filter(DomainModel.uuid==uuid).one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Not found domain")

    return _get_domain_detail(domain, db)


@app.get("/{uuid}/xml",response_model=DomainXML)
def get_vm_xml(
        uuid: str,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
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
