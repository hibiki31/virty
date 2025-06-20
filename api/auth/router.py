from datetime import UTC, datetime, timedelta
from typing import List

import jwt
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from pydantic import BaseModel
from sqlalchemy.orm import Session

from mixin.database import get_db
from mixin.exception import NoResultFound
from mixin.log import setup_logger
from settings import SECRET_KEY
from user.models import UserModel, UserScopeModel
from user.schemas import UserResponse

from .function import get_password_hash, verify_password
from .schemas import AuthValidateResponse, SetupRequest, TokenRFC6749Response

logger = setup_logger(__name__)


app = APIRouter(prefix="/api/auth", tags=["auth"])


scopes_dict = {
    "admin": {
        "storage": {},
        "network": {
            "delete": None,
            "create": None,
        }
    },
    "user": {
    }
}


scopes_list = []


def scopes_list_generator(argd, scope=None):
    for k in sorted(argd.keys(), reverse=False):
        if scope is None:
            gen_scope = k
        else:
            gen_scope = scope + "." + k
        scopes_list.append(gen_scope)
        if (isinstance(argd[k],dict)):
            scopes_list_generator(argd[k], gen_scope)  
    return scopes_list

scopes_list_generator(scopes_dict)


class CurrentUser(BaseModel):
    id: str
    token: str
    scopes: List[str] = []
    projects: List[str] = []
    def verify_scope(self, scopes, return_bool=False):
        # 要求Scopeでループ
        for request_scope in scopes:
            match_scoped = False
            # 持っているScopeでループ
            for having_scope in self.scopes:
                if having_scope in request_scope:
                    match_scoped = True
            # 持っているScopeが権限を持たない場合終了
            if not match_scoped:
                if return_bool:
                    return False
                else:
                    raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Not enough permissions",
                            headers={"WWW-Authenticate": "Bearer"},
                        )
        # すべての要求Scopeをクリア
        return True

# JWTトークンの設定
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 28

# oAuth2の設定
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth",
    auto_error=False,
    scopes={"admin": "Have all authority", "user": "User authority"},
)

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(UTC) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
        security_scopes: SecurityScopes, 
        token: str = Depends(oauth2_scheme)
    ):
    # ペイロード確認
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        scopes = payload.get("scopes", [])
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Signature has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.exceptions.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Illegal jwt",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    
    for request_scope in security_scopes.scopes:
        match_scoped = False
        for having_scope in scopes:
            if request_scope in having_scope:
                match_scoped = True
        if not match_scoped:
            raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not enough permissions",
                    headers={"WWW-Authenticate": "Bearer"},
                )

    return CurrentUser(id=user_id, token=token, scopes=scopes)


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
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already initialized"
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
        form_data: OAuth2PasswordRequestForm = Depends(), 
        db: Session = Depends(get_db)
    ):

    try:
        user = db.query(UserModel).filter(UserModel.username==form_data.username).one()
    except NoResultFound:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

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
    return {"access_token": access_token, "token_type": "Bearer"}


@app.get("/validate", tags=["auth"], response_model=AuthValidateResponse)
def validate_token(
        current_user: CurrentUser = Security(get_current_user, scopes=["user"])
    ):
    return {"access_token": current_user.token, "username": current_user.id, "token_type": "Bearer"}
