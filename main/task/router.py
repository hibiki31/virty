from fastapi import APIRouter, Depends
from starlette.requests import Request
from sqlalchemy.orm import Session
from sqlalchemy import desc
from mixin.database import get_db
from auth.router import get_current_user, CurrentUser

from .models import *
from .schemas import *


app = APIRouter()


@app.get("/api/tasks", tags=["task"], response_model=List[TaskSelect])
async def get_api_tasks(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    task = db.query(TaskModel).order_by(desc(TaskModel.post_time)).all()
    
    return task


@app.delete("/api/tasks", tags=["task"], response_model=List[TaskSelect])
async def delete_api_tasks(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
    model = db.query(TaskModel).all()
    db.query(TaskModel).delete()
    db.commit()

    return model