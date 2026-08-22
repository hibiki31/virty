from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from auth.router import CurrentUser, get_current_user
from mixin.database import get_db
from mixin.log import setup_logger
from resource_authorization import allowed_flavor_ids, require_admin

from .models import FlavorModel
from .schemas import Flavor, FlavorForCreate, FlavorForQuery, FlavorPage

logger = setup_logger(__name__)
app = APIRouter(prefix="/api/flavors", tags=["flavors"])


@app.post("")
def create_flavor(
        request_model: FlavorForCreate,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    current_user.verify_scope(["flavor.manage"])
    require_admin(current_user)
    if db.query(FlavorModel).filter(FlavorModel.name==request_model.name).one_or_none():
        raise HTTPException(
            status_code=400,
            detail=f"{request_model.name} already exists."
        )
    
    flavor_model = FlavorModel(**request_model.model_dump())
    db.add(flavor_model)
    db.commit()
    return db.query(FlavorModel).filter(FlavorModel.id==flavor_model.id).all()


@app.get("", response_model=FlavorPage)
def get_flavors(
        param: FlavorForQuery = Depends(),
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    current_user.verify_scope(["flavor.read"])
    query = db.query(FlavorModel)
    allowed_flavors = allowed_flavor_ids(db, current_user)
    if allowed_flavors is not None:
        query = query.filter(FlavorModel.id.in_(allowed_flavors))
    
    if param.name_like:
        query = query.filter(FlavorModel.name.like(f'%{param.name_like}%'))
    
    count = query.count()
    if param.limit > 0:
        query = query.limit(param.limit).offset(int(param.limit*param.page))
    
    return {"count": count, "data": query.all()}


@app.delete("/{flavor_id}", response_model=Flavor)
def delete_flavor(
        flavor_id: int,
        eq: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    cu.verify_scope(["flavor.manage"])
    require_admin(cu)
    deleted_model = (
        db.query(FlavorModel).filter(FlavorModel.id == flavor_id).one_or_none()
    )
    if deleted_model is None:
        raise HTTPException(status_code=404, detail="Flavor not found")
    db.query(FlavorModel).filter(FlavorModel.id==flavor_id).delete()
    db.commit()

    return deleted_model
