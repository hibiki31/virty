from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
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


@app.post("")
def post_api_flavors(
        request_model: PostFlavor,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    flavor_model = FlavorModel(**request_model.dict())
    db.add(flavor_model)
    db.commit()
    return db.query(FlavorModel).filter(FlavorModel.id==flavor_model.id).all()


@app.get("", response_model=List[GetFlavor])
def get_api_flavors(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    return db.query(FlavorModel).all()