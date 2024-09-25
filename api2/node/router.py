from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.router import pwd_context
from database import get_db
from log import setup_logger
from user.models import UserModel, UserScopeModel
from user.schemas import UserForCreate

logger = setup_logger(__name__)
app = APIRouter(
    prefix="/api/nodes",
    tags=["nodes"],
)


@app.post("/")
def node_for_join(
        request: UserForCreate,
        db: Session = Depends(get_db)
    ):
    if request.user_id == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Blanks are not allowed in id",
        )

    if db.query(UserModel).filter(UserModel.username==request.user_id).one_or_none():
        raise HTTPException(
            status_code=400,
            detail="User already exists",
        )

    # ユーザ追加
    user_model = UserModel(
        username=request.user_id,
        hashed_password=pwd_context.hash(request.password),
    )

    db.add(user_model)
    db.add(UserScopeModel(user_id=user_model.username,name="user"))

    db.commit()

    return user_model
