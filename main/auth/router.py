import jwt
import secrets

from datetime import datetime, timedelta
from typing import List, Optional
from passlib.context import CryptContext
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Security, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from sqlalchemy.orm import Session

from mixin.log import setup_logger
from mixin.database import get_db
from settings import SECRET_KEY, API_VERSION

from .schemas import *
from user.models import UserModel


logger = setup_logger(__name__)
app = APIRouter(
    prefix="/api/auth",
    tags=["auth"]
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

result = []

def scopes_list(argd, scope=None):
    for k in sorted(argd.keys(), reverse=False):
        if scope == None:
            gen_scope = k
        else:
            gen_scope = scope + "." + k
        result.append(gen_scope)
        if (isinstance(argd[k],dict)):
            scopes_list(argd[k], gen_scope)  
    return result


class CurrentUser(BaseModel):
    id: str
    token: str
    role: List[str] = []
    group: List[str] = []
    def is_joined(self, role):
        if not role in self.role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Illegal authority",
                headers={"WWW-Authenticate": 'Bearer'}
            )

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
    tokenUrl="api/auth",
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

    return CurrentUser(id=user_id, token=token)



@app.post("/", response_model=TokenRFC6749Response, tags=["auth"])
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
            "scopes": form_data.scopes,
            "groups": user.groups
            },
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "Bearer"}


@app.post("/setup", tags=["auth"])
def api_auth_setup(
        model: Setup, 
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
    db.add(UserModel(
        id=model.user_id, 
        hashed_password=pwd_context.hash(model.password)
    ))
    db.commit()

    return model


@app.get("/version")
def get_version(
        db: Session = Depends(get_db)
    ):
    initialized = (not db.query(UserModel).all() == [])

    return {"initialized": initialized, "version": API_VERSION}


@app.get("/validate", tags=["auth"])
def read_auth_validate(
        current_user: CurrentUser = Security(get_current_user, scopes=["adm"])
    ):
    return {"access_token": current_user.token, "username": current_user.id, "token_type": "Bearer", "scopes": scopes_list(scopes_dict)}



@app.get("/key", tags=["auth"])
def get_ssh_key_pear(current_user: CurrentUser = Depends(get_current_user)):
    private_key = ""
    publick_key = ""
    with open("/root/.ssh/id_rsa") as f:
        private_key = f.read()
    with open("/root/.ssh/id_rsa.pub") as f:
        publick_key = f.read()

    return {"private_key": private_key, "publick_key": publick_key}