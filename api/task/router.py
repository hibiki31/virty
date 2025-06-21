import hashlib
import time
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session

from auth.router import CurrentUser, get_current_user
from mixin.database import get_db
from task.models import TaskModel
from task.schemas import Task, TaskForQuery, TaskIncomplete, TaskPage

app = APIRouter(
    prefix="/api/tasks",
    tags=["tasks"]
)


@app.get("", response_model=TaskPage)
def get_tasks(
        param: TaskForQuery = Depends(),
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        admin: bool = False,
    ):

    query = db.query(TaskModel)

    if admin:
        current_user.verify_scope(["admin.tasks"])
    else:
        query.filter(TaskModel.user_id==current_user.id)

    if param.resource:
        query = query.filter(TaskModel.resource==param.resource)
    if param.object:
        query = query.filter(TaskModel.object==param.object)
    if param.method:
        query = query.filter(TaskModel.method==param.method)
    if param.status:
        if param.status == "incomplete":
            query = query.filter(or_(
                TaskModel.status=="wait",
                TaskModel.status=="init",
                TaskModel.status=="start",
            ))
        else:
            query = query.filter(TaskModel.status==param.status)
    
    count = query.count()

    query = query.order_by(desc(TaskModel.post_time))
    if param.limit > 0:
        task = query.limit(param.limit).offset(int(param.limit*param.page)).all()
    
    return { "count": count, "data": task }


@app.delete("", response_model=List[Task])
def delete_tasks(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
    current_user.verify_scope(["admin"])
    model = db.query(TaskModel).all()
    db.query(TaskModel).delete()
    db.commit()

    return model


@app.get("/incomplete", response_model=TaskIncomplete)
def get_incomplete_tasks(
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
        task_hash = str(hashlib.md5(str([j.uuid+j.status for j in task_model]).encode()).hexdigest())
        
        if task_hash != hash:
            break
        time.sleep(0.5)       

    return {"hash": task_hash, "count": task_count, "uuids": [j.uuid for j in task_model]}


@app.get("/{uuid}", response_model=Task)
def get_task(
        uuid: str,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
    task = db.query(TaskModel).filter(TaskModel.uuid==uuid).one_or_none()
    if task is None:
        raise HTTPException(status_code=404, detail="task uuid not found")
    
    return task