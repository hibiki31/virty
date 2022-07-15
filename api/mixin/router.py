from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from user.models import UserModel

from mixin.database import get_db
from mixin.log import setup_logger
from settings import API_VERSION

app = APIRouter(prefix="/api")
logger = setup_logger(__name__)


@app.get("/version")
def get_version(
        db: Session = Depends(get_db)
    ):
    initialized = (not db.query(UserModel).all() == [])

    return {"initialized": initialized, "version": API_VERSION}