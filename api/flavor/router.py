from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from mixin.database import get_db
from mixin.log import setup_logger
from settings import IS_DEV

from .models import *
from .schemas import *
from auth.router import CurrentUser, get_current_user, pwd_context

logger = setup_logger(__name__)
app = APIRouter(
    prefix="/api/flavors",
    tags=["flavors"],
)


@app.post("", operation_id="create_flavor")
def post_api_flavors(
        request_model: FlavorForCreate,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    
    if db.query(FlavorModel).filter(FlavorModel.name==request_model.name).one_or_none():
        raise HTTPException(
            status_code=400,
            detail=f"{request_model.name} already exists."
        )
    
    flavor_model = FlavorModel(**request_model.dict())
    db.add(flavor_model)
    db.commit()
    return db.query(FlavorModel).filter(FlavorModel.id==flavor_model.id).all()


@app.get("", response_model=Flavor, operation_id="get_flavors")
def get_api_flavors(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        limit: int = 25,
        page: int = 0,
        name: str = None
    ):
    
    query = db.query(FlavorModel)
    
    if name:
        query = query.filter(FlavorModel.name.like(f'%{name}%'))
    
    count = query.count()
    query = query.limit(limit).offset(int(limit*page))
    
    return {"count": count, "data": query.all()}


@app.delete("/{flavor_id}", response_model=FlavorPage, operation_id="delete_flavor")
def delete_flavors(
        flavor_id: int,
        eq: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
    
    deleted_model = db.query(FlavorModel).filter(FlavorModel.id==flavor_id).one()
    db.query(FlavorModel).filter(FlavorModel.id==flavor_id).delete()
    db.commit()

    return deleted_model