import ast
import re
from pathlib import Path
from typing import cast

import pytest
from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict, ValidationError, field_validator
from starlette.exceptions import HTTPException as StarletteHTTPException

from agent.exceptions import AgentError, NotFoundError
from agent.router import AgentAPIRoute
from mixin.exception import (
    AgentNoStoreMiddleware,
    ApiCORSMiddleware,
    ApiError,
    ApiErrorCode,
    ApiErrorDetail,
    ApiFieldError,
    FieldErrorCode,
    api_error_exception_handler,
    api_error_response,
    http_exception_handler,
    _normalized_field_error,
    unhandled_exception_handler,
    validation_exception_handler,
)


pytestmark = [pytest.mark.unit, pytest.mark.timeout(10)]


class _ValidationBody(BaseModel):
    count: int
    password: str

    @field_validator("password")
    @classmethod
    def reject_password(cls, value: str) -> str:
        raise ValueError(f"rejected secret: {value}")


def _test_application() -> FastAPI:
    application = FastAPI()
    application.add_exception_handler(ApiError, api_error_exception_handler)
    application.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,
    )
    application.add_exception_handler(
        StarletteHTTPException,
        http_exception_handler,
    )
    application.add_exception_handler(Exception, unhandled_exception_handler)

    @application.get("/known")
    def known_error() -> None:
        raise ApiError(
            404,
            ApiErrorCode.NODE_NOT_FOUND,
            "The node was not found.",
            params={"resource": "node"},
        )

    @application.get("/unknown-http")
    def unknown_http_error() -> None:
        raise HTTPException(418, detail="secret internal detail")

    @application.get("/unknown-http-list")
    def unknown_http_list_error() -> None:
        raise HTTPException(
            400,
            detail=[{"msg": "secret list detail", "input": "secret input"}],
        )

    @application.get("/forbidden")
    def forbidden_error() -> None:
        raise ApiError(
            403,
            ApiErrorCode.SCOPE_DENIED,
            "The required permission is missing.",
        )

    @application.get("/conflict")
    def conflict_error() -> None:
        raise ApiError(
            409,
            ApiErrorCode.LAST_ADMIN_REQUIRED,
            "The last administrator cannot be deleted.",
        )

    @application.post("/validate")
    def validate_body(_: _ValidationBody) -> dict[str, bool]:
        return {"accepted": True}

    @application.get("/unhandled")
    def unhandled_error() -> None:
        raise RuntimeError("secret internal failure")

    return application


def test_error_response_omits_unused_optional_members() -> None:
    response = api_error_response(
        status_code=404,
        code=ApiErrorCode.NODE_NOT_FOUND,
        message="The node was not found.",
    )
    assert response.body == (
        b'{"detail":{"code":"node_not_found",'
        b'"message":"The node was not found."}}'
    )


def test_error_response_rejects_non_scalar_params() -> None:
    with pytest.raises(ValidationError):
        api_error_response(
            status_code=400,
            code=ApiErrorCode.BAD_REQUEST,
            message="The request could not be processed.",
            params=cast(dict[str, str | int | float | bool | None], {"unsafe": []}),
        )


def test_no_store_replaces_cache_control_case_insensitively() -> None:
    response = api_error_response(
        status_code=404,
        code=ApiErrorCode.NODE_NOT_FOUND,
        message="The node was not found.",
        headers={"cache-control": "public, max-age=3600"},
        no_store=True,
    )

    assert response.headers.getlist("cache-control") == ["no-store"]


def test_rejected_cors_preflight_uses_common_envelope_and_agent_no_store() -> None:
    application = FastAPI()
    application.add_middleware(
        ApiCORSMiddleware,
        allow_origins=["https://allowed.example"],
        allow_methods=["GET"],
        allow_headers=["X-Allowed"],
    )
    application.add_middleware(AgentNoStoreMiddleware)
    client = TestClient(application)

    response = client.options(
        "/api/agent/v1/devices",
        headers={
            "Origin": "https://denied.example",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "X-Denied",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": {
            "code": "bad_request",
            "message": "The CORS preflight request was rejected.",
        }
    }
    assert response.headers["content-type"] == "application/json"
    assert response.headers["cache-control"] == "no-store"


def test_null_parameter_value_is_preserved() -> None:
    response = api_error_response(
        status_code=400,
        code=ApiErrorCode.BAD_REQUEST,
        message="The request could not be processed.",
        params={"limit": None},
    )

    assert response.body == (
        b'{"detail":{"code":"bad_request",'
        b'"message":"The request could not be processed.",'
        b'"params":{"limit":null}}}'
    )


def test_optional_error_members_reject_explicit_null() -> None:
    with pytest.raises(ValidationError):
        ApiErrorDetail(
            code=ApiErrorCode.BAD_REQUEST,
            message="The request could not be processed.",
            params=None,  # type: ignore[arg-type]
        )

    with pytest.raises(ValidationError):
        ApiFieldError(
            field="body.name",
            code=FieldErrorCode.INVALID_VALUE,
            params=None,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "error_type",
    ["url_parsing", "ip_v4_address", "string_pattern_mismatch"],
)
def test_format_validation_errors_take_precedence_over_generic_types(
    error_type: str,
) -> None:
    error = _normalized_field_error({"loc": ("body", "value"), "type": error_type})

    assert error.code is FieldErrorCode.INVALID_FORMAT
    assert error.params == {}


def test_error_codes_reject_unregistered_values() -> None:
    with pytest.raises(ValueError):
        ApiError(
            400,
            cast(ApiErrorCode, "unregistered_error"),
            "This must not be accepted.",
        )

    with pytest.raises(ValueError):
        AgentError("unregistered_error", "内部detail")


def test_public_error_codes_are_lower_snake_case() -> None:
    pattern = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")

    assert len(ApiErrorCode.__members__) == len(ApiErrorCode)
    assert len(FieldErrorCode.__members__) == len(FieldErrorCode)
    assert all(pattern.fullmatch(code.value) for code in ApiErrorCode)
    assert all(pattern.fullmatch(code.value) for code in FieldErrorCode)


def test_agent_literal_error_codes_are_registered() -> None:
    error_types = {
        "AgentError",
        "AuthenticationError",
        "AuthorizationError",
        "ConflictError",
        "NotFoundError",
        "ServiceUnavailableError",
    }
    registered = {code.value for code in ApiErrorCode}
    api_root = Path(__file__).resolve().parents[2]
    found: set[str] = set()
    unexpected: list[str] = []

    for source_path in (api_root / "agent").glob("*.py"):
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                continue
            if node.func.id not in error_types:
                continue
            if not node.args:
                unexpected.append(f"{source_path.name}:{node.lineno}")
                continue
            code_node = node.args[0]
            if isinstance(code_node, ast.Constant) and isinstance(code_node.value, str):
                found.add(code_node.value)
            elif not (
                isinstance(code_node, ast.Attribute)
                and isinstance(code_node.value, ast.Name)
                and code_node.value.id == "ApiErrorCode"
            ):
                unexpected.append(f"{source_path.name}:{node.lineno}")

    assert found
    assert not unexpected
    assert found <= registered


def test_normal_api_routes_do_not_raise_unstructured_http_errors() -> None:
    api_root = Path(__file__).resolve().parents[2]
    source_paths = [
        path
        for package in api_root.iterdir()
        if package.is_dir() and package.name not in {"agent", "tests"}
        for path in package.glob("router*.py")
    ]
    source_paths.append(api_root / "resource_authorization.py")
    unexpected: list[str] = []

    for source_path in source_paths:
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "HTTPException"
            ):
                unexpected.append(f"{source_path.relative_to(api_root)}:{node.lineno}")

    assert not unexpected


def test_known_api_error_uses_common_envelope() -> None:
    response = TestClient(_test_application()).get("/known")

    assert response.status_code == 404
    assert response.json() == {
        "detail": {
            "code": "node_not_found",
            "message": "The node was not found.",
            "params": {"resource": "node"},
        }
    }


@pytest.mark.parametrize(
    ("path", "status_code", "code", "message"),
    [
        (
            "/forbidden",
            403,
            "scope_denied",
            "The required permission is missing.",
        ),
        (
            "/conflict",
            409,
            "last_admin_required",
            "The last administrator cannot be deleted.",
        ),
    ],
)
def test_forbidden_and_conflict_use_common_envelope(
    path: str,
    status_code: int,
    code: str,
    message: str,
) -> None:
    response = TestClient(_test_application()).get(path)

    assert response.status_code == status_code
    assert response.json() == {
        "detail": {
            "code": code,
            "message": message,
        }
    }


def test_unknown_http_detail_is_not_exposed() -> None:
    response = TestClient(_test_application()).get("/unknown-http")

    assert response.status_code == 418
    assert response.json() == {
        "detail": {
            "code": "http_error",
            "message": "The HTTP request failed.",
        }
    }
    assert "secret internal detail" not in response.text

    list_response = TestClient(_test_application()).get("/unknown-http-list")
    assert list_response.status_code == 400
    assert list_response.json() == {
        "detail": {
            "code": "bad_request",
            "message": "The request could not be processed.",
        }
    }
    assert "secret list detail" not in list_response.text
    assert "secret input" not in list_response.text


def test_unhandled_exception_uses_safe_common_envelope() -> None:
    response = TestClient(
        _test_application(),
        raise_server_exceptions=False,
    ).get("/unhandled")

    assert response.status_code == 500
    assert response.json() == {
        "detail": {
            "code": "internal_server_error",
            "message": "An internal server error occurred.",
        }
    }
    assert "secret internal failure" not in response.text


def test_validation_error_contains_only_safe_structured_fields() -> None:
    secret = "DoNotReturnThisPassword"
    response = TestClient(_test_application()).post(
        "/validate",
        json={"count": "not-an-integer", "password": secret},
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": {
            "code": "validation_error",
            "message": "Request validation failed.",
            "errors": [
                {
                    "field": "body.count",
                    "code": FieldErrorCode.INVALID_TYPE.value,
                    "params": {"expected": "integer"},
                },
                {
                    "field": "body.password",
                    "code": FieldErrorCode.INVALID_VALUE.value,
                },
            ],
        }
    }
    assert secret not in response.text
    assert "rejected secret" not in response.text
    assert '"input"' not in response.text
    assert '"ctx"' not in response.text
    assert '"msg"' not in response.text


def test_extra_field_name_is_not_reflected() -> None:
    class StrictBody(BaseModel):
        model_config = ConfigDict(extra="forbid")

        name: str

    application = FastAPI()
    application.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,
    )

    @application.post("/strict")
    def strict_body(_: StrictBody) -> dict[str, bool]:
        return {"accepted": True}

    secret_field = "password_DoNotReturn"
    response = TestClient(application).post(
        "/strict",
        json={"name": "valid", secret_field: "secret"},
    )

    assert response.status_code == 422
    error = response.json()["detail"]["errors"][0]
    assert error == {"field": "body.*", "code": "extra_forbidden"}
    assert secret_field not in response.text


def test_agent_routes_are_no_store_on_success_and_all_error_paths() -> None:
    router = APIRouter(prefix="/api/agent/v1", route_class=AgentAPIRoute)

    @router.get("/success")
    def success() -> dict[str, bool]:
        return {"ok": True}

    @router.get("/agent-error")
    def agent_error() -> None:
        raise NotFoundError("node_not_found", "nodeがありません")

    @router.get("/http-error")
    def agent_http_error() -> None:
        raise HTTPException(404, detail="秘密のHTTP detail")

    @router.get("/unhandled")
    def agent_unhandled_error() -> None:
        raise RuntimeError("秘密の内部例外")

    application = FastAPI()
    application.add_exception_handler(ApiError, api_error_exception_handler)
    application.add_exception_handler(
        StarletteHTTPException,
        http_exception_handler,
    )
    application.add_exception_handler(Exception, unhandled_exception_handler)
    application.include_router(router)
    application.add_middleware(AgentNoStoreMiddleware)

    client = TestClient(application, raise_server_exceptions=False)
    success_response = client.get("/api/agent/v1/success")
    agent_response = client.get("/api/agent/v1/agent-error")
    http_response = client.get("/api/agent/v1/http-error")
    unhandled_response = client.get("/api/agent/v1/unhandled")
    missing_route_response = client.get("/api/agent/v1/missing-route")
    method_response = client.post("/api/agent/v1/success")
    redirect_response = client.get(
        "/api/agent/v1/success/",
        follow_redirects=False,
    )

    assert success_response.status_code == 200
    assert success_response.json() == {"ok": True}
    assert agent_response.status_code == 404
    assert agent_response.json() == {
        "detail": {
            "code": "node_not_found",
            "message": "The requested resource was not found.",
        }
    }
    assert "nodeがありません" not in agent_response.text
    assert http_response.status_code == 404
    assert http_response.json() == {
        "detail": {
            "code": "resource_not_found",
            "message": "The requested resource was not found.",
        }
    }
    assert "秘密のHTTP detail" not in http_response.text
    assert unhandled_response.status_code == 500
    assert unhandled_response.json() == {
        "detail": {
            "code": "internal_server_error",
            "message": "An internal server error occurred.",
        }
    }
    assert "秘密の内部例外" not in unhandled_response.text
    assert missing_route_response.status_code == 404
    assert missing_route_response.json() == {
        "detail": {
            "code": "resource_not_found",
            "message": "The requested resource was not found.",
        }
    }
    assert method_response.status_code == 405
    assert method_response.json() == {
        "detail": {
            "code": "method_not_allowed",
            "message": "The HTTP method is not allowed for this resource.",
        }
    }
    assert method_response.headers["allow"] == "GET"
    assert redirect_response.status_code == 307
    for response in (
        success_response,
        agent_response,
        http_response,
        unhandled_response,
        missing_route_response,
        method_response,
        redirect_response,
    ):
        assert response.headers["cache-control"] == "no-store"
