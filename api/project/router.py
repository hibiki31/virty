from fastapi import APIRouter, Depends, HTTPException, status, Request
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
    tags=["projects"],
)


@app.get("/api/projects", response_model=List[Project], operation_id="get_projects")
def get_api_projects(
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user),
        admin: bool = False,
        limit: int = 25,
        page: int = 0,
        name: str = None
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
    
    if name:
        query = query.filter(ProjectModel.name.like(f'%{name}%'))
    
    query = query.limit(limit).offset(int(limit*page))
    
    for row in query.all():
        res.append({
            **row[0].toDict(),
            'users':row[0].users,
            'storage_pools': row[0].storage_pools,
            'network_pools': row[0].network_pools,
            'used_memory_g': 0 if row[1] == None else int(row[1])/1024,
            'used_core': 0 if row[2] == None else row[2]
        })

    return res


@app.post("/api/tasks/projects", operation_id="create_project")
def post_api_projects(
        body: ProjectForCreate,
        req: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    task = TaskManager(db=db)
    task.select(method='post', resource='project', object='root')
    task.commit(user=cu, req=req, body=body)

    return [task.model]


@app.delete("/api/tasks/projects/{project_id}", operation_id="delete_project")
def delete_api_projects(
        project_id: str,
        req: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    task = TaskManager(db=db)
    task.select(method='delete', resource='project', object='root')
    task.commit(user=cu, req=req, param={"project_id": project_id})

    return [task.model]
    

@app.put("/api/projects", operation_id="update_project")
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
