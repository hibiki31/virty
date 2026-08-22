from datetime import timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from auth.router import create_access_token
from mixin.database import SessionLocal
from user.models import UserModel


pytestmark = [pytest.mark.integration, pytest.mark.timeout(60)]


def test_setup_login_and_validate(api_client: TestClient) -> None:
    username = f"integration-{uuid4().hex}"
    password = "Virty-Test_2026!"

    assert api_client.get("/api/version").json()["initialized"] is False
    invalid_setup = api_client.post(
        "/api/auth/setup",
        json={"username": username},
    )
    assert invalid_setup.status_code == 422
    try:
        setup = api_client.post(
            "/api/auth/setup",
            json={"username": username, "password": password},
        )
        assert setup.status_code == 201

        repeated_setup = api_client.post(
            "/api/auth/setup",
            json={"username": f"other-{username}", "password": password},
        )
        assert repeated_setup.status_code == 409

        invalid_login = api_client.post(
            "/api/auth",
            data={"username": username, "password": "Wrong-Test_2026!"},
        )
        assert invalid_login.status_code == 401

        login = api_client.post(
            "/api/auth",
            data={"username": username, "password": password},
        )
        assert login.status_code == 200
        token = login.json()["access_token"]

        validate = api_client.get(
            "/api/auth/validate",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert validate.status_code == 200
        assert validate.json()["username"] == username
    finally:
        with SessionLocal.begin() as db:
            db.query(UserModel).filter(UserModel.username == username).delete()


def test_validate_rejects_expired_and_malformed_tokens(api_client: TestClient) -> None:
    expired = create_access_token(
        data={"sub": "expired-user", "scopes": ["user"], "projects": []},
        expires_delta=timedelta(seconds=-1),
    )

    expired_response = api_client.get(
        "/api/auth/validate",
        headers={"Authorization": f"Bearer {expired}"},
    )
    malformed_response = api_client.get(
        "/api/auth/validate",
        headers={"Authorization": "Bearer malformed-token"},
    )
    missing_response = api_client.get("/api/auth/validate")

    assert expired_response.status_code == 401
    assert malformed_response.status_code == 401
    assert missing_response.status_code == 401
