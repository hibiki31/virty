from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from auth.router import CurrentUser, get_current_user
from mixin.database import get_db
from mixin.log import setup_logger

from .models import FlavorModel
from .schemas import Flavor, FlavorForCreate, FlavorForQuery, FlavorPage

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
    
    flavor_model = FlavorModel(**request_model.model_dump())
    db.add(flavor_model)
    db.commit()
    return db.query(FlavorModel).filter(FlavorModel.id==flavor_model.id).all()


@app.get("", response_model=FlavorPage, operation_id="get_flavors")
def get_api_flavors(
        param: FlavorForQuery = Depends(),
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
    
    query = db.query(FlavorModel)
    
    if param.name_like:
        query = query.filter(FlavorModel.name.like(f'%{param.name_like}%'))
    
    count = query.count()
    if param.limit > 0:
        query = query.limit(param.limit).offset(int(param.limit*param.page))
    
    return {"count": count, "data": query.all()}


@app.delete("/{flavor_id}", response_model=Flavor, operation_id="delete_flavor")
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