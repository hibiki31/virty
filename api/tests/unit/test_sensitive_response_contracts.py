from typing import cast

import pytest
from fastapi import HTTPException
from fastapi.routing import APIRoute
from sqlalchemy.orm import Session

from auth.schemas import SetupRequest
from auth.router import CurrentUser
from domain.schemas import CloudInitInsert
from node.schemas import SSHKeyPair
from user.router import app as user_router
from user.router import create_user, delete_user, get_users, update_user
from user.schemas import User, UserForCreate, UserForQuery, UserForUpdate


def _route(path: str, method: str) -> APIRoute:
    return next(
        route
        for route in user_router.routes
        if isinstance(route, APIRoute)
        and route.path == path
        and method in route.methods
    )


def test_user_write_routes_never_serialize_password_hashes() -> None:
    for path, method in (("/api/users", "POST"), ("/api/users/{username}", "PUT")):
        assert _route(path, method).response_model is User

    response = User.model_validate({
        "username": "operator",
        "hashed_password": "must-not-leak",
    }).model_dump(mode="json", by_alias=True)
    assert "hashedPassword" not in response
    assert "hashed_password" not in response
    assert "password" not in response


def test_secret_inputs_are_marked_write_only_in_openapi_schemas() -> None:
    fields = (
        (SetupRequest, "password"),
        (UserForCreate, "password"),
        (SSHKeyPair, "privateKey"),
        (CloudInitInsert, "userData"),
    )
    for schema_type, field_name in fields:
        schema = schema_type.model_json_schema(by_alias=True)
        assert schema["properties"][field_name]["writeOnly"] is True


def test_identity_manage_without_admin_cannot_mutate_or_list_users() -> None:
    delegated = CurrentUser(
        id="delegated",
        token="token",
        scopes=["identity.manage"],
    )
    create_request = UserForCreate(
        username="target",
        password="Strong1!Password",
    )
    update_request = UserForUpdate(
        username="target",
        password="Strong1!Password",
    )
    unreachable_db = cast(Session, object())
    calls = (
        lambda: create_user(create_request, db=unreachable_db, current_user=delegated),
        lambda: update_user(
            "target",
            update_request,
            db=unreachable_db,
            current_user=delegated,
        ),
        lambda: delete_user("target", db=unreachable_db, current_user=delegated),
        lambda: get_users(
            UserForQuery(),
            db=unreachable_db,
            current_user=delegated,
        ),
    )

    for call in calls:
        with pytest.raises(HTTPException) as exc_info:
            call()
        assert exc_info.value.status_code == 403
