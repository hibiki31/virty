from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from auth.router import CurrentUser, get_current_user
from mixin.database import get_db
from mixin.log import setup_logger
from project.schemas import (
    ProjectForCreate,
)
from task.functions import TaskManager

app = APIRouter(prefix="/api/tasks/projects", tags=["projects-tasks"])
logger = setup_logger(__name__)


@app.post("")
def create_project(
        body: ProjectForCreate,
        req: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    task = TaskManager(db=db)
    task.select(method='post', resource='project', object='root')
    task.commit(user=cu, req=req, body=body)

    return [task.model]


@app.delete("/{project_id}")
def delete_project(
        project_id: str,
        req: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    task = TaskManager(db=db)
    task.select(method='delete', resource='project', object='root')
    task.commit(user=cu, req=req, param={"project_id": project_id})

    return [task.model]
    
