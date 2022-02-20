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
from auth.router import CurrentUser, get_current_user

logger = setup_logger(__name__)
app = APIRouter(
    prefix="/api/groups",
    tags=["group"],
)


@app.get("/me", tags=["user"])
async def read_users_me(current_user: CurrentUser = Depends(get_current_user)):
    current_user.is_joined("aaaa")
    
    print(current_user)
    return ""


@app.post("/", tags=["user"])
async def post_api_users(
        user: UserInsert, 
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):
    hashed_password = get_password_hash(user.password)
    user_id = user.user_id

    db.add(UserModel(user_id=user_id, hashed_password=hashed_password))

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request user already exists"
        )

    return user


@app.get("/", tags=["user"],response_model=List[UserSelect])
def get_api_users(
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):
    users = db.query(UserModel).all()
    
    return users