from datetime import datetime, timedelta
from typing import List, Optional
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError
from fastapi import APIRouter, Depends, Request, HTTPException, Security, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from task.function import PostTask
from mixin.database import get_db
from mixin.log import setup_logger
from settings import IS_DEV

from user.models import *
from project.models import *
from .schemas import *
from auth.router import CurrentUser, get_current_user

logger = setup_logger(__name__)
app = APIRouter(
    prefix="/api/projects",
    tags=["project"],
)



@app.get("", response_model=List[ProjectSelect])
def get_api_projects(
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):
    projects = []
    for project in db.query(ProjectModel).all():
        project.users
        projects.append(project)
    return projects


@app.post("")
def post_api_projects(
        request: PostProject, 
        bg: BackgroundTasks,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):

    post_task = PostTask(db=db, user=current_user, model=request)
    task_model = post_task.commit("project","root","post", bg)
    return task_model


@app.put("")
def put_api_projects(
        request: ProjectPatch, 
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):
    try:
        project: ProjectModel = db.query(ProjectModel).filter(ProjectModel.id==request.project_id).one()
        user: UserModel = db.query(UserModel).filter(UserModel.id==request.user_id).one()
    except:
        raise  HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The specified value is invalid"
        )

    project.users.append(user)

    db.merge(project)
    db.commit()

    project: ProjectModel = db.query(ProjectModel).filter(ProjectModel.id==request.project_id).one()

    return project


@app.delete("")
def delete_api_projects(
        request: ProjectPatch, 
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):
    try:
        project: ProjectModel = db.query(ProjectModel).filter(ProjectModel.project_id==request.project_id).one()
        users = []
    except:
        raise  HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The specified value is invalid"
        )

    for user in project.users:
        if user.user_id == request.user_id:
            continue
        else:
            users.append(user)
        
    project.users = users
    db.merge(project)
    db.commit()

    project: ProjectModel = db.query(ProjectModel).filter(ProjectModel.project_id==request.project_id).one()

    return project