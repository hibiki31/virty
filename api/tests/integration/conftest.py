import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import make_url


def pytest_sessionstart(session: pytest.Session) -> None:
    if os.getenv("VIRTY_TESTING") != "1":
        raise pytest.UsageError("integration testはVIRTY_TESTING=1のCompose環境だけで実行できます")

    database_url = os.getenv("SQLALCHEMY_DATABASE_URL", "")
    try:
        database_name = make_url(database_url).database or ""
    except Exception as exc:
        raise pytest.UsageError("SQLALCHEMY_DATABASE_URLが不正です") from exc
    if not database_name.startswith("virty_test"):
        raise pytest.UsageError("database名がvirty_testで始まる専用DBを指定してください")


@pytest.fixture(scope="session")
def api_client() -> Iterator[TestClient]:
    from main import app

    with TestClient(app) as client:
        yield client
