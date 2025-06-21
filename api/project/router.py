from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from auth.router import CurrentUser, get_current_user
from domain.models import DomainModel
from mixin.database import get_db
from mixin.log import setup_logger
from project.models import ProjectModel
from project.schemas import (
    ProjectForQuery,
    ProjectForUpdate,
    ProjectPage,
)
from user.models import UserModel

app = APIRouter(prefix="/api/projects", tags=["projects"])
logger = setup_logger(__name__)


@app.get("", response_model=ProjectPage)
def get_projects(
        param: ProjectForQuery = Depends(),
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user),
        admin: bool = False,
    ):

    res = []

    query = db.query(
            ProjectModel,
            func.sum(DomainModel.memory).label("used_memory_g"),
            func.sum(DomainModel.core)
        ).outerjoin(
            DomainModel
        ).group_by(ProjectModel.id)
    

    if admin:
        current_user.verify_scope(['admin'])
    else:
        query = query.filter(ProjectModel.users.any(username=current_user.id))
    
    if param.name_like:
        query = query.filter(ProjectModel.name.like(f'%{param.name_like}%'))
    
    count = query.count()
    if param.limit > 0:
        query = query.limit(param.limit).offset(int(param.limit*param.page))
    
    for row in query.all():
        res.append({
            **row[0].toDict(),
            'users':row[0].users,
            'storage_pools': row[0].storage_pools,
            'network_pools': row[0].network_pools,
            'used_memory_g': 0 if row[1] is None else int(row[1])/1024,
            'used_core': 0 if row[2] is None else row[2]
        })

    return {"count": count, "data": res}
    

@app.put("")
def update_project(
        request: ProjectForUpdate, 
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):
    try:
        project: ProjectModel = db.query(
                ProjectModel
            ).filter(
                ProjectModel.id==request.project_id
            ).one()
        user: UserModel = db.query(
                UserModel
            ).filter(
                UserModel.id==request.user_id
            ).one()
    except NoResultFound:
        raise  HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The specified value is invalid"
        )

    project.users.append(user)

    db.merge(project)
    db.commit()

    project: ProjectModel = db.query(
            ProjectModel
        ).filter(
            ProjectModel.id==request.project_id
        ).one()

    return project
