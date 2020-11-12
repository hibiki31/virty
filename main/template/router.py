from fastapi import APIRouter, Depends
from starlette.requests import Request
from sqlalchemy.orm import Session
from mixin.database import get_db
from auth.router import get_current_user, CurrentUser

from .models import *
from .schemas import *

app = APIRouter()
