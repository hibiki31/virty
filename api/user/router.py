from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from auth.function import get_password_hash
from auth.router import CurrentUser, get_current_user as require_current_user
from mixin.database import get_db
from mixin.exception import ApiError, ApiErrorCode, raise_notfound
from mixin.log import setup_logger
from project.service import (
    ProjectConflictError,
    ensure_user_memberships_deletable,
)
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
        raise ApiError(
            status.HTTP_400_BAD_REQUEST,
            ApiErrorCode.USER_ID_REQUIRED,
            "A user ID is required.",
        )

    if db.query(UserModel).filter(UserModel.username==request.username).one_or_none():
        raise ApiError(
            status.HTTP_400_BAD_REQUEST,
            ApiErrorCode.USER_EXISTS,
            "The user already exists.",
        )

    # ユーザ追加
    user_model = UserModel(
        username=request.username,
        hashed_password=get_password_hash(request.password),
    )

    user_model.scopes.append(UserScopeModel(name="user"))
    db.add(user_model)

    db.commit()
    db.refresh(
        user_model,
        attribute_names=["scopes", "projects", "publickeys"],
    )

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
    try:
        user_model = db.query(UserModel).filter(UserModel.username == username).one()
    except NoResultFound:
        raise_notfound(
            "The user was not found.",
            code=ApiErrorCode.USER_NOT_FOUND,
        )

    new_scope_names = [scope.name for scope in request.scopes]
    if would_remove_last_admin(db, username, new_scope_names):
        raise ApiError(
            status.HTTP_409_CONFLICT,
            ApiErrorCode.LAST_ADMIN_SCOPE_REQUIRED,
            "The last administrator must retain the admin scope.",
        )

    user_model.publickeys = [
        UserPublickeyModel(name=key.name, publickey=key.publickey)
        for key in request.publickeys
    ]
    overwrite_user_scopes(
        db=db,
        user=user_model,
        new_scope_names=new_scope_names,
    )
    db.commit()
    db.refresh(
        user_model,
        attribute_names=["scopes", "projects", "publickeys"],
    )

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
        raise ApiError(
            status.HTTP_409_CONFLICT,
            ApiErrorCode.SELF_DELETE_DENIED,
            "The current administrator cannot delete its own account.",
        )
    if not db.query(UserModel).filter(UserModel.username==username).one_or_none():
        raise ApiError(
            status.HTTP_404_NOT_FOUND,
            ApiErrorCode.USER_NOT_FOUND,
            "The user was not found.",
        )
    if would_remove_last_admin(db, username, None):
        raise ApiError(
            status.HTTP_409_CONFLICT,
            ApiErrorCode.LAST_ADMIN_REQUIRED,
            "The last administrator cannot be deleted.",
        )
    try:
        ensure_user_memberships_deletable(db, username)
    except ProjectConflictError as exc:
        raise ApiError(
            status.HTTP_409_CONFLICT,
            ApiErrorCode.LAST_PROJECT_MEMBER_REQUIRED,
            "The last member of a project cannot be deleted.",
        ) from exc

    user_model = db.query(UserModel).filter(UserModel.username==username).delete()
    db.commit()

    return user_model
