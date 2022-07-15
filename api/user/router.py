
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from mixin.database import get_db
from mixin.log import setup_logger

from task.functions import TaskManager

from .models import *
from .schemas import *
from project.schemas import PostProject
from auth.router import CurrentUser, get_current_user, pwd_context


logger = setup_logger(__name__)
app = APIRouter(
    prefix="/api/users",
    tags=["users"],
)


@app.get("/me")
def read_users_me(current_user: CurrentUser = Depends(get_current_user)):
    current_user.is_joined("aaaa")
    
    print(current_user)
    return ""


@app.post("")
def post_api_users(
        request: UserInsert,
        bg: BackgroundTasks,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):
    if request.user_id == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Blanks are not allowed in id"
        )

    # ユーザ追加
    user_model = UserModel(
        id=request.user_id, 
        hashed_password=pwd_context.hash(request.password)
    )

    db.add(user_model)
    db.add(UserScope(user_id=user_model.id,name="user"))

    db.commit()

    project_reqeust = PostProject(project_name='default', user_ids=[request.user_id])
    task = TaskManager(db=db, bg=bg)
    task.select('post', 'project', 'root')
    task.commit(user=current_user, request=project_reqeust)

    return user_model


@app.get("")
def get_api_users(
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):
    users = db.query(UserModel).all()
    
    return users