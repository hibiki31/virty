from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from domain.models import DomainModel

from task.functions import TaskManager
from mixin.database import get_db
from mixin.log import setup_logger

from user.models import *
from project.models import *
from project.schemas import *
from auth.router import CurrentUser, get_current_user

logger = setup_logger(__name__)
app = APIRouter(
    prefix="/api/projects",
    tags=["projects"],
)



@app.get("", response_model=List[Project])
def get_api_projects(
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user),
        admin: bool = False
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
        rows = query.all()
    else:
        rows = query.filter(ProjectModel.users.any(id=current_user.id)).all()
    
    for row in rows:
        res.append({
            **row[0].toDict(),
            'users':row[0].users,
            'storage_pools': row[0].storage_pools,
            'network_pools': row[0].network_pools,
            'used_memory_g': 0 if row[1] == None else int(row[1])/1024,
            'used_core': 0 if row[2] == None else row[2]
        })

    return res

@app.post("")
def post_api_projects(
        request: ProjectForCreate, 
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):
    task = TaskManager(db=db)
    task.select(method='post', resource='project', object='root')
    task.commit(user=current_user, request=request)

    return task.model


@app.delete("")
def delete_api_projects(
        request: ProjectForDelete, 
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):
    task = TaskManager(db=db)
    task.select(method='delete', resource='project', object='root')
    task.commit(user=current_user, request=request)

    return task.model
    

@app.put("")
def put_api_projects(
        request: ProjectForUpdate, 
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
