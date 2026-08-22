from collections.abc import Collection

from sqlalchemy import func, text
from sqlalchemy.orm import Session

from user.models import UserScopeModel

# 全processで同じtransaction lockを取得するための固定namespace key。
LAST_ADMIN_ADVISORY_LOCK_KEY = int.from_bytes(b"VRTYADMN", byteorder="big")


def acquire_last_admin_guard(db: Session) -> None:
    """admin membership変更をPostgreSQL transaction単位で直列化する。"""

    if db.get_bind().dialect.name != "postgresql":
        # SQLiteは統合test専用で、書込みtransaction自体が直列化される。
        return
    db.execute(
        text("SELECT pg_advisory_xact_lock(:lock_key)"),
        {"lock_key": LAST_ADMIN_ADVISORY_LOCK_KEY},
    )


def would_remove_last_admin(
    db: Session,
    username: str,
    new_scopes: Collection[str] | None,
) -> bool:
    """lock取得後のDB状態から最後のadminを失う変更か判定する。"""

    # 呼出し側は判定後の変更まで同じtransactionでcommitする。
    acquire_last_admin_guard(db)
    target_is_admin = db.query(UserScopeModel).filter(
        UserScopeModel.user_id == username,
        UserScopeModel.name == "admin",
    ).one_or_none()
    if target_is_admin is None or (
        new_scopes is not None and "admin" in new_scopes
    ):
        return False
    admin_count = db.query(func.count(UserScopeModel.user_id)).filter(
        UserScopeModel.name == "admin",
    ).scalar()
    return int(admin_count or 0) <= 1
