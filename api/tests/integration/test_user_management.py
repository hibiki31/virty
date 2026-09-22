"""ユーザ管理と本人設定の認可・保存・Web session失効を確認する。"""

from collections.abc import Iterator
from datetime import timedelta
import importlib.util
from pathlib import Path
from typing import Any, cast
from uuid import uuid4

from alembic.migration import MigrationContext
from alembic.operations import Operations
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import text

from agent.adapters import user_update
from agent.input_models import AgentUserUpdateInput
from agent.policy import LeaseContext
from auth.function import get_password_hash
from auth.router import create_access_token
from mixin.database import SessionLocal, Engine
from user.models import UserModel, UserScopeModel
from user import router as user_router

PASSWORD = "Virty-Test_2026!"
NEW_PASSWORD = "Virty-New_2026!"
KEY = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6MDEyMzQ1"
pytestmark = [pytest.mark.integration, pytest.mark.timeout(60)]


def login(client: TestClient, username: str, password: str = PASSWORD) -> dict[str, str]:
    response = client.post("/api/auth", data={"username": username, "password": password})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def users(api_client: TestClient) -> Iterator[tuple[str, str, dict[str, str]]]:
    suffix = uuid4().hex
    admin, member = f"admin-{suffix}", f"member-{suffix}"
    with SessionLocal.begin() as db:
        db.add(UserModel(username=admin, hashed_password=get_password_hash(PASSWORD)))
        db.add(UserScopeModel(user_id=admin, name="admin"))
    headers = login(api_client, admin)
    created = api_client.post("/api/users", headers=headers, json={
        "username": member, "password": PASSWORD,
        "scopes": [{"name": "vm.create"}],
        "publickeys": [{"name": "laptop", "publickey": KEY}],
    })
    assert created.status_code == 200, created.text
    assert {item["name"] for item in created.json()["scopes"]} == {"user", "vm.create"}
    assert created.json()["publickeys"] == [{"name": "laptop", "publickey": KEY}]
    try:
        yield admin, member, headers
    finally:
        with SessionLocal.begin() as db:
            db.query(UserModel).filter(UserModel.username.in_([admin, member])).delete(synchronize_session=False)


def test_profile_keys_and_admin_boundaries(
    api_client: TestClient, users: tuple[str, str, dict[str, str]],
) -> None:
    admin, member, admin_headers = users
    member_headers = login(api_client, member)
    profile = api_client.get("/api/users/me", headers=member_headers).json()
    assert profile["id"] == profile["username"] == member
    assert profile["publickeys"][0]["publickey"] == KEY
    assert "hashedPassword" not in profile and "sessionGeneration" not in profile
    for path in ("/api/users", "/api/users/scopes", f"/api/users/detail/{admin}"):
        assert api_client.get(path, headers=member_headers).status_code == 403
        assert api_client.get(path, headers=admin_headers).status_code == 200
    updated = api_client.put("/api/users/me/publickeys", headers=member_headers, json={
        "publickeys": [{"name": "laptop", "publickey": KEY + " updated"}],
    })
    assert updated.status_code == 200, updated.text
    assert updated.json()["publickeys"][0]["publickey"].endswith("updated")
    assert api_client.get(f"/api/users/detail/{admin}", headers=admin_headers).json()["publickeys"] == []
    for extra in ({"username": admin}, {"scopes": [{"name": "admin"}]}):
        assert api_client.put("/api/users/me/publickeys", headers=member_headers,
                              json={"publickeys": [], **extra}).status_code == 422
    assert api_client.put(f"/api/users/{admin}/reset-password", headers=member_headers,
                          json={"newPassword": NEW_PASSWORD}).status_code == 403


def test_password_changes_revoke_every_old_web_token(
    api_client: TestClient, users: tuple[str, str, dict[str, str]],
) -> None:
    admin, member, admin_headers = users
    first, second = login(api_client, member), login(api_client, member)
    wrong = api_client.put("/api/users/me/password", headers=first, json={
        "currentPassword": "wrong", "newPassword": NEW_PASSWORD,
    })
    assert wrong.status_code == 403
    assert api_client.get("/api/users/me", headers=first).status_code == 200
    changed = api_client.put("/api/users/me/password", headers=first, json={
        "currentPassword": PASSWORD, "newPassword": NEW_PASSWORD,
    })
    assert changed.status_code == 204, changed.text
    for headers in (first, second):
        assert api_client.get("/api/users/me", headers=headers).status_code == 401
    assert api_client.post("/api/auth", data={"username": member, "password": PASSWORD}).status_code == 401
    fresh = login(api_client, member, NEW_PASSWORD)
    reset = api_client.put(f"/api/users/{member}/reset-password", headers=admin_headers,
                           json={"newPassword": PASSWORD})
    assert reset.status_code == 204
    assert api_client.get("/api/users/me", headers=fresh).status_code == 401
    login(api_client, member)
    assert api_client.put(f"/api/users/{admin}/reset-password", headers=admin_headers,
                          json={"newPassword": NEW_PASSWORD}).status_code == 409


def test_legacy_token_and_agent_password_change(
    api_client: TestClient, users: tuple[str, str, dict[str, str]],
) -> None:
    admin, member, _ = users
    legacy = {"Authorization": "Bearer " + create_access_token(
        {"sub": admin, "scopes": ["admin"], "projects": []}, timedelta(minutes=5),
    )}
    assert api_client.get("/api/users/me", headers=legacy).status_code == 200
    member_token = login(api_client, member)
    with SessionLocal.begin() as db:
        user_update(db, cast(LeaseContext, None), AgentUserUpdateInput(
            path_username=member, username=member, password=NEW_PASSWORD,
            scopes=[], publickeys=[],
        ), None)
    assert api_client.get("/api/users/me", headers=member_token).status_code == 401
    login(api_client, member, NEW_PASSWORD)
    assert api_client.put("/api/users/me/password", headers=legacy, json={
        "currentPassword": PASSWORD, "newPassword": NEW_PASSWORD,
    }).status_code == 204
    assert api_client.get("/api/users/me", headers=legacy).status_code == 401


def test_delete_recreate_does_not_revive_token(
    api_client: TestClient, users: tuple[str, str, dict[str, str]],
) -> None:
    _, member, headers = users
    old = login(api_client, member)
    assert api_client.delete(f"/api/users/{member}", headers=headers).status_code == 200
    assert api_client.post("/api/users", headers=headers, json={
        "username": member, "password": PASSWORD,
    }).status_code == 200
    assert api_client.get("/api/users/me", headers=old).status_code == 401
    login(api_client, member)


def test_password_failure_rolls_back_hash_and_generation(
    api_client: TestClient, users: tuple[str, str, dict[str, str]], monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, member, _ = users
    headers = login(api_client, member)
    change = user_router.change_password

    def fail_after_change(user: UserModel, password: str) -> None:
        change(user, password)
        raise RuntimeError("password transaction failure")

    monkeypatch.setattr(user_router, "change_password", fail_after_change)
    with pytest.raises(RuntimeError, match="password transaction failure"):
        api_client.put("/api/users/me/password", headers=headers, json={
            "currentPassword": PASSWORD, "newPassword": NEW_PASSWORD,
        })
    assert api_client.get("/api/users/me", headers=headers).status_code == 200
    login(api_client, member)


@pytest.mark.parametrize("body", [
    {"publickeys": [{"name": "a", "publickey": "-----BEGIN PRIVATE KEY-----"}]},
    {"publickeys": [{"name": "a", "publickey": "ssh-ed25519 invalid"}]},
    {"publickeys": [{"name": "a", "publickey": KEY}] * 2},
    {"password": "Short!1"},
    {"password": "Virty Test_2026!"},
    {"password": "Aa1!" + "あ" * 23},
])
def test_invalid_input_is_not_saved_or_echoed(
    api_client: TestClient, users: tuple[str, str, dict[str, str]], body: dict[str, Any],
) -> None:
    _, member, headers = users
    response = api_client.post("/api/users", headers=headers, json={
        "username": member + "-invalid", "password": PASSWORD, **body,
    })
    assert response.status_code == 422, response.text
    assert PASSWORD not in response.text
    assert "PRIVATE KEY" not in response.text
    assert "input" not in response.json()["detail"]["errors"][0]


def test_session_generation_migration_preserves_users(monkeypatch: pytest.MonkeyPatch) -> None:
    path = Path(__file__).parents[2] / "alembic/versions/20260922_140000_d839cb729ea1_user_session_generation.py"
    spec = importlib.util.spec_from_file_location("user_session_migration", path)
    assert spec is not None and spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    schema = "user_migration_" + uuid4().hex
    with Engine.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA "{schema}"'))
        connection.execute(text(f'SET LOCAL search_path TO "{schema}"'))
        connection.execute(text("CREATE TABLE users (username text PRIMARY KEY)"))
        connection.execute(text("INSERT INTO users VALUES ('legacy')"))
        monkeypatch.setattr(migration, "op", Operations(MigrationContext.configure(connection)))
        migration.upgrade()
        assert connection.execute(text("SELECT session_generation FROM users")).scalar_one() is None
        migration.downgrade()
        assert connection.execute(text("SELECT username FROM users")).scalar_one() == "legacy"
        connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
