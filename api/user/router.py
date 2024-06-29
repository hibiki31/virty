from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.router import CurrentUser, get_current_user, pwd_context
from mixin.database import get_db
from mixin.log import setup_logger
from user.models import UserModel, UserScopeModel
from user.schemas import TokenData, UserForCreate, UserForQuery, UserPage

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
        current_user: CurrentUser = Depends(get_current_user),
    ):
    if request.user_id == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Blanks are not allowed in id",
        )

    if db.query(UserModel).filter(UserModel.username==request.user_id).one_or_none():
        raise HTTPException(
            status_code=400,
            detail="User already exists",
        )

    # ユーザ追加
    user_model = UserModel(
        username=request.user_id,
        hashed_password=pwd_context.hash(request.password),
    )

    db.add(user_model)
    db.add(UserScopeModel(user_id=user_model.username,name="user"))

    db.commit()

    return user_model


@app.get("/users", response_model=UserPage, operation_id="get_users")
def get_api_users(
        param: UserForQuery = Depends(),
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user),
    ):
    query = db.query(UserModel)

    if param.name_like:
        query = query.filter(UserModel.usernamee.like(f"%{param.name_like}%"))

    count = query.count()
    if query.limit > 0:
        query = query.limit(param.limit).offset(int(param.limit*param.page))

    return {"count": count, "data": query.all()}


@app.delete("/users/{username}", operation_id="delete_user")
def delete_user(
        username: str,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user),
    ):

    if not db.query(UserModel).filter(UserModel.username==username).one_or_none():
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    user_model = db.query(UserModel).filter(UserModel.username==username).delete()
    db.commit()

    return user_model
