import jwt
import os

from datetime import datetime, timedelta
from typing import List, Optional
from passlib.context import CryptContext
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Security, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from sqlalchemy.orm import Session

from mixin.log import setup_logger
from mixin.database import get_db
from settings import SECRET_KEY, API_VERSION

from .schemas import *
from user.models import UserModel, UserScope
from task.functions import TaskManager
from project.schemas import PostProject


logger = setup_logger(__name__)


app = APIRouter(
    prefix="/api/auth"
)


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
        if scope == None:
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

# パスワードハッシュ化の設定
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto"
)

# oAuth2の設定
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth",
    auto_error=False,
    scopes={"admin": "Have all authority", "user": "User authority"},
)

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
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
    except:
        # トークンがデコード出来なかった場合は認証失敗
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


@app.post("/setup", tags=["auth"])
def api_auth_setup(
        model: Setup, 
        bg: BackgroundTasks,
        db: Session = Depends(get_db)
    ):
    if model.user_id == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Blanks are not allowed in id"
        )

    # ユーザがいる場合はセットアップ済みなのでイジェクト
    if not db.query(UserModel).all() == []:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already initialized"
        )

    # ユーザ追加
    user_model = UserModel(
        id=model.user_id, 
        hashed_password=pwd_context.hash(model.password)
    )

    db.add(user_model)

    db.add(UserScope(user_id=user_model.id,name="admin"))
    db.add(UserScope(user_id=user_model.id,name="user"))

    db.commit()

    # project_reqeust = PostProject(project_name='default', user_ids=[model.user_id])
    # task = TaskManager(db=db, bg=bg)
    # task.select('post', 'project', 'root')
    # task.commit(user=user_model, request=project_reqeust)

    return model


@app.post("", response_model=TokenRFC6749Response, tags=["auth"])
def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(), 
        db: Session = Depends(get_db)
    ):

    try:
        user = db.query(UserModel).filter(UserModel.id==form_data.username).one()
    except:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    if not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.id,
            # "scopes": form_data.scopes,
            "scopes": [i.name for i in list(user.scopes)],
            "projects": [i.id for i in list(user.projects)]
            },
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "Bearer"}


@app.get("/validate", tags=["auth"], response_model=AuthValidate)
def read_auth_validate(
        current_user: CurrentUser = Security(get_current_user, scopes=["user"])
    ):
    return {"access_token": current_user.token, "username": current_user.id, "token_type": "Bearer"}
