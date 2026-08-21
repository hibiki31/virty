from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from auth.function import get_password_hash
from auth.router import CurrentUser, get_current_user as require_current_user
from mixin.database import get_db
from mixin.exception import raise_notfound
from mixin.log import setup_logger
from resource_authorization import require_admin
from user.admin_guard import would_remove_last_admin
from user.functions import overwrite_user_scopes
from user.models import UserModel, UserPublickeyModel, UserScopeModel
from user.schemas import (
    TokenData,
    User,
    UserForCreate,
    UserForQuery,
    UserForUpdate,
    UserPage,
)

logger = setup_logger(__name__)
app = APIRouter(prefix="/api/users", tags=["users"])

@app.get("/me", response_model=TokenData)
def get_current_user_profile(
    current_user: CurrentUser = Depends(require_current_user),
):
    return current_user


@app.post("", response_model=User)
def create_user(
        request: UserForCreate,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(require_current_user),
):
    current_user.verify_scope(["identity.manage"])
    require_admin(current_user)
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
    db.refresh(user_model)

    return user_model

@app.put("/{username}", response_model=User)
def update_user(
        username: str,
        request: UserForUpdate,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(require_current_user),
):
    current_user.verify_scope(["identity.manage"])
    require_admin(current_user)
    if username != request.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Path username and body username must match",
        )
    try:
        user_model = db.query(UserModel).filter(UserModel.username==username).one()
    except NoResultFound:
        raise_notfound()
    new_scope_names = [scope.name for scope in request.scopes]
    if would_remove_last_admin(db, username, new_scope_names):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The last administrator cannot lose the admin scope",
        )
    
    user_model.publickeys = [
        UserPublickeyModel(name=key.name, publickey=key.publickey)
        for key in request.publickeys
    ]
    user_model.hashed_password = get_password_hash(request.password)

    overwrite_user_scopes(
        db=db,
        username=request.username,
        new_scope_names=new_scope_names,
    )
    db.refresh(user_model)

    return user_model

@app.get("", response_model=UserPage)
def get_users(
        param: UserForQuery = Depends(),
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(require_current_user),
):
    current_user.verify_scope(["identity.manage"])
    require_admin(current_user)
    query = db.query(UserModel)

    if param.name_like:
        query = query.filter(UserModel.username.like(f"%{param.name_like}%"))

    count = query.count()
    if param.limit > 0:
        query = query.limit(param.limit).offset(int(param.limit*param.page))

    return {"count": count, "data": query.all()}


@app.delete("/{username}")
def delete_user(
        username: str,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(require_current_user),
):
    current_user.verify_scope(["identity.manage"])
    require_admin(current_user)
    if username == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The current administrator cannot delete itself",
        )
    if not db.query(UserModel).filter(UserModel.username==username).one_or_none():
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    if would_remove_last_admin(db, username, None):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The last administrator cannot be deleted",
        )

    user_model = db.query(UserModel).filter(UserModel.username==username).delete()
    db.commit()

    return user_model
