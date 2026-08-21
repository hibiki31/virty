import os
import threading
from queue import Queue
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, func
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.schema import CreateSchema, DropSchema

# UserModelのrelationship解決に必要な既存modelを登録する。
import models  # noqa: F401
from user.admin_guard import would_remove_last_admin
from user.models import UserModel, UserScopeModel

pytestmark = [pytest.mark.integration, pytest.mark.timeout(60)]


def _create_user_tables(engine: Engine) -> None:
    UserModel.__table__.create(engine)
    UserScopeModel.__table__.create(engine)


def _add_admins(db: Session, *usernames: str) -> None:
    for username in usernames:
        db.add(UserModel(username=username, hashed_password="unused"))
        db.add(UserScopeModel(user_id=username, name="admin"))
    db.commit()


def test_postgresql_last_admin_guard_serializes_concurrent_removal() -> None:
    database_url = os.environ["SQLALCHEMY_DATABASE_URL"]
    schema = f"last_admin_{uuid4().hex}"
    admin_engine = create_engine(database_url)
    with admin_engine.begin() as connection:
        connection.execute(CreateSchema(schema))
    engine = create_engine(
        database_url,
        connect_args={"options": f"-csearch_path={schema}"},
        pool_size=4,
        max_overflow=0,
    )
    factory = sessionmaker(bind=engine)
    first_checked = threading.Event()
    release_first = threading.Event()
    second_checked = threading.Event()
    errors: Queue[BaseException] = Queue()
    decisions: Queue[bool] = Queue()

    def remove_admin(
        username: str,
        *,
        hold_after_check: bool,
    ) -> None:
        try:
            with factory() as db:
                rejected = would_remove_last_admin(db, username, {"user"})
                decisions.put(rejected)
                if hold_after_check:
                    first_checked.set()
                    assert release_first.wait(timeout=5)
                else:
                    second_checked.set()
                if not rejected:
                    db.query(UserScopeModel).filter(
                        UserScopeModel.user_id == username,
                        UserScopeModel.name == "admin",
                    ).delete()
                db.commit()
        except BaseException as exc:
            errors.put(exc)

    first = threading.Thread(
        target=remove_admin,
        args=("admin-a",),
        kwargs={"hold_after_check": True},
        daemon=True,
    )
    second = threading.Thread(
        target=remove_admin,
        args=("admin-b",),
        kwargs={"hold_after_check": False},
        daemon=True,
    )
    try:
        _create_user_tables(engine)
        with factory() as db:
            _add_admins(db, "admin-a", "admin-b")

        first.start()
        assert first_checked.wait(timeout=5)
        second.start()
        # 先行transactionがcommitするまで再countへ進めない。
        assert second_checked.wait(timeout=0.25) is False

        release_first.set()
        assert second_checked.wait(timeout=5)
        first.join(timeout=5)
        second.join(timeout=5)
        assert errors.empty(), list(errors.queue)
        assert sorted(decisions.queue) == [False, True]

        with factory() as db:
            admin_count = db.query(func.count(UserScopeModel.user_id)).filter(
                UserScopeModel.name == "admin",
            ).scalar()
            assert admin_count == 1
    finally:
        release_first.set()
        for thread in (first, second):
            if thread.ident is not None:
                thread.join(timeout=5)
        engine.dispose()
        with admin_engine.begin() as connection:
            connection.execute(DropSchema(schema, cascade=True))
        admin_engine.dispose()
