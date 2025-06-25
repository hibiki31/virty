from os.path import join
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from auth.router import CurrentUser, get_current_user
from mixin.database import get_db
from mixin.exception import raise_notfound
from mixin.log import setup_logger
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
    
    query = db.query(NetworkModel)
    
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

    return db.query(NetworkPoolModel).all()


@app.post("/pools")
def create_network_pool(
        model: NetworkPoolForCreate,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):
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
    pool_model = db.query(NetworkPoolModel).filter(NetworkPoolModel.id==model.pool_id).one()
    if model.port_name != None:
        port_model = db.query(NetworkPortgroupModel).filter(
            NetworkPortgroupModel.network_uuid==model.network_uuid,
            NetworkPortgroupModel.name==model.port_name).one()
        pool_model.ports.append(port_model)
    else:
        network_model = db.query(NetworkModel).filter(NetworkModel.uuid==model.network_uuid).one()
        pool_model.networks.append(network_model)
    db.commit()
    return True


@app.delete("/pools/{id}")
def delete_network_pool(
        id: int,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    cu.verify_scope(["admin.network.pools"])

    net_pool = db.query(NetworkPoolModel).filter(NetworkPoolModel.id==id).one_or_none()
    
    if net_pool == None:
        raise HTTPException(status_code=404, detail="network pool is not found")
    
    db.delete(net_pool)
    db.commit()

    return {"detail": "success"}


@app.get("/{uuid}", response_model=Network)
def get_network(
        uuid: str,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    try:
        network: NetworkModel = db.query(NetworkModel).filter(NetworkModel.uuid==uuid).one()
    except NoResultFound:
        raise_notfound(detial=f"Network not found: {uuid}")

    return network


@app.get("/{uuid}/xml",response_model=NetworkXML)
def get_network_xml(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        uuid:str = None
    ):
    try:
        with open(join(DATA_ROOT, "xml/network", f"{uuid}.xml")) as f:
            domain_xml = NetworkXML(xml=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Not found domain")

    return domain_xml