from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.function import get_password_hash
from auth.router import CurrentUser, get_current_user
from mixin.database import get_db
from mixin.log import setup_logger
from user.models import UserModel, UserScopeModel
from user.schemas import TokenData, UserForCreate, UserForQuery, UserPage

logger = setup_logger(__name__)
app = APIRouter(prefix="/api/users", tags=["users"])


@app.get("/me", response_model=TokenData)
def get_current_user(current_user: CurrentUser = Depends(get_current_user)):
    return current_user


@app.post("")
def create_user(
        request: UserForCreate,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user),
    ):
    if request.username == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Blanks are not allowed in id",
        )

    if db.query(UserModel).filter(UserModel.username==request.username).one_or_none():
        raise HTTPException(
            status_code=400,
            detail="User already exists",
        )

    # ユーザ追加
    user_model = UserModel(
        username=request.username,
        hashed_password=get_password_hash(request.password),
    )

    db.add(user_model)
    db.add(UserScopeModel(user_id=user_model.username,name="user"))

    db.commit()

    return user_model


@app.get("", response_model=UserPage)
def get_users(
        param: UserForQuery = Depends(),
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user),
    ):
    query = db.query(UserModel)

    if param.name_like:
        query = query.filter(UserModel.usernamee.like(f"%{param.name_like}%"))

    count = query.count()
    if param.limit > 0:
        query = query.limit(param.limit).offset(int(param.limit*param.page))

    return {"count": count, "data": query.all()}


@app.delete("/{username}")
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
