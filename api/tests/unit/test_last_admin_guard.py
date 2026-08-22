import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# UserModelのrelationship解決に必要な既存modelを登録する。
import models  # noqa: F401
from user.admin_guard import would_remove_last_admin
from user.models import UserModel, UserScopeModel

pytestmark = [pytest.mark.unit, pytest.mark.timeout(30)]


def _create_user_tables(engine: Engine) -> None:
    UserModel.__table__.create(engine)
    UserScopeModel.__table__.create(engine)


def _add_admins(db: Session, *usernames: str) -> None:
    for username in usernames:
        db.add(UserModel(username=username, hashed_password="unused"))
        db.add(UserScopeModel(user_id=username, name="admin"))
    db.commit()


def test_last_admin_guard_recounts_current_transaction_state() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    _create_user_tables(engine)
    factory = sessionmaker(bind=engine)
    try:
        with factory() as db:
            _add_admins(db, "admin-a", "admin-b")
            assert would_remove_last_admin(db, "admin-a", {"user"}) is False
            db.query(UserScopeModel).filter(
                UserScopeModel.user_id == "admin-a",
                UserScopeModel.name == "admin",
            ).delete()
            db.commit()

            assert would_remove_last_admin(db, "admin-b", None) is True
            assert would_remove_last_admin(db, "admin-b", {"admin"}) is False
    finally:
        engine.dispose()
