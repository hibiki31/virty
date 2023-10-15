from asyncio.log import logger
from fastapi import APIRouter, Depends, HTTPException
from starlette.websockets import WebSocket
from starlette.requests import Request
from starlette.endpoints import WebSocketEndpoint
from starlette.routing import Route, WebSocketRoute
from sqlalchemy.orm import Session
from sqlalchemy import desc, true
from mixin.database import get_db
from auth.router import get_current_user, CurrentUser

from .models import *
from .schemas import *

import time
import hashlib


app = APIRouter(
    prefix="/api",
    tags=["tasks"]
)


@app.get("/tasks", response_model=TaskPagesnation)
def get_tasks(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        admin: bool = False,
        limit: int = 25,
        page: int = 0,
        resource: str = None,
        object: str = None,
        method: str = None,
        status: str = None,
    ):

    query = db.query(TaskModel)

    if admin:
        current_user.verify_scope(["admin.tasks"])
    else:
        query.filter(TaskModel.user_id==current_user.id)

    if resource:
        query = query.filter(TaskModel.resource==resource)
    if object:
        query = query.filter(TaskModel.object==object)
    if method:
        query = query.filter(TaskModel.method==method)
    if status:
        query = query.filter(TaskModel.status==status)
    
    count = query.count()

    query = query.order_by(desc(TaskModel.post_time))
    task = query.limit(limit).offset(int(limit*page)).all()

    return { "count": count, "data": task }


@app.delete("/tasks/", response_model=List[Task])
def delete_tasks(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
    current_user.verify_scope(["admin"])
    model = db.query(TaskModel).all()
    db.query(TaskModel).delete()
    db.commit()

    return model


@app.get("/tasks/incomplete", response_model=TaskIncomplete)
def get_tasks_incomplete(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        hash: str = None,
        admin: bool = False
    ):

    task_hash = None
    task_count = 0
    task_model = None

    if admin:
        current_user.verify_scope(["admin.tasks"])
 
    for i in range(0,20):
        query = db.query(TaskModel)
        if not admin:
            query = query.filter(TaskModel.user_id==current_user.id)
    
        task_model = query.filter(TaskModel.status!="error")\
            .filter(TaskModel.status!="lost")\
            .filter(TaskModel.status!="finish").all()        
        
        task_count = len(task_model)
        task_hash = str(hashlib.md5(str([j.uuid for j in task_model]).encode()).hexdigest())
        
        if task_hash != hash:
            break
        time.sleep(0.5)       

    return {"hash": task_hash, "count": task_count, "uuids": [j.uuid for j in task_model]}


@app.get("/tasks/{uuid}", response_model=Task)
def get_tasks(
        uuid: str,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
    task = db.query(TaskModel)\
            .filter(TaskModel.uuid==uuid).one_or_none()
    
    if task == None:
        raise HTTPException(status_code=404, detail="task uuid not found")
    
    return task