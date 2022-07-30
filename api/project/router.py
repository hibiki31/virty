from datetime import datetime, timedelta
from typing import List, Optional
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError
from fastapi import APIRouter, Depends, Request, HTTPException, Security, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from sqlalchemy.orm import Session, aliased
from sqlalchemy.exc import IntegrityError
from sqlalchemy import alias, func
from domain.models import DomainModel

from task.functions import TaskManager
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
        current_user: CurrentUser = Depends(get_current_user),
        admin: bool = False
    ):
    if admin:
        current_user.verify_scope(['admin'])

        rows = db.query(
            ProjectModel,
            func.sum(DomainModel.memory).label("used_memory_g"),
            func.sum(DomainModel.core)
        ).outerjoin(
            DomainModel
        ).group_by(ProjectModel.id).all()
        
        res = []

        for row in rows:
            res.append({
                **row[0].toDict(),
                'users':row[0].users,
                'used_memory_g': 0 if row[1] == None else row[0],
                'used_core': 0 if row[2] == None else row[0]
            })

        return res
    else:
        return db.query(ProjectModel).filter(ProjectModel.users.any(id=current_user.id)).all()

@app.post("")
def post_api_projects(
        request: PostProject, 
        bg: BackgroundTasks,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):
    task = TaskManager(db=db, bg=bg)
    task.select('post', 'project', 'root')
    task.commit(user=current_user, request=request)

    return task.model


@app.delete("")
def delete_api_projects(
        request: DeleteProject, 
        bg: BackgroundTasks,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):
    task = TaskManager(db=db, bg=bg)
    task.select('delete', 'project', 'root')
    task.commit(user=current_user, request=request)

    return task.model
    

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
