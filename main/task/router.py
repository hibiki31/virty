from fastapi import APIRouter, Depends
from starlette.requests import Request
from sqlalchemy.orm import Session
from sqlalchemy import desc
from mixin.database import get_db
from auth.router import get_current_user, CurrentUser

from .models import *
from .schemas import *

import asyncio


app = APIRouter()


@app.get("/api/tasks", tags=["task"], response_model=List[TaskSelect])
async def get_api_tasks(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    task = db.query(TaskModel).order_by(desc(TaskModel.post_time)).all()
    
    return task


@app.get("/api/tasks/{uuid}", tags=["task"], response_model=TaskSelect)
async def get_api_tasks(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        uuid: str = None,
        polling: bool = False
    ):
    while True:
        try:
            task: TaskModel = db.query(TaskModel).filter(TaskModel.uuid==uuid).one()
        except:
            raise HTTPException(status_code=400, detail="task not fund")
        if task.status == "finish":
            break
        if polling:
            await asyncio.sleep(0.5)
            db.commit() # こいつないと、他が加えたDBの変更入らない
            continue
        break
    
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