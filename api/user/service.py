"""RESTとAgentで共用する利用者保存処理。commitは呼出し側が所有する。"""

from collections.abc import Sequence
from uuid import uuid4

from sqlalchemy.orm import Session

from auth.function import get_password_hash
from user.models import UserModel, UserPublickeyModel, UserScopeModel
from user.schemas import UserForCreate, UserPublickey


def replace_publickeys(user: UserModel, keys: Sequence[UserPublickey]) -> None:
    existing = {key.name: key for key in user.publickeys}
    replacement = []
    for key in keys:
        row = existing.get(key.name) or UserPublickeyModel(name=key.name)
        row.publickey = key.publickey
        replacement.append(row)
    user.publickeys = replacement


def change_password(user: UserModel, password: str) -> None:
    user.hashed_password = get_password_hash(password)
    user.session_generation = str(uuid4())


def create_user_record(db: Session, request: UserForCreate) -> UserModel:
    user = UserModel(username=request.username)
    change_password(user, request.password)
    user.scopes = [UserScopeModel(name=name) for name in sorted(
        {scope.name for scope in request.scopes} | {"user"},
    )]
    replace_publickeys(user, request.publickeys)
    db.add(user)
    db.flush()
    return user
