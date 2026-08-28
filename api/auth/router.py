from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import jwt
from fastapi import APIRouter, Depends, Response, status
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from mixin.database import get_db
from mixin.exception import ApiError, ApiErrorCode, NoResultFound
from mixin.log import setup_logger
from settings import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_AUDIENCE,
    JWT_ISSUER,
    SECRET_KEY,
)
from user.models import UserModel, UserScopeModel
from user.schemas import UserResponse

from .function import get_password_hash, verify_password
from .schemas import AuthValidateResponse, SetupRequest, TokenRFC6749Response

logger = setup_logger(__name__)

if SECRET_KEY is None:
    # settingsでも検査するが、JWT libraryへ渡す型をこの境界で確定する。
    raise RuntimeError("JWT署名鍵が設定されていません")
JWT_SECRET_KEY: str = SECRET_KEY


app = APIRouter(prefix="/api/auth", tags=["auth"])


OAUTH_SCOPES = {
    "admin": "すべての管理操作（後方互換用）",
    "user": "一般利用者の基本権限（後方互換用）",
    "inventory.read": "インベントリの参照",
    "vm.read": "仮想マシンの参照",
    "vm.create": "仮想マシンの作成",
    "vm.power": "仮想マシンの電源操作",
    "vm.attach": "仮想マシンの媒体・ネットワーク変更",
    "vm.delete": "仮想マシンの削除",
    "vm.project": "仮想マシンのプロジェクト変更",
    "node.read": "ノードの参照",
    "node.manage": "ノードの変更",
    "node.credentials": "ノード接続鍵の投入",
    "storage.read": "ストレージの参照",
    "storage.manage": "ストレージの変更",
    "image.read": "イメージの参照",
    "image.manage": "イメージの変更",
    "network.read": "ネットワークの参照",
    "network.manage": "ネットワークの変更",
    "project.read": "所属プロジェクトの参照",
    "project.manage": "プロジェクトの変更",
    "flavor.read": "フレーバーの参照",
    "flavor.manage": "フレーバーの変更",
    "task.read.self": "自身のタスクの参照",
    "task.read.any": "すべてのタスクの参照",
    "task.manage": "タスクの取消・削除",
    "identity.manage": "利用者と権限の管理",
    "metrics.read": "メトリクスの参照",
}

LEGACY_USER_SCOPES = {
    "inventory.read",
    "vm.read",
    "vm.power",
    "node.read",
    "storage.read",
    "image.read",
    "network.read",
    "project.read",
    "flavor.read",
    "task.read.self",
}


def scope_grants(granted_scope: str, required_scope: str) -> bool:
    """完全一致または明示的な末尾wildcardだけを許可する。"""
    if granted_scope == "admin":
        return True
    if granted_scope == "user":
        return required_scope in LEGACY_USER_SCOPES
    if granted_scope == required_scope:
        return True
    if granted_scope.endswith(".*"):
        namespace = granted_scope[:-2]
        return required_scope.startswith(f"{namespace}.")
    return False


class CurrentUser(BaseModel):
    id: str
    token: str
    scopes: list[str] = Field(default_factory=list)
    token_scopes: list[str] | None = None
    projects: list[str] = Field(default_factory=list)

    def verify_scope(self, scopes: list[str], return_bool: bool = False) -> bool:
        for required_scope in scopes:
            granted_by_database = any(
                scope_grants(scope, required_scope) for scope in self.scopes
            )
            granted_by_token = self.token_scopes is None or any(
                scope_grants(scope, required_scope) for scope in self.token_scopes
            )
            if not (granted_by_database and granted_by_token):
                if return_bool:
                    return False
                raise ApiError(
                    status.HTTP_403_FORBIDDEN,
                    ApiErrorCode.SCOPE_DENIED,
                    "The required permission is missing.",
                )
        return True

    def can_access_project(self, project_id: str | None) -> bool:
        return (
            self.verify_scope(["admin"], return_bool=True)
            or project_id is None
            or project_id in self.projects
        )

# JWTトークンの設定
ALGORITHM = "HS256"

# oAuth2の設定
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth",
    auto_error=False,
    scopes=OAUTH_SCOPES,
)


def create_access_token(data: dict[str, Any], expires_delta: timedelta) -> str:
    to_encode = data.copy()
    now = datetime.now(UTC)
    expire = datetime.now(UTC) + expires_delta
    to_encode.update({
        "aud": JWT_AUDIENCE,
        "exp": expire,
        "iat": now,
        "iss": JWT_ISSUER,
        "jti": str(uuid4()),
    })
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    security_scopes: SecurityScopes,
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> CurrentUser:
    if token is None:
        raise ApiError(
            status.HTTP_401_UNAUTHORIZED,
            ApiErrorCode.AUTHENTICATION_REQUIRED,
            "Authentication is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[ALGORITHM],
            audience=JWT_AUDIENCE,
            issuer=JWT_ISSUER,
        )
        user_id = payload.get("sub")
        token_scopes = payload.get("scopes", [])
        token_projects = payload.get("projects", [])
        if (
            not isinstance(user_id, str)
            or not user_id
            or not isinstance(token_scopes, list)
            or not isinstance(token_projects, list)
            or not all(isinstance(scope, str) for scope in token_scopes)
            or not all(isinstance(project, str) for project in token_projects)
        ):
            raise jwt.InvalidTokenError("required claims are invalid")
    except jwt.exceptions.ExpiredSignatureError:
        raise ApiError(
            status.HTTP_401_UNAUTHORIZED,
            ApiErrorCode.TOKEN_EXPIRED,
            "The access token has expired.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.exceptions.InvalidTokenError:
        raise ApiError(
            status.HTTP_401_UNAUTHORIZED,
            ApiErrorCode.INVALID_TOKEN,
            "The access token is invalid.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    
    user = db.query(UserModel).filter(UserModel.username == user_id).one_or_none()
    if user is None:
        raise ApiError(
            status.HTTP_401_UNAUTHORIZED,
            ApiErrorCode.INACTIVE_USER,
            "The user is no longer active.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # token発行後の権限変更・端末失効を即時反映するためDBを正本にする。
    current_user = CurrentUser(
        id=user_id,
        token=token,
        scopes=[scope.name for scope in user.scopes],
        token_scopes=token_scopes,
        projects=[
            project.id
            for project in user.projects
            if project.id in token_projects
        ],
    )
    current_user.verify_scope(security_scopes.scopes)
    return current_user


@app.post(
    "/setup", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED,
)
def api_auth_setup(
        model: SetupRequest, 
        db: Session = Depends(get_db),
):
    if db.query(UserModel).count():
        raise ApiError(
            status.HTTP_409_CONFLICT,
            ApiErrorCode.ALREADY_INITIALIZED,
            "Virty has already been initialized.",
        )
    user = UserModel(
        username=model.username,
        hashed_password=get_password_hash(model.password)
    )
    db.add_all([
        user,
        UserScopeModel(user_id=model.username, name="admin"),
        UserScopeModel(user_id=model.username, name="user")
    ])
    db.commit()

    return user


## 恐らくFastAPIの仕様でform_dataは明示的にOperationID指定しないとBodyスキーマの名前が自動生成されたものになってしまう。
# "application/x-www-form-urlencoded": components["schemas"]["Body_login_api_auth_post"];
# "application/x-www-form-urlencoded": components["schemas"]["Body_login"];
@app.post("", response_model=TokenRFC6749Response, operation_id="login")
def login(
        response: Response,
        form_data: OAuth2PasswordRequestForm = Depends(), 
        db: Session = Depends(get_db)
    ):

    try:
        user = db.query(UserModel).filter(UserModel.username==form_data.username).one()
    except NoResultFound:
        raise ApiError(
            status.HTTP_401_UNAUTHORIZED,
            ApiErrorCode.INVALID_CREDENTIALS,
            "The username or password is incorrect.",
        )
    
    if not verify_password(form_data.password, user.hashed_password):
        raise ApiError(
            status.HTTP_401_UNAUTHORIZED,
            ApiErrorCode.INVALID_CREDENTIALS,
            "The username or password is incorrect.",
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username,
            # "scopes": form_data.scopes,
            "scopes": [i.name for i in list(user.scopes)],
            "projects": [i.id for i in list(user.projects)]
            },
        expires_delta=access_token_expires,
    )
    response.headers["Cache-Control"] = "no-store"
    return {"access_token": access_token, "token_type": "Bearer"}


@app.get("/validate", tags=["auth"], response_model=AuthValidateResponse)
def validate_token(
        response: Response,
        current_user: CurrentUser = Depends(get_current_user)
    ):
    response.headers["Cache-Control"] = "no-store"
    return {"access_token": current_user.token, "username": current_user.id, "token_type": "Bearer"}
