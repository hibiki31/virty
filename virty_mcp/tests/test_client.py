from __future__ import annotations

import ast
import base64
import json
import ssl
from collections import deque
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from virty_mcp.client import AgentApiClient, AgentApiConfig, AgentApiError, redact_secrets
from virty_mcp.credentials import LeaseCredential, MemoryCredentialStore, ProfileRepository
from virty_mcp.crypto import DeviceKey


def _decode_segment(value: str) -> dict[str, Any]:
    return json.loads(base64.urlsafe_b64decode(value + "=" * (-len(value) % 4)))


class FakeTransport:
    def __init__(self, *responses: tuple[int, dict[str, Any]]) -> None:
        self.responses = deque(responses)
        self.requests: list[dict[str, Any]] = []

    def request(
        self,
        *,
        method: str,
        url: str,
        headers: Mapping[str, str],
        body: bytes | None,
        timeout: float,
        ssl_context: ssl.SSLContext,
    ) -> tuple[int, Mapping[str, str], bytes]:
        self.requests.append(
            {
                "method": method,
                "url": url,
                "headers": dict(headers),
                "body": None if body is None else json.loads(body),
                "timeout": timeout,
                "sslContext": ssl_context,
            }
        )
        status, response = self.responses.popleft()
        return status, {"Content-Type": "application/json"}, json.dumps(response).encode()


def _client(transport: FakeTransport) -> tuple[AgentApiClient, ProfileRepository]:
    repository = ProfileRepository(MemoryCredentialStore())
    client = AgentApiClient(
        config=AgentApiConfig(base_url="https://virty.internal"),
        repository=repository,
        transport=transport,
    )
    return client, repository


def _paired_repository(repository: ProfileRepository) -> None:
    repository.set_private_key_pem(DeviceKey.generate().to_pem())
    repository.set_device(
        {
            "deviceId": "device-1",
            "pairingId": "pair-1",
            "origin": "https://virty.internal/",
        }
    )


def test_pairing_generates_key_and_approved_poll_stores_device() -> None:
    transport = FakeTransport(
        (
            201,
            {
                "pairingId": "pair-1",
                "pairingCode": "ABCD-EFGH",
                "status": "pending",
                "expiresAt": "2026-08-22T01:00:00Z",
            },
        ),
        (
            200,
            {
                "pairingId": "pair-1",
                "deviceId": "device-1",
                "status": "active",
                "expiresAt": "2026-08-22T01:00:00Z",
            },
        ),
    )
    client, repository = _client(transport)

    pairing = client.create_pairing(device_name="ops-laptop", requested_scopes=["vm.get"])
    assert pairing["pairingCode"] == "ABCD-EFGH"
    assert repository.get_private_key_pem().startswith("-----BEGIN PRIVATE KEY-----")
    assert transport.requests[0]["body"]["publicKeyJwk"]["crv"] == "P-256"

    repository.set_device(
        {
            "deviceId": "old-device",
            "pairingId": "old-pairing",
            "origin": "https://virty.internal/",
        }
    )
    repository.set_lease(
        LeaseCredential(
            "old-token",
            "old-lease",
            "2099-08-22T01:00:00Z",
            1,
            "https://virty.internal/",
            "old-device",
        )
    )
    status = client.get_pairing()
    assert status["status"] == "active"
    assert repository.get_device()["deviceId"] == "device-1"
    assert repository.get_device()["origin"] == "https://virty.internal/"
    assert repository.get_pairing() is None
    assert repository.get_lease() is None
    assert transport.requests[1]["headers"]["X-Pairing-Code"] == "ABCD-EFGH"


def test_lease_is_approved_in_web_ui_then_exchanged_without_webauthn_in_helper() -> None:
    transport = FakeTransport(
        (
            202,
            {
                "kind": "pending",
                "requestId": "lease-request-1",
                "status": "pending",
                "expiresAt": "2026-08-22T01:00:00Z",
            },
        ),
        (
            200,
            {
                "requestId": "lease-request-1",
                "deviceId": "device-1",
                "status": "pending",
                "expiresAt": "2026-08-22T01:00:00Z",
            },
        ),
        (
            200,
            {
                "requestId": "lease-request-1",
                "deviceId": "device-1",
                "status": "approved",
                "expiresAt": "2026-08-22T01:00:00Z",
            },
        ),
        (
            200,
            {
                "kind": "lease",
                "accessToken": "secret-lease-token",
                "tokenType": "DPoP",
                "expiresAt": "2026-08-22T01:30:00Z",
                "leaseId": "lease-1",
                "maxMutations": 20,
            },
        ),
    )
    client, repository = _client(transport)
    _paired_repository(repository)

    pending = client.begin_lease(
        principal_id="admin",
        requested_scopes=["vm.get", "vm.power.update"],
        project_ids=["project-1"],
        node_ids=["node-1"],
        max_mutations=20,
        allow_destructive=True,
        allow_delete_without_recovery=False,
        allow_network_change_without_oob=False,
    )
    assert pending["kind"] == "pending"
    assert "webauthnAssertion" not in transport.requests[0]["body"]
    assert transport.requests[0]["headers"]["DPoP"]

    assert client.get_lease_status()["status"] == "pending"
    issued = client.get_lease_status()
    assert issued["status"] == "active"
    assert issued["lease"]["accessToken"] == "[REDACTED]"
    assert repository.get_lease() == LeaseCredential(
        access_token="secret-lease-token",
        lease_id="lease-1",
        expires_at="2026-08-22T01:30:00Z",
        max_mutations=20,
        origin="https://virty.internal/",
        device_id="device-1",
    )
    assert transport.requests[3]["url"].endswith("/leases/lease-request-1/exchange")


def test_action_uses_dpop_authorization_ath_and_exact_envelope() -> None:
    transport = FakeTransport(
        (
            202,
            {
                "operationId": "operation-1",
                "taskIds": ["operation-1"],
                "status": "queued",
                "risk": "R2",
                "leaseId": "lease-1",
                "correlationId": "correlation-1",
            },
        )
    )
    client, repository = _client(transport)
    _paired_repository(repository)
    repository.set_lease(
        LeaseCredential(
            access_token="lease-token",
            lease_id="lease-1",
            expires_at="2099-08-22T01:30:00Z",
            max_mutations=20,
            origin="https://virty.internal/",
            device_id="device-1",
        )
    )

    client.call_action(
        action="vm.power.update",
        action_input={"uuid": "vm-1", "status": "off"},
        target={"resourceType": "vm", "resourceId": "vm-1"},
        idempotency_key="retry-key-1",
        expected_generation="generation-token-1",
    )
    request = transport.requests[0]
    assert request["headers"]["Authorization"] == "DPoP lease-token"
    payload = _decode_segment(request["headers"]["DPoP"].split(".")[1])
    assert payload["ath"]
    assert payload["htm"] == "POST"
    assert request["body"] == {
        "expectedGeneration": "generation-token-1",
        "idempotencyKey": "retry-key-1",
        "input": {"status": "off", "uuid": "vm-1"},
        "target": {"resourceId": "vm-1", "resourceType": "vm"},
    }


def test_cancel_operation_path_matches_agent_router_contract() -> None:
    transport = FakeTransport(
        (200, {"operationId": "operation-1", "status": "cancel_requested"})
    )
    client, repository = _client(transport)
    _paired_repository(repository)
    repository.set_lease(
        LeaseCredential(
            "lease-token",
            "lease-1",
            "2099-08-22T01:00:00Z",
            1,
            "https://virty.internal/",
            "device-1",
        )
    )
    client.cancel_operation("operation-1")
    assert transport.requests[0]["method"] == "POST"
    assert transport.requests[0]["url"] == (
        "https://virty.internal/api/agent/v1/operations/operation-1"
    )

    router_path = Path(__file__).resolve().parents[2] / "api/agent/router.py"
    tree = ast.parse(router_path.read_text(encoding="utf-8"), filename=str(router_path))
    routes = {
        (
            decorator.func.attr.upper(),
            decorator.args[0].value,
            node.name,
        )
        for node in tree.body
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
        for decorator in node.decorator_list
        if isinstance(decorator, ast.Call)
        and isinstance(decorator.func, ast.Attribute)
        and isinstance(decorator.func.value, ast.Name)
        and decorator.func.value.id == "app"
        and decorator.func.attr.upper() in {"GET", "POST"}
        and decorator.args
        and isinstance(decorator.args[0], ast.Constant)
        and isinstance(decorator.args[0].value, str)
    }
    assert ("GET", "/operations/{operation_id}", "operation_status") in routes
    assert ("POST", "/operations/{operation_id}", "cancel_operation") in routes
    assert ("POST", "/operations/{operation_id}/cancel", "cancel_operation") not in routes


def test_http_error_is_typed_and_does_not_include_request_token() -> None:
    transport = FakeTransport((403, {"code": "policy_denied", "detail": "scope denied"}))
    client, repository = _client(transport)
    _paired_repository(repository)
    repository.set_lease(
        LeaseCredential(
            "request-secret",
            "lease-1",
            "2099-08-22T01:00:00Z",
            1,
            "https://virty.internal/",
            "device-1",
        )
    )
    try:
        client.get_operation("operation-1")
    except AgentApiError as exc:
        assert exc.status == 403
        assert exc.code == "policy_denied"
        assert "request-secret" not in str(exc)
    else:
        raise AssertionError("AgentApiError was not raised")


def test_nested_agent_error_envelope_is_typed_and_redacted() -> None:
    transport = FakeTransport(
        (
            403,
            {
                "detail": {
                    "code": "scope_denied",
                    "message": "denied token=request-secret",
                }
            },
        )
    )
    client, repository = _client(transport)
    _paired_repository(repository)
    repository.set_lease(
        LeaseCredential(
            "request-secret",
            "lease-1",
            "2099-08-22T01:00:00Z",
            1,
            "https://virty.internal/",
            "device-1",
        )
    )
    try:
        client.get_operation("operation-1")
    except AgentApiError as exc:
        assert exc.status == 403
        assert exc.code == "scope_denied"
        assert str(exc) == "denied token=[REDACTED]"
    else:
        raise AssertionError("AgentApiError was not raised")


def test_http_error_never_echoes_write_only_action_input() -> None:
    secret = "Aa1!" + ("write-only-value" * 100)
    transport = FakeTransport(
        (422, {"code": "invalid_input", "detail": f"invalid value: {secret}"})
    )
    client, repository = _client(transport)
    _paired_repository(repository)
    repository.set_lease(
        LeaseCredential(
            "lease-token",
            "lease-1",
            "2099-08-22T01:00:00Z",
            1,
            "https://virty.internal/",
            "device-1",
        )
    )
    try:
        client.call_action(
            action="user.create",
            action_input={"username": "alice", "password": secret},
            target={"resourceType": "user", "resourceId": "alice"},
            idempotency_key="stable-key-1",
            expected_generation="0",
            secret_values=(secret,),
        )
    except AgentApiError as exc:
        assert secret not in str(exc)
        assert "write-only-value" not in str(exc)
        assert "[REDACTED]" in str(exc)
    else:
        raise AssertionError("AgentApiError was not raised")


def test_lease_token_is_never_sent_after_configured_origin_changes() -> None:
    transport = FakeTransport((200, {"operationId": "operation-1"}))
    repository = ProfileRepository(MemoryCredentialStore())
    _paired_repository(repository)
    repository.set_lease(
        LeaseCredential(
            "bound-token",
            "lease-1",
            "2099-08-22T01:00:00Z",
            1,
            "https://virty.internal/",
            "device-1",
        )
    )
    client = AgentApiClient(
        config=AgentApiConfig(base_url="https://other.internal"),
        repository=repository,
        transport=transport,
    )
    try:
        client.get_operation("operation-1")
    except AgentApiError as exc:
        assert "origin" in str(exc)
    else:
        raise AssertionError("credential origin mismatch must fail closed")
    assert transport.requests == []


def test_lease_is_bound_to_current_origin_and_device_before_token_is_sent() -> None:
    transport = FakeTransport((200, {"operationId": "operation-1"}))
    client, repository = _client(transport)
    _paired_repository(repository)
    repository.set_lease(
        LeaseCredential(
            "bound-token",
            "lease-1",
            "2099-08-22T01:00:00Z",
            1,
            "https://different.internal/",
            "device-1",
        )
    )
    try:
        client.get_operation("operation-1")
    except AgentApiError as exc:
        assert "origin/device" in str(exc)
    else:
        raise AssertionError("lease origin mismatch must fail closed")
    assert transport.requests == []


def test_expired_lease_and_path_segment_injection_are_rejected_locally() -> None:
    transport = FakeTransport((200, {"operationId": "operation-1"}))
    client, repository = _client(transport)
    _paired_repository(repository)
    repository.set_lease(
        LeaseCredential(
            "expired-token",
            "lease-1",
            "2000-01-01T00:00:00Z",
            1,
            "https://virty.internal/",
            "device-1",
        )
    )
    try:
        client.get_operation("operation-1")
    except AgentApiError as exc:
        assert "有効期限" in str(exc)
    else:
        raise AssertionError("expired lease must fail closed")

    try:
        client.get_operation("../leases")
    except AgentApiError as exc:
        assert "path ID" in str(exc)
    else:
        raise AssertionError("path segment injection must fail closed")
    assert transport.requests == []


def test_plain_http_is_rejected_except_explicit_loopback_test_mode() -> None:
    try:
        AgentApiConfig(base_url="http://virty.internal")
    except ValueError:
        pass
    else:
        raise AssertionError("plain HTTP must be rejected")

    config = AgentApiConfig(
        base_url="http://127.0.0.1:8000", allow_insecure_loopback=True
    )
    assert config.base_url == "http://127.0.0.1:8000"


def test_base_url_rejects_path_credentials_and_invalid_port() -> None:
    for url in (
        "https://virty.internal/api",
        "https://user:secret@virty.internal",
        "https://virty.internal:invalid",
    ):
        try:
            AgentApiConfig(base_url=url)
        except ValueError:
            pass
        else:
            raise AssertionError(f"non-origin URL must be rejected: {url}")


def test_recursive_secret_redaction_handles_camel_and_snake_case() -> None:
    assert redact_secrets(
        {
            "accessToken": "a",
            "nested": {"vnc_password": "b", "privateKey": "c", "safe": 1},
        }
    ) == {
        "accessToken": "[REDACTED]",
        "nested": {"vnc_password": "[REDACTED]", "privateKey": "[REDACTED]", "safe": 1},
    }


def test_secret_redaction_sanitizes_raw_xml_and_private_key_text() -> None:
    result = redact_secrets(
        {
            "xml": "<graphics type='vnc' passwd='vnc-secret'/>",
            "log": (
                "generated -----BEGIN OPENSSH PRIVATE KEY-----\nsecret\n"
                "-----END OPENSSH PRIVATE KEY----- done"
            ),
        }
    )
    assert result["xml"] == "<graphics type='vnc' passwd='[REDACTED]'/>"
    assert "secret" not in result["log"]
    assert result["log"] == "generated [REDACTED] done"


def test_short_and_overlapping_write_only_values_are_fully_redacted() -> None:
    result = redact_secrets(
        "payload=E and secret-long then secret",
        secret_values=("E", "secret", "secret-long"),
    )
    assert result == "payload=[REDACTED] and [REDACTED] then [REDACTED]"
