from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from auth.function import verify_password
from auth.router import OAUTH_SCOPES, CurrentUser, get_current_user as require_current_user
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
from user.models import UserModel
from user.service import change_password, create_user_record, replace_publickeys
from user.schemas import (
    OwnPublickeysUpdate,
    PasswordChange,
    PasswordReset,
    User,
    UserForCreate,
    UserForQuery,
    UserForUpdate,
    UserPage,
    UserProfile,
    UserProject,
    UserPublickey,
)

logger = setup_logger(__name__)
app = APIRouter(prefix="/api/users", tags=["users"])

def find_user(db: Session, username: str, *, lock: bool = False) -> UserModel:
    query = db.query(UserModel).filter(UserModel.username == username)
    if lock:
        query = query.with_for_update(of=UserModel).populate_existing()
    user = query.one_or_none()
    if user is None:
        raise_notfound("The user was not found.", code=ApiErrorCode.USER_NOT_FOUND)
    assert user is not None
    return user


def profile(user: UserModel) -> UserProfile:
    return UserProfile(
        id=user.username, username=user.username,
        scopes=[scope.name for scope in user.scopes],
        projects=[UserProject.model_validate(item) for item in user.projects],
        publickeys=[UserPublickey.model_validate(item) for item in user.publickeys],
    )


@app.get("/me", response_model=UserProfile)
def get_current_user_profile(
    current_user: CurrentUser = Depends(require_current_user),
    db: Session = Depends(get_db),
) -> UserProfile:
    return profile(find_user(db, current_user.id))


@app.put("/me/publickeys", response_model=UserProfile)
def update_own_publickeys(
    request: OwnPublickeysUpdate,
    current_user: CurrentUser = Depends(require_current_user),
    db: Session = Depends(get_db),
) -> UserProfile:
    user = find_user(db, current_user.id, lock=True)
    replace_publickeys(user, request.publickeys)
    db.commit()
    return profile(user)


@app.put("/me/password", status_code=204)
def update_own_password(
    request: PasswordChange,
    current_user: CurrentUser = Depends(require_current_user),
    db: Session = Depends(get_db),
) -> Response:
    user = find_user(db, current_user.id, lock=True)
    if user.session_generation != current_user.session_generation:
        raise ApiError(401, ApiErrorCode.INVALID_TOKEN, "Please sign in again.")
    if not verify_password(request.current_password, user.hashed_password):
        raise ApiError(403, ApiErrorCode.PASSWORD_REAUTHENTICATION_FAILED,
                       "The current password is incorrect.")
    change_password(user, request.new_password)
    db.commit()
    return Response(status_code=204)


@app.get("/scopes", response_model=list[str])
def get_user_scopes(current_user: CurrentUser = Depends(require_current_user)) -> list[str]:
    require_admin(current_user)
    return list(OAUTH_SCOPES)


@app.get("/detail/{username}", response_model=User)
def get_user(
    username: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_current_user),
) -> UserModel:
    require_admin(current_user)
    return find_user(db, username)


@app.put("/{username}/reset-password", status_code=204)
def reset_user_password(
    username: str,
    request: PasswordReset,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_current_user),
) -> Response:
    require_admin(current_user)
    if username == current_user.id:
        raise ApiError(409, ApiErrorCode.PASSWORD_REAUTHENTICATION_FAILED,
                       "Use the account settings to change your own password.")
    user = find_user(db, username, lock=True)
    change_password(user, request.new_password)
    db.commit()
    return Response(status_code=204)


@app.post("", response_model=User)
def create_user(
        request: UserForCreate,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(require_current_user),
) -> UserModel:
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

    user_model = create_user_record(db, request)

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
) -> UserModel:
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

    replace_publickeys(user_model, request.publickeys)
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
) -> UserPage:
    current_user.verify_scope(["identity.manage"])
    require_admin(current_user)
    query = db.query(UserModel)

    if param.name_like:
        query = query.filter(UserModel.username.like(f"%{param.name_like}%"))

    count = query.count()
    if param.limit > 0:
        query = query.limit(param.limit).offset(int(param.limit*param.page))

    return UserPage(count=count, data=[User.model_validate(user) for user in query.all()])


@app.delete("/{username}")
def delete_user(
        username: str,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(require_current_user),
) -> int:
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
