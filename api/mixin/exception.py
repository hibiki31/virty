"""APIへ公開する共通error契約と例外handler。"""

import logging
from enum import StrEnum
from math import isfinite
from typing import Any, Mapping, Sequence

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import Field, FiniteFloat
from sqlalchemy.orm.exc import NoResultFound as NoResultFound
from starlette.datastructures import Headers, MutableHeaders
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from mixin.schemas import BaseSchema

logger = logging.getLogger(__name__)

_AGENT_API_PREFIX = "/api/agent/v1"


class ApiErrorCode(StrEnum):
    """通常APIとAgent APIで共有する公開error code。"""

    ACTION_ADAPTER_MISSING = "action_adapter_missing"
    ACTION_NOT_FOUND = "action_not_found"
    AGENT_CONTROL_MISSING = "agent_control_missing"
    AGENT_PUBLIC_BASE_URL_MISSING = "agent_public_base_url_missing"
    AGENT_SIGNING_KEY_MISSING = "agent_signing_key_missing"
    AGENT_SIGNING_KEY_TOO_SHORT = "agent_signing_key_too_short"
    ALREADY_INITIALIZED = "already_initialized"
    AUDIT_UNAVAILABLE = "audit_unavailable"
    AUTHENTICATION_REQUIRED = "authentication_required"
    BAD_REQUEST = "bad_request"
    CATALOG_ACTION_MISSING_AT_DISPATCH = "catalog_action_missing_at_dispatch"
    CATALOG_RISK_MISMATCH_AT_DISPATCH = "catalog_risk_mismatch_at_dispatch"
    CATALOG_SELECTOR_MISMATCH_AT_DISPATCH = "catalog_selector_mismatch_at_dispatch"
    CDROM_IMAGE_NOT_FOUND = "cdrom_image_not_found"
    CDROM_IMAGE_REQUIRED = "cdrom_image_required"
    CHALLENGE_EXPIRED = "challenge_expired"
    CHALLENGE_MISMATCH = "challenge_mismatch"
    CHALLENGE_NOT_FOUND = "challenge_not_found"
    CHALLENGE_REPLAY = "challenge_replay"
    CONFLICT = "conflict"
    COPY_SOURCE_REQUIRED = "copy_source_required"
    DESTINATION_PROJECT_DENIED = "destination_project_denied"
    DESTRUCTIVE_ACTION_DENIED = "destructive_action_denied"
    DESTRUCTIVE_ACTION_DENIED_AT_DISPATCH = "destructive_action_denied_at_dispatch"
    DEVICE_BREAKER_OPEN = "device_breaker_open"
    DEVICE_INACTIVE = "device_inactive"
    DEVICE_INACTIVE_AFTER_DPOP = "device_inactive_after_dpop"
    DEVICE_INACTIVE_AT_DISPATCH = "device_inactive_at_dispatch"
    DEVICE_KEY_EXISTS = "device_key_exists"
    DEVICE_KEY_MISMATCH = "device_key_mismatch"
    DEVICE_MISSING_AT_HANDLER = "device_missing_at_handler"
    DEVICE_NOT_FOUND = "device_not_found"
    DEVICE_PRINCIPAL_CHANGED_AFTER_DPOP = "device_principal_changed_after_dpop"
    DEVICE_PRINCIPAL_MISMATCH = "device_principal_mismatch"
    DEVICE_REVOKED = "device_revoked"
    DIRECT_ACTION_KIND_MISMATCH = "direct_action_kind_mismatch"
    DIRECT_REQUEST_INVALID = "direct_request_invalid"
    DPOP_METHOD_MISMATCH = "dpop_method_mismatch"
    DPOP_REPLAY = "dpop_replay"
    DPOP_REPLAY_STORE_UNAVAILABLE = "dpop_replay_store_unavailable"
    DPOP_TOKEN_MISMATCH = "dpop_token_mismatch"
    DPOP_URI_MISMATCH = "dpop_uri_mismatch"
    EXPECTED_GENERATION_REQUIRED = "expected_generation_required"
    FLAVOR_CONSTRAINT_DENIED = "flavor_constraint_denied"
    FLAVOR_EXISTS = "flavor_exists"
    FLAVOR_IN_USE = "flavor_in_use"
    FLAVOR_NOT_FOUND = "flavor_not_found"
    FLAVOR_PROJECT_DENIED = "flavor_project_denied"
    GENERATION_SENTINEL_REQUIRED = "generation_sentinel_required"
    GENERATION_TARGET_INVALID = "generation_target_invalid"
    GENERATION_TARGET_MISSING = "generation_target_missing"
    GLOBAL_ADMIN_REQUIRED = "global_admin_required"
    GLOBAL_MUTATION_REQUIRES_UNSCOPED_LEASE = (
        "global_mutation_requires_unscoped_lease"
    )
    HTTP_ERROR = "http_error"
    IDEMPOTENCY_KEY_CONFLICT = "idempotency_key_conflict"
    IDEMPOTENCY_KEY_REQUIRED = "idempotency_key_required"
    IDENTITY_TARGET_MISSING_AT_DISPATCH = "identity_target_missing_at_dispatch"
    IMAGE_ADDRESS_DENIED = "image_address_denied"
    IMAGE_FILENAME_REQUIRED = "image_filename_required"
    IMAGE_HOST_DENIED = "image_host_denied"
    IMAGE_HOST_UNRESOLVED = "image_host_unresolved"
    IMAGE_NODE_MISMATCH = "image_node_mismatch"
    IMAGE_NOT_FOUND = "image_not_found"
    IMAGE_OR_FLAVOR_NOT_FOUND = "image_or_flavor_not_found"
    IMAGE_PROJECT_GRANT_DENIED = "image_project_grant_denied"
    IMAGE_STORAGE_PROJECT_DENIED = "image_storage_project_denied"
    IMAGE_STORAGE_TARGET_MISSING = "image_storage_target_missing"
    IMAGE_URL_DENIED = "image_url_denied"
    INACTIVE_USER = "inactive_user"
    INTERNAL_SERVER_ERROR = "internal_server_error"
    INVALID_ACTION_INPUT = "invalid_action_input"
    INVALID_CONSOLE_TICKET = "invalid_console_ticket"
    INVALID_CREDENTIALS = "invalid_credentials"
    INVALID_DEVICE_KEY = "invalid_device_key"
    INVALID_DPOP = "invalid_dpop"
    INVALID_LEASE = "invalid_lease"
    INVALID_LEASE_REQUEST_STATUS = "invalid_lease_request_status"
    INVALID_MUTATION_RISK = "invalid_mutation_risk"
    INVALID_OPERATION_RESOLUTION = "invalid_operation_resolution"
    INVALID_PAIRING_STATUS = "invalid_pairing_status"
    INVALID_SSH_PRIVATE_KEY = "invalid_ssh_private_key"
    INVALID_TOKEN = "invalid_token"
    INVALID_VALUE = "invalid_value"
    INVALID_WEBAUTHN_ASSERTION = "invalid_webauthn_assertion"
    INVALID_WEBAUTHN_PURPOSE = "invalid_webauthn_purpose"
    INVALID_WEBAUTHN_REGISTRATION = "invalid_webauthn_registration"
    JSONSCHEMA_DEPENDENCY_MISSING = "jsonschema_dependency_missing"
    LAST_ADMIN_REQUIRED = "last_admin_required"
    LAST_ADMIN_SCOPE_REQUIRED = "last_admin_scope_required"
    LAST_PROJECT_MEMBER_REQUIRED = "last_project_member_required"
    LEASE_ALREADY_EXCHANGED = "lease_already_exchanged"
    LEASE_EXPIRED = "lease_expired"
    LEASE_INACTIVE_AFTER_DPOP = "lease_inactive_after_dpop"
    LEASE_INACTIVE_AT_DISPATCH = "lease_inactive_at_dispatch"
    LEASE_INTEGRITY_ERROR = "lease_integrity_error"
    LEASE_MISMATCH = "lease_mismatch"
    LEASE_MISSING = "lease_missing"
    LEASE_MISSING_AT_HANDLER = "lease_missing_at_handler"
    LEASE_NOT_APPROVED = "lease_not_approved"
    LEASE_NOT_FOUND = "lease_not_found"
    LEASE_PRINCIPAL_MISMATCH = "lease_principal_mismatch"
    LEASE_REQUEST_ALREADY_PENDING = "lease_request_already_pending"
    LEASE_REQUEST_CAPACITY_EXCEEDED = "lease_request_capacity_exceeded"
    LEASE_REQUEST_NOT_FOUND = "lease_request_not_found"
    LEASE_REQUEST_NOT_PENDING = "lease_request_not_pending"
    LEASE_REQUIRED = "lease_required"
    LEASE_REVOKED = "lease_revoked"
    LEASE_SCOPE_ESCALATION = "lease_scope_escalation"
    METHOD_NOT_ALLOWED = "method_not_allowed"
    MUTATION_CONCURRENCY_LIMIT = "mutation_concurrency_limit"
    MUTATION_LIMIT_EXHAUSTED = "mutation_limit_exhausted"
    MUTATION_TARGET_MISSING = "mutation_target_missing"
    MUTATIONS_DISABLED = "mutations_disabled"
    MUTATIONS_DISABLED_AT_DISPATCH = "mutations_disabled_at_dispatch"
    NETWORK_CONSTRAINT_DENIED = "network_constraint_denied"
    NETWORK_NODE_MISMATCH = "network_node_mismatch"
    NETWORK_NODE_NOT_FOUND = "network_node_not_found"
    NETWORK_NOT_FOUND = "network_not_found"
    NETWORK_OR_POOL_NOT_FOUND = "network_or_pool_not_found"
    NETWORK_OR_PORT_NOT_FOUND = "network_or_port_not_found"
    NETWORK_POOL_NOT_FOUND = "network_pool_not_found"
    NETWORK_POOL_IN_USE = "network_pool_in_use"
    NETWORK_PORT_NOT_FOUND = "network_port_not_found"
    NETWORK_VM_NODE_MISMATCH = "network_vm_node_mismatch"
    NETWORK_XML_NOT_FOUND = "network_xml_not_found"
    NODE_DENIED = "node_denied"
    NODE_DENIED_AT_DISPATCH = "node_denied_at_dispatch"
    NODE_MISSING_AT_DISPATCH = "node_missing_at_dispatch"
    NODE_NOT_FOUND = "node_not_found"
    OOB_REQUIRED = "oob_required"
    OOB_REQUIRED_AT_DISPATCH = "oob_required_at_dispatch"
    OPERATION_ACTION_MISMATCH = "operation_action_mismatch"
    OPERATION_ACTION_NOT_FOUND = "operation_action_not_found"
    OPERATION_DEPENDENCY_CYCLE_AT_DISPATCH = "operation_dependency_cycle_at_dispatch"
    OPERATION_DEPENDENCY_INVALID_AT_DISPATCH = "operation_dependency_invalid_at_dispatch"
    OPERATION_NODE_DENIED = "operation_node_denied"
    OPERATION_NOT_FOUND = "operation_not_found"
    OPERATION_NOT_UNKNOWN = "operation_not_unknown"
    OPERATION_OWNER_MISMATCH = "operation_owner_mismatch"
    OPERATION_PROJECT_DENIED = "operation_project_denied"
    OPERATION_ROOT_INVALID_AT_DISPATCH = "operation_root_invalid_at_dispatch"
    OPERATION_TARGET_INVALID = "operation_target_invalid"
    OPERATION_TARGET_MISSING = "operation_target_missing"
    OPERATION_TIMESTAMP_MISSING = "operation_timestamp_missing"
    PAIRING_CAPACITY_EXCEEDED = "pairing_capacity_exceeded"
    PAIRING_EXPIRED = "pairing_expired"
    PAIRING_NOT_FOUND = "pairing_not_found"
    PAIRING_NOT_PENDING = "pairing_not_pending"
    PAIRING_SCOPE_ESCALATION = "pairing_scope_escalation"
    PASSWORD_REAUTHENTICATION_FAILED = "password_reauthentication_failed"
    PERMISSION_DENIED = "permission_denied"
    PRINCIPAL_AUTHORITY_REVOKED = "principal_authority_revoked"
    PRINCIPAL_AUTHORITY_REVOKED_AT_DISPATCH = "principal_authority_revoked_at_dispatch"
    PRINCIPAL_MISMATCH = "principal_mismatch"
    PRINCIPAL_MISMATCH_AT_HANDLER = "principal_mismatch_at_handler"
    PRINCIPAL_NOT_FOUND = "principal_not_found"
    PRINCIPAL_PROJECT_REVOKED = "principal_project_revoked"
    PROJECT_CONSTRAINT_DENIED = "project_constraint_denied"
    PROJECT_DENIED = "project_denied"
    PROJECT_DENIED_AT_DISPATCH = "project_denied_at_dispatch"
    PROJECT_MISSING_AT_DISPATCH = "project_missing_at_dispatch"
    PROJECT_GRANT_CONFLICT = "project_grant_conflict"
    PROJECT_GRANT_NOT_FOUND = "project_grant_not_found"
    PROJECT_GRANT_RESOURCE_NOT_FOUND = "project_grant_resource_not_found"
    PROJECT_MEMBERSHIP_DENIED = "project_membership_denied"
    PROJECT_MEMBER_CONFLICT = "project_member_conflict"
    PROJECT_MEMBER_NOT_FOUND = "project_member_not_found"
    PROJECT_NOT_EMPTY = "project_not_empty"
    PROJECT_NOT_FOUND = "project_not_found"
    PROJECT_OR_USER_NOT_FOUND = "project_or_user_not_found"
    PROJECT_SCOPE_ESCALATION = "project_scope_escalation"
    PROJECT_UPDATE_CONFLICT = "project_update_conflict"
    R3_CONCURRENCY_LIMIT = "r3_concurrency_limit"
    RATE_LIMITED = "rate_limited"
    RECOVERY_REQUIRED = "recovery_required"
    RECOVERY_REQUIRED_AT_DISPATCH = "recovery_required_at_dispatch"
    RELATED_IMAGE_INVALID = "related_image_invalid"
    RELATED_NODE_CHANGED_AT_DISPATCH = "related_node_changed_at_dispatch"
    RELATED_PROJECT_CHANGED_AT_DISPATCH = "related_project_changed_at_dispatch"
    RELATED_TARGET_MISSING_AT_DISPATCH = "related_target_missing_at_dispatch"
    REQUEST_TOO_LARGE = "request_too_large"
    RESOLVED_TARGET_MISSING_AT_HANDLER = "resolved_target_missing_at_handler"
    RESOURCE_ID_REQUIRED = "resource_id_required"
    RESOURCE_IN_USE = "resource_in_use"
    RESOURCE_NOT_FOUND = "resource_not_found"
    RESOURCE_TYPE_MISMATCH = "resource_type_mismatch"
    RISK_DISABLED = "risk_disabled"
    RISK_DISABLED_AT_DISPATCH = "risk_disabled_at_dispatch"
    SCOPE_DENIED = "scope_denied"
    SCOPED_GLOBAL_READ_DENIED = "scoped_global_read_denied"
    SELF_DELETE_DENIED = "self_delete_denied"
    SERVICE_UNAVAILABLE = "service_unavailable"
    SSH_KEY_PAIR_REQUIRED = "ssh_key_pair_required"
    SSH_PUBLIC_KEY_MISMATCH = "ssh_public_key_mismatch"
    SSH_PUBLIC_KEY_NOT_FOUND = "ssh_public_key_not_found"
    STALE_DPOP = "stale_dpop"
    STALE_GENERATION = "stale_generation"
    STORAGE_CONSTRAINT_DENIED = "storage_constraint_denied"
    STORAGE_NODE_MISMATCH = "storage_node_mismatch"
    STORAGE_NOT_FOUND = "storage_not_found"
    STORAGE_POOL_IN_USE = "storage_pool_in_use"
    STORAGE_POOL_NOT_FOUND = "storage_pool_not_found"
    STORAGE_PROJECT_DENIED = "storage_project_denied"
    TARGET_BUSY = "target_busy"
    TARGET_MAPPING_MISMATCH = "target_mapping_mismatch"
    TARGET_NOT_FOUND = "target_not_found"
    TASK_NOT_FOUND = "task_not_found"
    TASK_OWNERSHIP_DENIED = "task_ownership_denied"
    TASK_PRINCIPAL_MISMATCH_AT_DISPATCH = "task_principal_mismatch_at_dispatch"
    TASK_SELECTOR_MISSING = "task_selector_missing"
    TOKEN_EXPIRED = "token_expired"
    UNKNOWN_ACTION_SCOPE = "unknown_action_scope"
    UNKNOWN_LEASE = "unknown_lease"
    UNKNOWN_WEBAUTHN_CREDENTIAL = "unknown_webauthn_credential"
    UNSUPPORTED_MEDIA_TYPE = "unsupported_media_type"
    UNSUPPORTED_SSH_KEY = "unsupported_ssh_key"
    USER_EXISTS = "user_exists"
    USER_ID_REQUIRED = "user_id_required"
    USER_NOT_FOUND = "user_not_found"
    USERNAME_MISMATCH = "username_mismatch"
    VALIDATION_ERROR = "validation_error"
    VM_NETWORK_PROJECT_DENIED = "vm_network_project_denied"
    VM_COPY_SOURCE_REQUIRED = "vm_copy_source_required"
    VM_IMAGE_PROJECT_DENIED = "vm_image_project_denied"
    VM_NOT_FOUND = "vm_not_found"
    VM_OWNER_DENIED = "vm_owner_denied"
    VM_OR_PROJECT_NOT_FOUND = "vm_or_project_not_found"
    VM_PROJECT_BINDING_CHANGED = "vm_project_binding_changed"
    VM_PROJECT_DENIED = "vm_project_denied"
    VM_PROJECT_RESOURCE_CONFLICT = "vm_project_resource_conflict"
    VM_SOURCE_DENIED = "vm_source_denied"
    VM_STORAGE_PROJECT_DENIED = "vm_storage_project_denied"
    VM_XML_NOT_FOUND = "vm_xml_not_found"
    WEBAUTHN_CHALLENGE_CAPACITY_EXCEEDED = "webauthn_challenge_capacity_exceeded"
    WEBAUTHN_CREDENTIAL_EXISTS = "webauthn_credential_exists"
    WEBAUTHN_DEPENDENCY_MISSING = "webauthn_dependency_missing"
    WEBAUTHN_ENROLLMENT_REQUIRED = "webauthn_enrollment_required"


class FieldErrorCode(StrEnum):
    """Pydantic固有表現から独立した公開field error code。"""

    EXTRA_FORBIDDEN = "extra_forbidden"
    GREATER_THAN = "greater_than"
    GREATER_THAN_OR_EQUAL = "greater_than_or_equal"
    INVALID_CHOICE = "invalid_choice"
    INVALID_FORMAT = "invalid_format"
    INVALID_JSON = "invalid_json"
    INVALID_TYPE = "invalid_type"
    INVALID_VALUE = "invalid_value"
    LESS_THAN = "less_than"
    LESS_THAN_OR_EQUAL = "less_than_or_equal"
    MULTIPLE_OF = "multiple_of"
    REQUIRED = "required"
    TOO_LONG = "too_long"
    TOO_SHORT = "too_short"
    PASSWORD_POLICY = "password_policy"
    INVALID_PUBLIC_KEY = "invalid_public_key"
    DUPLICATE_KEY_NAME = "duplicate_key_name"
    KEY_NAME_REQUIRED = "key_name_required"
    INVALID_USERNAME = "invalid_username"


ApiErrorParam = str | int | FiniteFloat | bool | None


class ApiFieldError(BaseSchema):
    field: str
    code: FieldErrorCode
    params: dict[str, ApiErrorParam] = Field(default_factory=dict)


class ApiErrorDetail(BaseSchema):
    code: ApiErrorCode
    message: str
    params: dict[str, ApiErrorParam] = Field(default_factory=dict)
    errors: list[ApiFieldError] = Field(default_factory=list)


class ApiErrorResponse(BaseSchema):
    detail: ApiErrorDetail


COMMON_ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    "default": {
        "model": ApiErrorResponse,
        "description": "API Error",
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/ApiErrorResponse"},
            },
        },
    },
    422: {
        "model": ApiErrorResponse,
        "description": "Validation Error",
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/ApiErrorResponse"},
            },
        },
    },
}


class ApiError(HTTPException):
    """公開codeと英語fallbackを必須にする通常API例外。"""

    def __init__(
        self,
        status_code: int,
        code: ApiErrorCode,
        message: str,
        *,
        params: Mapping[str, ApiErrorParam] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=message, headers=headers)
        self.code = ApiErrorCode(code)
        self.message = message
        self.params = dict(params) if params else None


def agent_error_message(status_code: int) -> str:
    """Agent内部の既存日本語detailを変更せず公開用英語fallbackを返す。"""

    return {
        status.HTTP_400_BAD_REQUEST: "The request could not be processed.",
        status.HTTP_422_UNPROCESSABLE_ENTITY: "The request could not be processed.",
        status.HTTP_401_UNAUTHORIZED: "Authentication failed.",
        status.HTTP_403_FORBIDDEN: "Permission denied.",
        status.HTTP_404_NOT_FOUND: "The requested resource was not found.",
        status.HTTP_409_CONFLICT: "The request conflicts with the current state.",
        status.HTTP_503_SERVICE_UNAVAILABLE: "The service is temporarily unavailable.",
    }.get(status_code, "The request could not be completed.")


def api_error_response(
    *,
    status_code: int,
    code: ApiErrorCode,
    message: str,
    params: Mapping[str, ApiErrorParam] | None = None,
    errors: Sequence[ApiFieldError] | None = None,
    headers: Mapping[str, str] | None = None,
    no_store: bool = False,
) -> JSONResponse:
    """全API経路で同じenvelopeを生成する。"""

    response_headers = dict(headers or {})
    if no_store:
        response_headers = {
            key: value
            for key, value in response_headers.items()
            if key.lower() != "cache-control"
        }
        response_headers["Cache-Control"] = "no-store"
    envelope = ApiErrorResponse(
        detail=ApiErrorDetail(
            code=ApiErrorCode(code),
            message=message,
            params=dict(params) if params else {},
            errors=list(errors) if errors else [],
        )
    )
    return JSONResponse(
        status_code=status_code,
        content=envelope.model_dump(
            mode="json",
            by_alias=True,
            exclude_defaults=True,
        ),
        headers=response_headers,
    )


_HTTP_ERROR_DEFAULTS: dict[int, tuple[ApiErrorCode, str]] = {
    status.HTTP_400_BAD_REQUEST: (
        ApiErrorCode.BAD_REQUEST,
        "The request could not be processed.",
    ),
    status.HTTP_401_UNAUTHORIZED: (
        ApiErrorCode.AUTHENTICATION_REQUIRED,
        "Authentication is required.",
    ),
    status.HTTP_403_FORBIDDEN: (
        ApiErrorCode.PERMISSION_DENIED,
        "Permission denied.",
    ),
    status.HTTP_404_NOT_FOUND: (
        ApiErrorCode.RESOURCE_NOT_FOUND,
        "The requested resource was not found.",
    ),
    status.HTTP_405_METHOD_NOT_ALLOWED: (
        ApiErrorCode.METHOD_NOT_ALLOWED,
        "The HTTP method is not allowed for this resource.",
    ),
    status.HTTP_409_CONFLICT: (
        ApiErrorCode.CONFLICT,
        "The request conflicts with the current state.",
    ),
    status.HTTP_413_REQUEST_ENTITY_TOO_LARGE: (
        ApiErrorCode.REQUEST_TOO_LARGE,
        "The request body is too large.",
    ),
    status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: (
        ApiErrorCode.UNSUPPORTED_MEDIA_TYPE,
        "The request media type is not supported.",
    ),
    status.HTTP_429_TOO_MANY_REQUESTS: (
        ApiErrorCode.RATE_LIMITED,
        "Too many requests.",
    ),
    status.HTTP_500_INTERNAL_SERVER_ERROR: (
        ApiErrorCode.INTERNAL_SERVER_ERROR,
        "An internal server error occurred.",
    ),
    status.HTTP_502_BAD_GATEWAY: (
        ApiErrorCode.SERVICE_UNAVAILABLE,
        "The service is temporarily unavailable.",
    ),
    status.HTTP_503_SERVICE_UNAVAILABLE: (
        ApiErrorCode.SERVICE_UNAVAILABLE,
        "The service is temporarily unavailable.",
    ),
    status.HTTP_504_GATEWAY_TIMEOUT: (
        ApiErrorCode.SERVICE_UNAVAILABLE,
        "The service is temporarily unavailable.",
    ),
}


def _is_agent_path(path: str) -> bool:
    return path == _AGENT_API_PREFIX or path.startswith(f"{_AGENT_API_PREFIX}/")


def _is_agent_request(request: Request) -> bool:
    return request.scope.get("virty.agent_api") is True or _is_agent_path(
        request.url.path,
    )


class AgentNoStoreMiddleware:
    """redirectやCORS preflightを含むAgent API応答を保存させない。"""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        path = scope.get("path")
        if (
            scope["type"] != "http"
            or not isinstance(path, str)
            or not _is_agent_path(path)
        ):
            await self.app(scope, receive, send)
            return

        async def send_no_store(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers["Cache-Control"] = "no-store"
            await send(message)

        await self.app(scope, receive, send_no_store)


class ApiCORSMiddleware(CORSMiddleware):
    """拒否したpreflightも共通JSON error契約へ変換する。"""

    def preflight_response(self, request_headers: Headers) -> Response:
        response = super().preflight_response(request_headers)
        if response.status_code < status.HTTP_400_BAD_REQUEST:
            return response

        # 元のplain-text responseのentity headerはJSON本文へ引き継がない。
        headers = {
            key: value
            for key, value in response.headers.items()
            if key.lower() not in {"content-length", "content-type"}
        }
        return api_error_response(
            status_code=response.status_code,
            code=ApiErrorCode.BAD_REQUEST,
            message="The CORS preflight request was rejected.",
            headers=headers,
        )


async def api_error_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    if not isinstance(exc, ApiError):
        raise TypeError("ApiError handlerへ想定外の例外が渡されました") from exc
    return api_error_response(
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
        params=exc.params,
        headers=exc.headers,
        no_store=_is_agent_request(request),
    )


async def http_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    if not isinstance(exc, StarletteHTTPException):
        raise TypeError("HTTPException handlerへ想定外の例外が渡されました") from exc
    code, message = _HTTP_ERROR_DEFAULTS.get(
        exc.status_code,
        (ApiErrorCode.HTTP_ERROR, "The HTTP request failed."),
    )
    return api_error_response(
        status_code=exc.status_code,
        code=code,
        message=message,
        headers=exc.headers,
        no_store=_is_agent_request(request),
    )


def _safe_number(value: object) -> int | float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if isinstance(value, float) and not isfinite(value):
        return None
    return value


def _field_name(location: Sequence[object], error_type: str) -> str:
    parts: list[str] = []
    for value in location:
        if isinstance(value, int):
            parts.append(str(value))
        elif isinstance(value, str) and value and len(value) <= 128:
            parts.append(value)
        else:
            parts.append("*")
    if error_type == "extra_forbidden" and parts:
        parts[-1] = "*"
    return ".".join(parts) or "request"


def _expected_type(error_type: str) -> str | None:
    prefixes = {
        "bool": "boolean",
        "bytes": "string",
        "date": "date",
        "datetime": "date_time",
        "decimal": "number",
        "dict": "object",
        "float": "number",
        "int": "integer",
        "list": "array",
        "mapping": "object",
        "model": "object",
        "set": "array",
        "string": "string",
        "time": "time",
        "tuple": "array",
        "uuid": "uuid",
    }
    prefix = error_type.split("_", 1)[0]
    return prefixes.get(prefix)


def _normalized_field_error(item: Mapping[str, Any]) -> ApiFieldError:
    error_type = str(item.get("type") or "invalid_value")
    location = item.get("loc")
    safe_location = (
        list(location)
        if isinstance(location, (list, tuple))
        else ["request"]
    )
    context = item.get("ctx")
    safe_context = context if isinstance(context, Mapping) else {}
    params: dict[str, ApiErrorParam] = {}

    if error_type in {"password_policy", "invalid_public_key", "duplicate_key_name",
                      "key_name_required", "invalid_username"}:
        code = FieldErrorCode(error_type)
    elif error_type == "missing":
        code = FieldErrorCode.REQUIRED
    elif error_type == "extra_forbidden":
        code = FieldErrorCode.EXTRA_FORBIDDEN
    elif error_type == "json_invalid":
        code = FieldErrorCode.INVALID_JSON
    elif error_type in {"literal_error", "enum"}:
        code = FieldErrorCode.INVALID_CHOICE
    elif error_type in {"string_too_short", "bytes_too_short", "too_short"}:
        code = FieldErrorCode.TOO_SHORT
        minimum = _safe_number(safe_context.get("min_length"))
        if minimum is not None:
            params["minimum"] = minimum
    elif error_type in {"string_too_long", "bytes_too_long", "too_long"}:
        code = FieldErrorCode.TOO_LONG
        maximum = _safe_number(safe_context.get("max_length"))
        if maximum is not None:
            params["maximum"] = maximum
    elif error_type == "greater_than":
        code = FieldErrorCode.GREATER_THAN
        limit = _safe_number(safe_context.get("gt"))
        if limit is not None:
            params["limit"] = limit
    elif error_type == "greater_than_equal":
        code = FieldErrorCode.GREATER_THAN_OR_EQUAL
        limit = _safe_number(safe_context.get("ge"))
        if limit is not None:
            params["limit"] = limit
    elif error_type == "less_than":
        code = FieldErrorCode.LESS_THAN
        limit = _safe_number(safe_context.get("lt"))
        if limit is not None:
            params["limit"] = limit
    elif error_type == "less_than_equal":
        code = FieldErrorCode.LESS_THAN_OR_EQUAL
        limit = _safe_number(safe_context.get("le"))
        if limit is not None:
            params["limit"] = limit
    elif error_type == "multiple_of":
        code = FieldErrorCode.MULTIPLE_OF
        multiple = _safe_number(safe_context.get("multiple_of"))
        if multiple is not None:
            params["multiple"] = multiple
    elif (
        "pattern" in error_type
        or error_type.startswith(("url_", "ip_"))
        or error_type in {"color_error", "timezone_aware", "timezone_naive"}
    ):
        code = FieldErrorCode.INVALID_FORMAT
    elif (
        error_type.endswith("_type")
        or error_type.endswith("_parsing")
        or error_type in {"iterable_type", "model_attributes_type"}
    ):
        code = FieldErrorCode.INVALID_TYPE
        expected = _expected_type(error_type)
        if expected is not None:
            params["expected"] = expected
    else:
        code = FieldErrorCode.INVALID_VALUE

    return ApiFieldError(
        field=_field_name(safe_location, error_type),
        code=code,
        params=params,
    )


def validation_error_response(
    request: Request,
    exc: RequestValidationError,
    *,
    no_store: bool | None = None,
) -> JSONResponse:
    """入力値、raw message、未選別ctxを含まない422応答を返す。"""

    errors = [_normalized_field_error(item) for item in exc.errors()]
    return api_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code=ApiErrorCode.VALIDATION_ERROR,
        message="Request validation failed.",
        errors=errors,
        no_store=_is_agent_request(request) if no_store is None else no_store,
    )


async def validation_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    if not isinstance(exc, RequestValidationError):
        raise TypeError("validation handlerへ想定外の例外が渡されました") from exc
    return validation_error_response(request, exc)


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.error(
        "未処理のAPI例外を共通errorへ変換しました",
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    return api_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code=ApiErrorCode.INTERNAL_SERVER_ERROR,
        message="An internal server error occurred.",
        no_store=_is_agent_request(request),
    )


def raise_notfound(
    detail: str = "The specified resource was not found.",
    *,
    code: ApiErrorCode = ApiErrorCode.RESOURCE_NOT_FOUND,
    params: Mapping[str, ApiErrorParam] | None = None,
) -> None:
    raise ApiError(
        status.HTTP_404_NOT_FOUND,
        code,
        detail,
        params=params,
    )


def raise_forbidden(
    detail: str = "You do not have permission to perform this action.",
    *,
    code: ApiErrorCode = ApiErrorCode.PERMISSION_DENIED,
    params: Mapping[str, ApiErrorParam] | None = None,
) -> None:
    raise ApiError(
        status.HTTP_403_FORBIDDEN,
        code,
        detail,
        params=params,
    )
