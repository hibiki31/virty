from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from auth.router import CurrentUser, get_current_user
from mixin.database import get_db
from mixin.exception import ApiError, ApiErrorCode
from mixin.log import setup_logger
from resource_authorization import require_admin
from task.functions import TaskManager
from task.schemas import Task

from .schemas import ProjectForCreate
from .service import (
    ProjectConflictError,
    ProjectNotFoundError,
    ensure_project_deletable,
)

app = APIRouter(prefix="/api/tasks/projects", tags=["projects-tasks"])
logger = setup_logger(__name__)


@app.post("", response_model=list[Task])
def create_project(
    body: ProjectForCreate,
    req: Request,
    cu: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Task]:
    cu.verify_scope(["project.manage"])
    require_admin(cu)
    task = TaskManager(db=db)
    task.select(method="post", resource="project", object="root")
    task.commit(user=cu, req=req, body=body)
    return [Task.model_validate(task.model)]


@app.delete("/{project_id}", response_model=list[Task])
def delete_project(
    project_id: str,
    req: Request,
    cu: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Task]:
    cu.verify_scope(["project.manage"])
    require_admin(cu)
    try:
        ensure_project_deletable(db, project_id)
    except ProjectNotFoundError as error:
        raise ApiError(
            status.HTTP_404_NOT_FOUND,
            ApiErrorCode.PROJECT_NOT_FOUND,
            "The project was not found.",
        ) from error
    except ProjectConflictError as error:
        raise ApiError(
            status.HTTP_409_CONFLICT,
            ApiErrorCode.PROJECT_NOT_EMPTY,
            "The project still has dependent resources.",
        ) from error

    task = TaskManager(db=db)
    task.select(method="delete", resource="project", object="root")
    task.commit(user=cu, req=req, param={"project_id": project_id})
    return [Task.model_validate(task.model)]
