from datetime import timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from auth.router import create_access_token
from mixin.database import SessionLocal
from user import router as user_router
from user.models import UserModel, UserPublickeyModel, UserScopeModel


pytestmark = [pytest.mark.integration, pytest.mark.timeout(60)]


def _headers(username: str) -> dict[str, str]:
    token = create_access_token(
        data={"sub": username, "scopes": ["user", "admin"], "projects": []},
        expires_delta=timedelta(hours=1),
    )
    return {"Authorization": f"Bearer {token}"}


def test_user_crud_status_path_and_validation(api_client: TestClient) -> None:
    suffix = uuid4().hex
    caller = f"user-crud-caller-{suffix}"
    target = f"user-crud-target-{suffix}"
    other = f"user-crud-other-{suffix}"
    usernames = [caller, target, other]
    payload = {
        "username": target,
        "password": "Virty-Test_2026!",
        "scopes": [],
        "projects": [],
        "publickeys": [],
    }

    try:
        with SessionLocal.begin() as db:
            db.add_all([
                UserModel(username=caller, hashed_password="unchanged"),
                UserModel(username=other, hashed_password="unchanged"),
            ])
            db.add(UserScopeModel(user_id=caller, name="admin"))

        create_response = api_client.post(
            "/api/users",
            headers=_headers(caller),
            json=payload,
        )
        assert create_response.status_code == 200, create_response.text
        assert create_response.json()["username"] == target

        duplicate_response = api_client.post(
            "/api/users",
            headers=_headers(caller),
            json=payload,
        )
        weak_password_response = api_client.post(
            "/api/users",
            headers=_headers(caller),
            json={**payload, "username": f"weak-{suffix}", "password": "weakpass"},
        )
        assert duplicate_response.status_code == 400
        assert weak_password_response.status_code == 422

        list_response = api_client.get(
            "/api/users",
            headers=_headers(caller),
            params={"nameLike": target},
        )
        assert list_response.status_code == 200, list_response.text
        assert list_response.json()["count"] == 1
        assert list_response.json()["data"][0]["username"] == target

        me_response = api_client.get("/api/users/me", headers=_headers(caller))
        assert me_response.status_code == 200
        assert me_response.json()["id"] == caller

        delete_response = api_client.request(
            "DELETE",
            f"/api/users/{target}",
            headers=_headers(caller),
            json={"username": other},
        )
        assert delete_response.status_code == 200
        assert delete_response.json() == 1

        with SessionLocal() as db:
            assert (
                db.query(UserModel).filter(UserModel.username == target).one_or_none()
                is None
            )
            assert (
                db.query(UserModel).filter(UserModel.username == other).one_or_none()
                is not None
            )

        missing_delete = api_client.delete(
            f"/api/users/{target}", headers=_headers(caller)
        )
        assert missing_delete.status_code == 404
    finally:
        with SessionLocal.begin() as db:
            db.query(UserPublickeyModel).filter(
                UserPublickeyModel.user_id.in_(usernames)
            ).delete(synchronize_session=False)
            db.query(UserScopeModel).filter(
                UserScopeModel.user_id.in_(usernames)
            ).delete(synchronize_session=False)
            db.query(UserModel).filter(UserModel.username.in_(usernames)).delete(
                synchronize_session=False
            )


def test_update_user_uses_path_and_accepts_only_update_fields(
    api_client: TestClient,
) -> None:
    suffix = uuid4().hex
    caller = f"user-update-caller-{suffix}"
    target = f"user-update-target-{suffix}"
    other = f"user-update-other-{suffix}"
    usernames = [caller, target, other]

    try:
        with SessionLocal.begin() as db:
            db.add_all([
                UserModel(username=username, hashed_password="unchanged")
                for username in usernames
            ])
            db.add_all([
                UserScopeModel(user_id=caller, name="admin"),
                UserScopeModel(user_id=target, name="user"),
                UserScopeModel(user_id=other, name="user"),
            ])

        response = api_client.put(
            f"/api/users/{target}",
            headers=_headers(caller),
            json={
                "username": other,
                "password": "Ignored-Test_2026!",
                "projects": [{"name": "ignored"}],
                "scopes": [{"name": "admin"}],
                "publickeys": [{"name": "main", "publickey": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6MDEyMzQ1"}],
            },
        )
        assert response.status_code == 200, response.text

        with SessionLocal() as db:
            updated = db.query(UserModel).filter(UserModel.username == target).one()
            untouched = db.query(UserModel).filter(UserModel.username == other).one()
            assert {scope.name for scope in updated.scopes} == {"admin"}
            assert [(key.name, key.publickey) for key in updated.publickeys] == [
                ("main", "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6MDEyMzQ1")
            ]
            assert updated.hashed_password == "unchanged"
            assert {scope.name for scope in untouched.scopes} == {"user"}
            assert untouched.publickeys == []

        missing = api_client.put(
            f"/api/users/missing-{suffix}",
            headers=_headers(caller),
            json={"scopes": [], "publickeys": []},
        )
        assert missing.status_code == 404

        schema = api_client.get("/api/openapi.json").json()
        update_schema = schema["components"]["schemas"]["UserForUpdate"]
        assert set(update_schema["properties"]) == {"scopes", "publickeys"}
        assert set(update_schema["required"]) == {"scopes", "publickeys"}
    finally:
        with SessionLocal.begin() as db:
            db.query(UserPublickeyModel).filter(
                UserPublickeyModel.user_id.in_(usernames)
            ).delete(synchronize_session=False)
            db.query(UserScopeModel).filter(
                UserScopeModel.user_id.in_(usernames)
            ).delete(synchronize_session=False)
            db.query(UserModel).filter(UserModel.username.in_(usernames)).delete(
                synchronize_session=False
            )


def test_update_user_rolls_back_publickeys_when_scope_update_fails(
    api_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    suffix = uuid4().hex
    caller = f"user-rollback-caller-{suffix}"
    target = f"user-rollback-target-{suffix}"
    usernames = [caller, target]

    def fail_scope_update(*args: object, **kwargs: object) -> None:
        raise RuntimeError("scope update failure")

    try:
        with SessionLocal.begin() as db:
            db.add_all([
                UserModel(username=username, hashed_password="unchanged")
                for username in usernames
            ])
            db.add_all([
                UserScopeModel(user_id=caller, name="admin"),
                UserScopeModel(user_id=target, name="user"),
            ])
            db.add(UserPublickeyModel(
                user_id=target,
                name="original",
                publickey="ssh-ed25519 original",
            ))

        monkeypatch.setattr(user_router, "overwrite_user_scopes", fail_scope_update)
        with pytest.raises(RuntimeError, match="scope update failure"):
            api_client.put(
                f"/api/users/{target}",
                headers=_headers(caller),
                json={
                    "scopes": [{"name": "admin"}],
                    "publickeys": [
                        {"name": "replacement", "publickey": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6MDEyMzQ1"}
                    ],
                },
            )

        with SessionLocal() as db:
            target_model = db.query(UserModel).filter(UserModel.username == target).one()
            assert {scope.name for scope in target_model.scopes} == {"user"}
            assert [(key.name, key.publickey) for key in target_model.publickeys] == [
                ("original", "ssh-ed25519 original")
            ]
    finally:
        with SessionLocal.begin() as db:
            db.query(UserPublickeyModel).filter(
                UserPublickeyModel.user_id.in_(usernames)
            ).delete(synchronize_session=False)
            db.query(UserScopeModel).filter(
                UserScopeModel.user_id.in_(usernames)
            ).delete(synchronize_session=False)
            db.query(UserModel).filter(UserModel.username.in_(usernames)).delete(
                synchronize_session=False
            )
