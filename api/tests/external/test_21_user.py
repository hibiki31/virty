import pytest

from mixin.database import SessionLocal
from tests.external.conftest import EnvConfig
from user.models import UserModel


def _delete_run_users(env: EnvConfig) -> None:
    usernames = [user.username for user in env.users]
    with SessionLocal.begin() as db:
        db.query(UserModel).filter(UserModel.username.in_(usernames)).delete(
            synchronize_session=False,
        )


def _create_run_users(env: EnvConfig, client) -> None:
    for user in env.users:
        response = client.post(
            "/api/users",
            json={"username": user.username, "password": user.password},
        )
        assert response.status_code == 200


@pytest.fixture
def absent_run_users(env: EnvConfig):
    _delete_run_users(env)
    yield
    _delete_run_users(env)


@pytest.fixture
def existing_run_users(env: EnvConfig, client, absent_run_users):
    _create_run_users(env, client)
    yield


def test_create_user(env: EnvConfig, client, absent_run_users) -> None:
    _create_run_users(env, client)


def test_delete_user(env: EnvConfig, client, existing_run_users) -> None:
    for user in env.users:
        response = client.delete(f"/api/users/{user.username}")
        assert response.status_code == 200


def test_update_user(env: EnvConfig, client, existing_run_users) -> None:
    for user in env.users:
        request = {
            "username": user.username,
            "password": user.password,
            "scopes": [{"name": "user"}],
            "projects": [],
            "publickeys": [],
        }
        response = client.put(f"/api/users/{user.username}", json=request)
        assert response.status_code == 200
