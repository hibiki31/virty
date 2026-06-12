from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from models import UserModel, UserScopeModel


def overwrite_user_scopes(
    db: Session,
    username: str,
    new_scope_names: list[str],
) -> None:
    """users_scope を new_scope_names の内容で完全に置き換える"""
    new_scope_set = set(new_scope_names)

    # 1. ユーザと既存スコープを読み込む
    user: UserModel = (
        db.execute(
            select(UserModel)
            .where(UserModel.username == username)
            .options(selectinload(UserModel.scopes))  # 既存 scope を一括 prefetch
        ).scalar_one()
    )

    # 2. 既存 ←→ 新規 の集合差分を計算
    existing = {s.name: s for s in user.scopes}

    # 削除対象
    for obsolete_name in existing.keys() - new_scope_set:
        db.delete(existing[obsolete_name])

    # 追加対象
    for missing_name in new_scope_set - existing.keys():
        user.scopes.append(UserScopeModel(name=missing_name))

    # 3. commit
    db.commit()