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
    prefix="/api/users",
    tags=["auth"],
)

@app.get("/api/users/me/", tags=["user"])
async def read_users_me(current_user: CurrentUser = Depends(get_current_user)):
    current_user.is_joined("aaaa")
    
    print(current_user)
    return ""


@app.post("/api/users", tags=["user"])
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


@app.get("/api/users", tags=["user"],response_model=List[UserSelect])
async def get_api_users(
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):
    users = []
    for user in db.query(UserModel).all():
        user.groups
        users.append(user)
    return users


@app.get("/api/groups", tags=["groups"],response_model=List[GroupSelect])
async def get_api_groups(
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):
    groups = []
    for group in db.query(GroupModel).all():
        group.users
        groups.append(group)
    return groups


@app.post("/api/groups", tags=["groups"])
async def post_api_groups(
        request: GroupInsert, 
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):

    group = GroupModel(group_id=request.group_id)

    db.add(group)
    db.commit()

    return


@app.patch("/api/groups", tags=["groups"])
async def patch_api_groups(
        request: GroupPatch, 
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):
    try:
        group: GroupModel = db.query(GroupModel).filter(GroupModel.group_id==request.group_id).one()
        user: UserModel = db.query(UserModel).filter(UserModel.user_id==request.user_id).one()
    except:
        raise  HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The specified value is invalid"
        )

    group.users.append(user)

    db.merge(group)
    db.commit()

    group: GroupModel = db.query(GroupModel).filter(GroupModel.group_id==request.group_id).one()

    return group


@app.delete("/api/groups", tags=["groups"])
async def delete_api_groups(
        request: GroupPatch, 
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):
    try:
        group: GroupModel = db.query(GroupModel).filter(GroupModel.group_id==request.group_id).one()
        users = []
    except:
        raise  HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The specified value is invalid"
        )

    for user in group.users:
        if user.user_id == request.user_id:
            continue
        else:
            users.append(user)
        
    group.users = users
    db.merge(group)
    db.commit()

    group: GroupModel = db.query(GroupModel).filter(GroupModel.group_id==request.group_id).one()

    return group