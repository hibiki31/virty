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

from user.models import *
from .schemas import *
from auth.router import CurrentUser, get_current_user

logger = setup_logger(__name__)
app = APIRouter(
    prefix="/api/groups",
    tags=["group"],
)



@app.get("", tags=["groups"],response_model=List[GroupSelect])
def get_api_groups(
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):
    groups = []
    for group in db.query(GroupModel).all():
        group.users
        groups.append(group)
    return groups


@app.post("", tags=["groups"])
def post_api_groups(
        request: GroupPost, 
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):

    group = GroupModel(id=request.group_id)

    db.add(group)
    db.commit()

    return


@app.put("")
def put_api_groups(
        request: GroupPatch, 
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):
    try:
        group: GroupModel = db.query(GroupModel).filter(GroupModel.id==request.group_id).one()
        user: UserModel = db.query(UserModel).filter(UserModel.id==request.user_id).one()
    except:
        raise  HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The specified value is invalid"
        )

    group.users.append(user)

    db.merge(group)
    db.commit()

    group: GroupModel = db.query(GroupModel).filter(GroupModel.id==request.group_id).one()

    return group


@app.delete("", tags=["groups"])
def delete_api_groups(
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