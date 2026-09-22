from datetime import timedelta
from typing import cast

import pytest
from fastapi import HTTPException
from fastapi.security import SecurityScopes
from sqlalchemy.orm import Session

from auth.router import (
    CurrentUser,
    create_access_token,
    get_current_user,
    scope_grants,
)


class _Query:
    def __init__(self, value: object) -> None:
        self.value = value

    def filter(self, *_args: object) -> "_Query":
        return self

    def one_or_none(self) -> object:
        return self.value


class _Session:
    def __init__(self, value: object) -> None:
        self.value = value

    def query(self, *_args: object) -> _Query:
        return _Query(self.value)


@pytest.mark.parametrize(
    ("granted", "required", "expected"),
    [
        ("vm.read", "vm.read", True),
        ("vm.*", "vm.read", True),
        ("vm", "vm.read", False),
        ("vm.read.more", "vm.read", False),
        ("read", "vm.read", False),
        ("user", "vm.read", True),
        ("user", "vm.delete", False),
        ("admin", "network.manage", True),
    ],
)
def test_scope_grants_only_exact_or_explicit_wildcard(
    granted: str,
    required: str,
    expected: bool,
) -> None:
    assert scope_grants(granted, required) is expected


def test_missing_scope_is_forbidden() -> None:
    user = CurrentUser(id="alice", token="token", scopes=["vm.read"])

    with pytest.raises(HTTPException) as exc_info:
        user.verify_scope(["vm.delete"])

    assert exc_info.value.status_code == 403


def test_access_token_preserves_project_constraint() -> None:
    token = create_access_token(
        {
            "sub": "alice",
            "scopes": ["vm.read"],
            "projects": ["a1b2c3"],
        },
        expires_delta=timedelta(minutes=1),
    )

    db_user = type(
        "DbUser",
        (),
        {
            "session_generation": None,
            "scopes": [type("Scope", (), {"name": "vm.read"})()],
            "projects": [type("Project", (), {"id": "a1b2c3"})()],
        },
    )()
    user = get_current_user(
        SecurityScopes(scopes=["vm.read"]),
        token,
        cast(Session, _Session(db_user)),
    )

    assert user.id == "alice"
    assert user.projects == ["a1b2c3"]


def test_invalid_token_is_unauthorized() -> None:
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(SecurityScopes(), "not-a-jwt", cast(Session, _Session(None)))

    assert exc_info.value.status_code == 401


def test_non_string_subject_is_unauthorized() -> None:
    token = create_access_token(
        {"sub": 123, "scopes": [], "projects": []},
        expires_delta=timedelta(minutes=1),
    )

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(SecurityScopes(), token, cast(Session, _Session(None)))

    assert exc_info.value.status_code == 401


def test_new_database_grant_does_not_expand_existing_token() -> None:
    token = create_access_token(
        {
            "sub": "alice",
            "scopes": ["vm.read"],
            "projects": ["a1b2c3"],
        },
        expires_delta=timedelta(minutes=1),
    )
    db_user = type(
        "DbUser",
        (),
        {
            "session_generation": None,
            "scopes": [
                type("Scope", (), {"name": "vm.read"})(),
                type("Scope", (), {"name": "vm.delete"})(),
            ],
            "projects": [
                type("Project", (), {"id": "a1b2c3"})(),
                type("Project", (), {"id": "ffffff"})(),
            ],
        },
    )()

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(
            SecurityScopes(scopes=["vm.delete"]),
            token,
            cast(Session, _Session(db_user)),
        )

    assert exc_info.value.status_code == 403
    current = get_current_user(
        SecurityScopes(),
        token,
        cast(Session, _Session(db_user)),
    )
    assert current.projects == ["a1b2c3"]
