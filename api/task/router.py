import hashlib
import time
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, not_, or_
from sqlalchemy.orm import Session

from auth.router import CurrentUser, get_current_user
from mixin.database import get_db
from task.models import TaskModel
from task.schemas import (
    Task,
    TaskForQuery,
    TaskIncomplete,
    TaskIncompleteForQuery,
    TaskPage,
)

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


EXCLUDED_STATUSES = ("error", "lost", "finish")

def _calc_hash(rows: list[tuple[str, str]]) -> str:
    # rows=(uuid,status)
    joined = ";".join(f"{u}:{s}" for u, s in rows)
    return hashlib.md5(joined.encode()).hexdigest()

@app.get("/incomplete", response_model=TaskIncomplete)
def get_incomplete_tasks(
        param: TaskIncompleteForQuery = Depends(),
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):

    if param.admin:
        current_user.verify_scope(["admin.tasks"])
    
    base_query = (
        db.query(TaskModel.uuid, TaskModel.status)
          .filter(not_(TaskModel.status.in_(EXCLUDED_STATUSES)))
          .order_by(TaskModel.uuid)
    )
    
    if not param.admin:
        base_query = base_query.filter(TaskModel.user_id==current_user.id)
 
    for _ in range(20):
        rows = base_query.all()                      # uuid,status のみ取得
        new_hash = _calc_hash(rows)

        if new_hash != param.reference_hash:
            return {
                "hash": new_hash,
                "count": len(rows),
                "uuids": [u for u, _ in rows],
            }

        time.sleep(0.5)  # 同期版を維持。非同期なら asyncio.sleep()

    # 変更なしのままタイムアウト
    return {
        "hash": new_hash,
        "count": len(rows),
        "uuids": [u for u, _ in rows],
    }


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