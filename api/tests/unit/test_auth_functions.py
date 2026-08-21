import pytest

from auth.function import get_password_hash, verify_password


pytestmark = [pytest.mark.unit, pytest.mark.timeout(10)]


def test_password_hash_round_trip() -> None:
    password = "Virty-Test_2026!"

    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong-password", hashed)
