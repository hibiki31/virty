import os
import jwt
import secrets

from datetime import datetime, timedelta
from typing import List, Optional
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError
from fastapi import APIRouter, Depends, Request, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from sqlalchemy.orm import Session

from mixin.database import get_db
from mixin.log import setup_logger

from .models import *
from .schemas import *


logger = setup_logger(__name__)
app = APIRouter()


class CurrentUser(BaseModel):
    user_id: str
    token: str
    role: List[str] = []
    group: List[str] = []
    def is_joined(self, role):
        if not role in self.role:
            raise exception_authority

# JWTトークンの設定
SECRET_KEY = "virty"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# パスワードハッシュ化の設定
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto"
)
# oAuth2の設定
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/auth",
    auto_error=False
)
# 例外定義
exception_certification = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="認証情報が不正です",
    headers={"WWW-Authenticate": "Bearer"}
)
exception_authority = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="権限が不正です",
    headers={"WWW-Authenticate": 'Bearer'}
)
exception_setup = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="すでに初期化されています"
)

# パスワード比較
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# パスワードハッシュ化
def get_password_hash(password):
    return pwd_context.hash(password)

# ユーザ取得
def get_user(db: Session, user_id: str):
    try:
        user = db.query(UserModel).filter(UserModel.user_id==user_id).one()
    except:
        return None
    return user

# ユーザ認証
def authenticate_user(db: Session, user_id: str, password: str):
    user = get_user(db=db, user_id=user_id)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

#  トークン生成
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # ペイロード確認
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, user_id=user_id)
    except:
        raise exception_certification

    user = get_user(db, user_id=token_data.user_id)

    return CurrentUser(user_id=token_data.user_id, token=token)


@app.post("/api/auth", response_model=TokenRFC6749Response, tags=["auth"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.user_id,
            "scopes": form_data.scopes,
            "role": [],
            "group": []
            },
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/users/me/", tags=["user"])
async def read_users_me(current_user: CurrentUser = Depends(get_current_user)):
    current_user.is_joined("aaaa")
    
    print(current_user)
    return ""


@app.get("/api/auth/validate", tags=["auth"])
async def read_auth_validate(current_user: CurrentUser = Depends(get_current_user)):
    return {"access_token": current_user.token, "token_type": "bearer"}


@app.post("/api/users", tags=["user"])
async def post_api_users(
        user: UserInsert, 
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):
    hashed_password = get_password_hash(user.hashed_password)
    user_id = user.user_id

    db.add(UserModel(user_id=user_id, hashed_password=hashed_password))
    db.commit()

    return user


@app.get("/api/users", tags=["user"],response_model=List[UserResponse])
async def get_api_users(
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):
    return db.query(UserModel).all()


@app.post("/api/auth/setup", tags=["auth"])
async def api_auth_setup(
        user: UserInsert, 
        db: Session = Depends(get_db)
    ):
    if not db.query(UserModel).all() == []:
        raise exception_setup
    hashed_password = get_password_hash(user.password)
    user_id = user.user_id

    db.add(UserModel(user_id=user_id, hashed_password=hashed_password))
    db.commit()

    return user