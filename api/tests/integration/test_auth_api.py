from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from mixin.database import SessionLocal
from user.models import UserModel


pytestmark = [pytest.mark.integration, pytest.mark.timeout(60)]


def test_setup_login_and_validate(api_client: TestClient) -> None:
    username = f"integration-{uuid4().hex}"
    password = "Virty-Test_2026!"

    assert api_client.get("/api/version").json()["initialized"] is False
    try:
        setup = api_client.post(
            "/api/auth/setup",
            json={"username": username, "password": password},
        )
        assert setup.status_code == 201

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
