from os.path import join
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.router import CurrentUser, get_current_user
from mixin.database import get_db
from mixin.exception import ApiError, ApiErrorCode
from mixin.log import setup_logger
from resource_authorization import (
    allowed_network_ids,
    allowed_network_pool_ids,
    get_authorized_network,
    get_authorized_network_pool,
    require_admin,
)
from settings import DATA_ROOT

from .models import NetworkModel, NetworkPoolModel, NetworkPortgroupModel
from .schemas import (
    Network,
    NetworkForQuery,
    NetworkPage,
    NetworkPool,
    NetworkPoolForCreate,
    NetworkPoolForUpdate,
    NetworkXML,
)

app = APIRouter(prefix="/api/networks", tags=["networks"])
logger = setup_logger(__name__)


@app.get("", response_model=NetworkPage)
def get_networks(
        param: NetworkForQuery = Depends(),
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    current_user.verify_scope(["network.read"])
    query = db.query(NetworkModel)
    allowed_networks = allowed_network_ids(db, current_user)
    if allowed_networks is not None:
        query = query.filter(NetworkModel.uuid.in_(allowed_networks))
    
    if param.name_like:
        query = query.filter(NetworkModel.name.like(f'%{param.name_like}%'))
    
    if param.node_name_like:
        query = query.filter(NetworkModel.node_name.like(f'%{param.node_name_like}%'))
    
    if param.type:
        query = query.filter(NetworkModel.type==param.type)
    
    query = query.order_by(NetworkModel.name)
    count = query.count()
    if param.limit > 0:
        query = query.limit(param.limit).offset(int(param.limit*param.page))
    
    return { "count": count, "data": query.all() }


@app.get("/pools", response_model=List[NetworkPool])
def get_network_pools(
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
):
    current_user.verify_scope(["network.read"])
    query = db.query(NetworkPoolModel)
    allowed_pools = allowed_network_pool_ids(db, current_user)
    if allowed_pools is not None:
        query = query.filter(NetworkPoolModel.id.in_(allowed_pools))
    return query.all()


@app.post("/pools")
def create_network_pool(
        model: NetworkPoolForCreate,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
):
    current_user.verify_scope(["network.manage"])
    require_admin(current_user)
    pool_model = NetworkPoolModel(name=model.name)
    db.add(pool_model)
    db.commit()
    return True


@app.patch("/pools")
def update_network_pool(
        model: NetworkPoolForUpdate,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
):
    current_user.verify_scope(["network.manage"])
    pool_model = get_authorized_network_pool(db, model.pool_id, current_user)
    network_model = get_authorized_network(db, model.network_uuid, current_user)
    if model.port_name is not None:
        port_model = db.query(NetworkPortgroupModel).filter(
            NetworkPortgroupModel.network_uuid==model.network_uuid,
            NetworkPortgroupModel.name==model.port_name).one_or_none()
        if port_model is None:
            raise ApiError(
                404,
                ApiErrorCode.NETWORK_PORT_NOT_FOUND,
                "The network port was not found.",
            )
        pool_model.ports.append(port_model)
    else:
        pool_model.networks.append(network_model)
    db.commit()
    return True


@app.delete("/pools/{id}")
def delete_network_pool(
        id: int,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    cu.verify_scope(["network.manage"])
    net_pool = get_authorized_network_pool(db, id, cu)
    
    db.delete(net_pool)
    db.commit()

    return {"detail": "success"}


@app.get("/{uuid}", response_model=Network)
def get_network(
        uuid: str,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    current_user.verify_scope(["network.read"])
    return get_authorized_network(db, uuid, current_user)


@app.get("/{uuid}/xml",response_model=NetworkXML)
def get_network_xml(
        uuid: str,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    current_user.verify_scope(["network.read"])
    get_authorized_network(db, uuid, current_user)
    try:
        with open(join(DATA_ROOT, "xml/network", f"{uuid}.xml")) as f:
            domain_xml = NetworkXML(xml=f.read())
    except FileNotFoundError:
        raise ApiError(
            404,
            ApiErrorCode.NETWORK_XML_NOT_FOUND,
            "The network XML was not found.",
        )

    return domain_xml
