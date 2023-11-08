from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from fastapi_camelcase import CamelModel
from typing import List, Optional
from pydantic import BaseModel, Field


from user.models import UserModel

from mixin.database import get_db
from mixin.log import setup_logger
from settings import API_VERSION

app = APIRouter(prefix="/api",tags=["mixin"])
logger = setup_logger(__name__)


class Version(CamelModel):
    initialized: bool
    version: str


@app.get("/version", response_model=Version, operation_id="get_version")
def get_version(
        db: Session = Depends(get_db)
    ):
    '''
    初期化済みか判定用
    '''
    initialized = (not db.query(UserModel).all() == [])

    return {"initialized": initialized, "version": API_VERSION}