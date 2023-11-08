
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from mixin.database import get_db
from mixin.log import setup_logger

from task.functions import TaskManager

from .models import *
from .schemas import *
from project.schemas import ProjectForCreate
from auth.router import CurrentUser, get_current_user, pwd_context


logger = setup_logger(__name__)
app = APIRouter(
    prefix="/api",
    tags=["users"],
)


@app.get("/users/me", response_model=TokenData, operation_id="get_current_user")
def read_users_me(current_user: CurrentUser = Depends(get_current_user)):
    return current_user


@app.post("/users", operation_id="create_user")
def post_api_users(
        request: UserForCreate,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):
    if request.user_id == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Blanks are not allowed in id"
        )
    
    if db.query(UserModel).filter(UserModel.id==request.user_id).one_or_none():
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    # ユーザ追加
    user_model = UserModel(
        id=request.user_id, 
        hashed_password=pwd_context.hash(request.password)
    )

    db.add(user_model)
    db.add(UserScopeModel(user_id=user_model.id,name="user"))

    db.commit()

    # project_reqeust = ProjectForCreate(project_name=f'default_{user_model.id}', user_ids=[request.user_id])
    # task = TaskManager(db=db, bg=bg)
    # task.select('post', 'project', 'root')
    # task.commit(user=current_user, request=project_reqeust)

    return user_model


@app.get("/users", response_model=List[User], operation_id="get_users")
def get_api_users(
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user),
    ):
    users = db.query(UserModel).all()
    
    return users