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
from sqlalchemy.exc import IntegrityError

from mixin.database import get_db
from mixin.log import setup_logger
from settings import IS_DEV

from .models import *
from .schemas import *
from auth.router import CurrentUser, get_current_user, pwd_context

logger = setup_logger(__name__)
app = APIRouter(
    prefix="/api/users",
    tags=["user"],
)


@app.get("/me", tags=["user"])
def read_users_me(current_user: CurrentUser = Depends(get_current_user)):
    current_user.is_joined("aaaa")
    
    print(current_user)
    return ""


@app.post("", tags=["user"])
def post_api_users(
        model: UserInsert, 
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):
    print(model)
    if model.user_id == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Blanks are not allowed in id"
        )

    # ユーザ追加
    user_model = UserModel(
        id=model.user_id, 
        hashed_password=pwd_context.hash(model.password)
    )

    db.add(user_model)
    db.commit()

    db.add(UserScope(user_id=user_model.id,name="user"))

    db.commit()

    return user_model

@app.get("", tags=["user"])
def get_api_users(
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):
    users = db.query(UserModel).all()
    
    return users