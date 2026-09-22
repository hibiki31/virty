from os.path import join
from typing import Any, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from auth.router import CurrentUser, get_current_user
from mixin.database import get_db
from mixin.exception import ApiError, ApiErrorCode
from mixin.log import setup_logger
from project.service import (
    ProjectConflictError,
    ProjectGrantNotFoundError,
    ensure_network_pool_deletable,
    ensure_network_pool_update_allowed,
)
from resource_authorization import (
    allowed_network_ids,
    allowed_network_port_names,
    allowed_network_pool_ids,
    get_authorized_network,
    is_global_inventory,
    require_admin,
)
from settings import DATA_ROOT

from .models import NetworkModel, NetworkPoolModel, NetworkPortgroupModel
from .schemas import (
    Network,
    NetworkForQuery,
    NetworkPage,
    NetworkPool,
    NetworkPoolDeleteResponse,
    NetworkPoolForCreate,
    NetworkPoolForReplace,
    NetworkPoolForUpdate,
    NetworkXML,
)

app = APIRouter(prefix="/api/networks", tags=["networks"])
logger = setup_logger(__name__)


def _network_response(
    model: NetworkModel,
    db: Session,
    current_user: CurrentUser,
    project_id: str | None,
    *,
    admin: bool = False,
) -> Network:
    """network全体grantがない場合は許可portgroupだけを応答へ残す。"""
    response = Network.model_validate(model)
    if is_global_inventory(current_user, admin=admin, project_id=project_id):
        return response
    allowed_port_names = allowed_network_port_names(
        db,
        current_user,
        model.uuid,
        project_id,
    )
    if allowed_port_names is None:
        return response
    return response.model_copy(update={
        "portgroups": [
            port
            for port in response.portgroups
            if port.name in allowed_port_names
        ],
    })


@app.get("", response_model=NetworkPage)
def get_networks(
        param: NetworkForQuery = Depends(),
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
) -> dict[str, Any]:
    current_user.verify_scope(["network.read"])
    query = db.query(NetworkModel)
    if not is_global_inventory(current_user, admin=param.admin, project_id=param.project_id):
        allowed_networks = allowed_network_ids(db, current_user, param.project_id)
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
    
    return {
        "count": count,
        "data": [
            _network_response(model, db, current_user, param.project_id, admin=param.admin)
            for model in query.all()
        ],
    }


@app.get("/pools", response_model=List[NetworkPool])
def get_network_pools(
        project_id: str | None = Query(default=None, alias="projectId"),
        admin: bool = False,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
) -> list[NetworkPoolModel]:
    current_user.verify_scope(["network.read"])
    query = db.query(NetworkPoolModel)
    if not is_global_inventory(current_user, admin=admin, project_id=project_id):
        allowed_pools = allowed_network_pool_ids(db, current_user, project_id)
        query = query.filter(NetworkPoolModel.id.in_(allowed_pools))
    return query.all()


@app.post("/pools", response_model=NetworkPool)
def create_network_pool(
        model: NetworkPoolForCreate,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
) -> NetworkPoolModel:
    current_user.verify_scope(["network.manage"])
    require_admin(current_user)
    pool_model = NetworkPoolModel(name=model.name)
    db.add(pool_model)
    db.commit()
    return pool_model


@app.patch("/pools", response_model=NetworkPool)
def update_network_pool(
        model: NetworkPoolForUpdate,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
) -> NetworkPoolModel:
    current_user.verify_scope(["network.manage"])
    require_admin(current_user)
    pool_model = db.get(NetworkPoolModel, model.pool_id)
    network_model = db.get(NetworkModel, model.network_uuid)
    if pool_model is None or network_model is None:
        raise ApiError(
            404,
            ApiErrorCode.NETWORK_OR_POOL_NOT_FOUND,
            "The network or network pool was not found.",
        )
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
    return pool_model


@app.put("/pools/{pool_id}", response_model=NetworkPool)
def replace_network_pool(
    pool_id: int,
    model: NetworkPoolForReplace,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> NetworkPoolModel:
    """networkとportgroupの構成を完全置換する。"""
    current_user.verify_scope(["network.manage"])
    require_admin(current_user)
    network_ids = set(model.network_uuids)
    port_keys = {(port.network_uuid, port.port_name) for port in model.ports}
    networks = db.query(NetworkModel).filter(NetworkModel.uuid.in_(network_ids)).all()
    ports = db.query(NetworkPortgroupModel).filter(
        NetworkPortgroupModel.network_uuid.in_({key[0] for key in port_keys}),
    ).all()
    selected_ports = [port for port in ports if (port.network_uuid, port.name) in port_keys]
    if {network.uuid for network in networks} != network_ids or {
        (port.network_uuid, port.name) for port in selected_ports
    } != port_keys:
        raise ApiError(404, ApiErrorCode.NETWORK_OR_PORT_NOT_FOUND, "The network or port was not found.")
    try:
        pool = ensure_network_pool_update_allowed(db, pool_id, network_ids, port_keys)
    except ProjectGrantNotFoundError as exc:
        raise ApiError(404, ApiErrorCode.NETWORK_POOL_NOT_FOUND, "The network pool was not found.") from exc
    except ProjectConflictError as exc:
        raise ApiError(409, ApiErrorCode.NETWORK_POOL_IN_USE, "The network pool is still in use.") from exc
    pool.networks = networks
    pool.ports = selected_ports
    db.commit()
    return pool


@app.delete("/pools/{id}", response_model=NetworkPoolDeleteResponse)
def delete_network_pool(
        id: int,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
) -> NetworkPoolDeleteResponse:
    cu.verify_scope(["network.manage"])
    require_admin(cu)
    try:
        net_pool = ensure_network_pool_deletable(db, id)
    except ProjectGrantNotFoundError as error:
        raise ApiError(
            404,
            ApiErrorCode.NETWORK_POOL_NOT_FOUND,
            "The network pool was not found.",
        ) from error
    except ProjectConflictError as error:
        raise ApiError(
            409,
            ApiErrorCode.NETWORK_POOL_IN_USE,
            "The network pool is still in use.",
        ) from error
    
    db.delete(net_pool)
    db.commit()

    return NetworkPoolDeleteResponse(deleted=True, id=id)


@app.get("/{uuid}", response_model=Network)
def get_network(
        uuid: str,
        project_id: str | None = Query(default=None, alias="projectId"),
        admin: bool = False,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
) -> Network:
    current_user.verify_scope(["network.read"])
    model = get_authorized_network(db, uuid, current_user, project_id, admin=admin)
    return _network_response(model, db, current_user, project_id, admin=admin)


@app.get("/{uuid}/xml",response_model=NetworkXML)
def get_network_xml(
        uuid: str,
        project_id: str | None = Query(default=None, alias="projectId"),
        admin: bool = False,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
) -> NetworkXML:
    current_user.verify_scope(["network.read"])
    get_authorized_network(db, uuid, current_user, project_id, admin=admin)
    if not is_global_inventory(current_user, admin=admin, project_id=project_id) and allowed_network_port_names(
        db,
        current_user,
        uuid,
        project_id,
    ) is not None:
        # XMLはnetwork全体と全portgroupを含むため、port単位grantでは公開しない。
        raise ApiError(
            404,
            ApiErrorCode.NETWORK_XML_NOT_FOUND,
            "The network XML was not found.",
        )
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
