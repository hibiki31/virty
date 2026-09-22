"""初期設定、REST、Agentで同じ入力規則を確認する。"""

import pytest
from pydantic import ValidationError

from agent.input_models import AgentUserCreateInput
from auth.function import get_password_hash, verify_password
from auth.schemas import SetupRequest
from user.schemas import UserForCreate


@pytest.mark.parametrize("password", [
    "shortA1", "lowercase1!", "UPPERCASE1!", "NoDigits!!", "NoSymbols123",
    "With Space1!", "Aa1!" + "あ" * 23, "Aa1!" + "x" * 69, "Aa1!\x00xxxx",
])
def test_password_policy_matches_all_creation_paths(password: str) -> None:
    for schema in (SetupRequest, UserForCreate, AgentUserCreateInput):
        with pytest.raises(ValidationError):
            schema(username="alice", password=password)


def test_password_byte_boundary_and_legacy_login() -> None:
    password = "Aa1!" + "x" * 68
    for schema in (SetupRequest, UserForCreate, AgentUserCreateInput):
        assert schema(username="alice", password=password).password == password
    legacy = password + "legacy-suffix"
    assert verify_password(legacy, get_password_hash(legacy))


@pytest.mark.parametrize("username", ["", "   ", "alice/bob", "alice\nbob", "a" * 256])
def test_username_validation_matches_creation_paths(username: str) -> None:
    for schema in (SetupRequest, UserForCreate, AgentUserCreateInput):
        with pytest.raises(ValidationError):
            schema(username=username, password="Virty-Test_2026!")
