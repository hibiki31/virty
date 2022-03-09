from datetime import datetime
from distutils import core
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from flavor.models import FlavorModel

from mixin.database import get_db
from mixin.log import setup_logger
from settings import IS_DEV
from storage.models import StoragePoolModel

from .models import *
from .schemas import *
from auth.router import CurrentUser, get_current_user, pwd_context

logger = setup_logger(__name__)
app = APIRouter(
    prefix="/api/tickets",
    tags=["tickets"],
)


@app.post("")
def post_api_tickets(
        request_model: PostTicket,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    ticket_model = TicketModel(
        core=request_model.core,
        memory=request_model.memory,
        user_installable=request_model.user_installable,
        isolated_networks=request_model.isolated_networks
    )
    
    for pool_id in request_model.network_pools:
        ticket_model.network_pools.append(
            db.query(NetworkPoolModel).filter(NetworkPoolModel.id==pool_id).one()
        )
    
    for pool_id in request_model.storage_pools:
        ticket_model.storage_pools.append(
            db.query(StoragePoolModel).filter(StoragePoolModel.id==pool_id).one()
        )
    
    for flavor_id in request_model.flavors:
        ticket_model.flavors.append(
            db.query(FlavorModel).filter(FlavorModel.id==flavor_id).one()
        )

    db.add(ticket_model)
    db.commit()
    return db.query(TicketModel).filter(TicketModel.id==ticket_model.id).all()


@app.get("",response_model=List[GetTicket])
def get_api_tickets(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        admin: bool = False
    ):
    query = db.query(TicketModel)

    if admin:
        current_user.verify_scope(scopes=["admin"])
    else:
        query = query.filter(TicketModel.users.any(id=current_user.id))

    return query.all()


@app.post("/issuances")
def post_api_issuances(
        request_model: PostIssuance,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    model = IssuanceModel(
        date = datetime.now(),
        issued_by = current_user.id,
        user_id = request_model.user_id,
        ticket_id = request_model.ticket_id
    )

    db.add(model)
    db.commit()
    return db.query(IssuanceModel).filter(IssuanceModel.id==model.id).one()

@app.get("/issuances",response_model=List[GetIssuance])
def get_api_tickets(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        admin: bool = False
    ):
    query = db.query(IssuanceModel)

    if admin:
        current_user.verify_scope(scopes=["admin"])
    else:
        query = query.filter(IssuanceModel.user_id==current_user.id)

    return query.all()