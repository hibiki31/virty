import jwt
import pytest
from fastapi import HTTPException
from fastapi.security import SecurityScopes

from auth.function import get_password_hash, verify_password
from auth.router import ALGORITHM, get_current_user
from settings import SECRET_KEY


pytestmark = [pytest.mark.unit, pytest.mark.timeout(10)]


def test_password_hash_round_trip() -> None:
    password = "Virty-Test_2026!"

    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong-password", hashed)


def test_get_current_user_rejects_token_without_subject() -> None:
    token = jwt.encode({"scopes": []}, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(SecurityScopes(), token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Illegal jwt"
