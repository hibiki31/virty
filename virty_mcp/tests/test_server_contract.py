from __future__ import annotations

import io
import json
from typing import Any

from jsonschema import Draft202012Validator

from virty_mcp.client import AgentApiError
from virty_mcp.credentials import LeaseCredential, MemoryCredentialStore, ProfileRepository
from virty_mcp.server import PROTOCOL_VERSION, SERVER_INSTRUCTIONS, TASK_EXTENSION, VirtyMcpServer


class FakeAgentClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.operation: dict[str, Any] = {
            "operationId": "operation-1",
            "action": "vm.power.update",
            "status": "succeeded",
            "createdAt": "2026-08-22T00:00:00Z",
            "updatedAt": "2026-08-22T00:00:01Z",
            "result": {"ok": True},
        }

    def call_action(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("call_action", kwargs))
        if kwargs["action"] == "vm.get":
            return {
                "uuid": kwargs["action_input"]["uuid"],
                "vncPassword": "never-return-this",
                "nested": {"access_token": "never-return-this-either"},
            }
        if kwargs["action"] == "user.create":
            return {
                "username": kwargs["action_input"]["username"],
                "log": f"submitted={kwargs['action_input']['password']}",
            }
        if kwargs["action"] == "vm.create":
            user_data = kwargs["action_input"]["cloudInit"]["userData"]
            self.operation["action"] = "vm.create"
            return {
                "operationId": "operation-1",
                "taskIds": ["operation-1"],
                "status": "queued",
                "risk": "R2",
                "leaseId": "lease-1",
                "correlationId": "correlation-1",
                "log": f"cloud-init payload={user_data}",
            }
        return {
            "operationId": "operation-1",
            "taskIds": ["operation-1"],
            "status": "queued",
            "risk": "R2",
            "leaseId": "lease-1",
            "correlationId": "correlation-1",
        }

    def create_pairing(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("create_pairing", kwargs))
        return {
            "pairingId": "pair-1",
            "pairingCode": "ABCD-EFGH",
            "status": "pending",
            "expiresAt": "2026-08-22T01:00:00Z",
        }

    def get_pairing(self) -> dict[str, Any]:
        return {"pairingId": "pair-1", "status": "pending", "expiresAt": "soon"}

    def begin_lease(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("begin_lease", kwargs))
        return {"kind": "pending", "requestId": "request-1", "status": "pending"}

    def get_lease_status(self) -> dict[str, Any]:
        return {"requestId": "request-1", "status": "pending"}

    def session_status(self) -> dict[str, Any]:
        return {"paired": True, "lease": None}

    def get_operation(self, operation_id: str) -> dict[str, Any]:
        self.calls.append(("get_operation", {"operationId": operation_id}))
        return self.operation

    def cancel_operation(self, operation_id: str) -> dict[str, Any]:
        self.calls.append(("cancel_operation", {"operationId": operation_id}))
        return {"operationId": operation_id, "status": "cancel_requested"}


def _server() -> tuple[VirtyMcpServer, FakeAgentClient]:
    client = FakeAgentClient()
    repository = ProfileRepository(MemoryCredentialStore())
    return VirtyMcpServer(client=client, repository=repository), client  # type: ignore[arg-type]


def _retained_server_state(server: VirtyMcpServer) -> dict[str, Any]:
    """Fake clientのcall記録を除き、helper自身の長期stateだけを返す。"""

    return {
        name: value
        for name, value in vars(server).items()
        if name != "client"
    }


def _request(method: str, params: dict[str, Any], request_id: int = 1) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}


def _meta(*, tasks: bool = False) -> dict[str, Any]:
    extensions = {TASK_EXTENSION: {}} if tasks else {}
    return {
        "io.modelcontextprotocol/protocolVersion": PROTOCOL_VERSION,
        "io.modelcontextprotocol/clientInfo": {"name": "contract-test", "version": "1"},
        "io.modelcontextprotocol/clientCapabilities": {"extensions": extensions},
    }


def test_discover_advertises_2026_tools_tasks_and_security_instructions() -> None:
    server, _ = _server()
    response = server.handle_message(_request("server/discover", {"_meta": _meta()}))
    result = response["result"]
    assert result["supportedVersions"][0] == PROTOCOL_VERSION
    assert TASK_EXTENSION in result["capabilities"]["extensions"]
    assert result["instructions"] == SERVER_INSTRUCTIONS
    assert "任意HTTP proxy" in result["instructions"]


def test_legacy_initialize_is_supported_for_current_codex_hosts() -> None:
    server, _ = _server()
    response = server.handle_message(
        _request(
            "initialize",
            {
                "protocolVersion": "2025-11-25",
                "capabilities": {},
                "clientInfo": {"name": "codex", "version": "1"},
            },
        )
    )
    assert response["result"]["protocolVersion"] == "2025-11-25"
    assert response["result"]["capabilities"]["tools"] == {"listChanged": False}
    assert "experimental" not in response["result"]["capabilities"]


def test_codex_legacy_session_accepts_standard_meta_and_falls_back_without_tasks() -> None:
    server, _ = _server()
    initialized = server.handle_message(
        _request(
            "initialize",
            {
                "protocolVersion": "2025-11-25",
                "capabilities": {},
                "clientInfo": {"name": "codex", "version": "1"},
            },
        )
    )
    assert initialized["result"]["protocolVersion"] == "2025-11-25"

    listed = server.handle_message(
        _request("tools/list", {"_meta": {"progressToken": "codex-progress-1"}}, 2)
    )
    assert "error" not in listed

    called = server.handle_message(
        _request(
            "tools/call",
            {
                "_meta": {"progressToken": "codex-progress-2", "codex/unknown": True},
                "name": "virty.vm.power.update",
                "arguments": {
                    "uuid": "vm-1",
                    "status": "off",
                    "idempotencyKey": "stable-key-codex",
                    "expectedGeneration": "generation-1",
                },
            },
            3,
        )
    )
    assert called["result"]["resultType"] == "complete"


def test_2026_initialize_negotiates_tasks_for_later_requests_without_custom_meta() -> None:
    server, _ = _server()
    initialized = server.handle_message(
        _request(
            "initialize",
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"extensions": {TASK_EXTENSION: {}}},
                "clientInfo": {"name": "contract-test", "version": "1"},
            },
        )
    )
    assert initialized["result"]["protocolVersion"] == PROTOCOL_VERSION

    called = server.handle_message(
        _request(
            "tools/call",
            {
                "_meta": {"progressToken": "task-progress-1"},
                "name": "virty.vm.power.update",
                "arguments": {
                    "uuid": "vm-1",
                    "status": "off",
                    "idempotencyKey": "stable-key-2026",
                    "expectedGeneration": "generation-1",
                },
            },
            2,
        )
    )
    assert called["result"]["resultType"] == "task"

    polled = server.handle_message(
        _request("tasks/get", {"taskId": "operation-1", "_meta": {"progressToken": 3}}, 3)
    )
    assert polled["result"]["status"] == "completed"


def test_tasks_methods_reject_session_that_did_not_negotiate_extension() -> None:
    server, _ = _server()
    server.handle_message(
        _request(
            "initialize",
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "contract-test", "version": "1"},
            },
        )
    )
    response = server.handle_message(
        _request(
            "tasks/get",
            {
                "taskId": "operation-1",
                "_meta": {
                    "io.modelcontextprotocol/protocolVersion": PROTOCOL_VERSION,
                    "io.modelcontextprotocol/clientCapabilities": {
                        "extensions": {TASK_EXTENSION: {}}
                    },
                },
            },
            2,
        )
    )
    assert response["error"]["code"] == -32003


def test_tools_list_is_deterministic_strict_and_excludes_sensitive_plumbing() -> None:
    server, _ = _server()
    response = server.handle_message(_request("tools/list", {"_meta": _meta()}))
    result = response["result"]
    tools = result["tools"]
    names = [tool["name"] for tool in tools]
    assert names == sorted(names)
    assert len(names) == 70
    assert "virty.device.pair" in names
    assert "virty.lease.begin" in names
    assert "virty.operation.cancel" in names
    assert all(tool["inputSchema"]["additionalProperties"] is False for tool in tools)
    assert all("outputSchema" in tool for tool in tools)
    serialized = json.dumps(tools).lower()
    assert "console-ticket" not in serialized
    assert "/vnc/" not in serialized
    assert "/api/auth" not in serialized


def test_read_action_returns_structured_content_and_redacts_secrets() -> None:
    server, client = _server()
    response = server.handle_message(
        _request(
            "tools/call",
            {"_meta": _meta(), "name": "virty.vm.get", "arguments": {"uuid": "vm-1"}},
        )
    )
    result = response["result"]
    assert result["resultType"] == "complete"
    assert result["structuredContent"] == {
        "action": "vm.get",
        "data": {
            "uuid": "vm-1",
            "vncPassword": "[REDACTED]",
            "nested": {"access_token": "[REDACTED]"},
        },
    }
    assert "never-return-this" not in result["content"][0]["text"]
    assert client.calls[0][1]["target"] == {"resourceType": "vm", "resourceId": "vm-1"}


def test_mutation_requires_string_generation_and_returns_task_when_client_opts_in() -> None:
    server, client = _server()
    arguments = {
        "uuid": "vm-1",
        "status": "off",
        "idempotencyKey": "stable-key-1",
        "expectedGeneration": "update-token-7",
    }
    response = server.handle_message(
        _request(
            "tools/call",
            {
                "_meta": _meta(tasks=True),
                "name": "virty.vm.power.update",
                "arguments": arguments,
            },
        )
    )
    result = response["result"]
    assert result["resultType"] == "task"
    assert result["taskId"] == "operation-1"
    call = client.calls[0][1]
    assert call["expected_generation"] == "update-token-7"
    assert call["idempotency_key"] == "stable-key-1"
    assert call["action_input"] == {"uuid": "vm-1", "status": "off"}


def test_mutation_falls_back_to_regular_result_without_tasks_capability() -> None:
    server, _ = _server()
    response = server.handle_message(
        _request(
            "tools/call",
            {
                "_meta": _meta(tasks=False),
                "name": "virty.vm.power.update",
                "arguments": {
                    "uuid": "vm-1",
                    "status": "off",
                    "idempotencyKey": "stable-key-1",
                    "expectedGeneration": "token-1",
                },
            },
        )
    )
    assert response["result"]["resultType"] == "complete"
    assert response["result"]["structuredContent"]["data"]["operationId"] == "operation-1"


def test_already_succeeded_mutation_returns_regular_result_to_tasks_client() -> None:
    server, client = _server()

    def succeeded_action(**kwargs: Any) -> dict[str, Any]:
        return {
            "operationId": "operation-1",
            "taskIds": ["operation-1"],
            "status": "succeeded",
            "risk": "R1",
            "leaseId": "lease-1",
            "correlationId": "correlation-1",
        }

    client.call_action = succeeded_action  # type: ignore[method-assign]
    response = server.handle_message(
        _request(
            "tools/call",
            {
                "_meta": _meta(tasks=True),
                "name": "virty.vm.power.update",
                "arguments": {
                    "uuid": "vm-1",
                    "status": "off",
                    "idempotencyKey": "stable-key-1",
                    "expectedGeneration": "generation-1",
                },
            },
        )
    )
    assert response["result"]["resultType"] == "complete"
    assert response["result"]["structuredContent"]["data"]["status"] == "succeeded"


def test_validation_error_never_echoes_write_only_password() -> None:
    server, _ = _server()
    response = server.handle_message(
        _request(
            "tools/call",
            {
                "_meta": _meta(),
                "name": "virty.user.create",
                "arguments": {
                    "username": "alice",
                    "password": "secret",
                    "idempotencyKey": "stable-key-1",
                    "expectedGeneration": "0",
                },
            },
        )
    )
    result = response["result"]
    assert result["isError"] is True
    assert "secret" not in result["content"][0]["text"]
    assert "minLength" in result["content"][0]["text"]


def test_agent_policy_denial_is_a_tool_error_not_a_jsonrpc_protocol_error() -> None:
    server, client = _server()

    def deny_action(**kwargs: Any) -> dict[str, Any]:
        raise AgentApiError("scope denied", status=403, code="scope_denied")

    client.call_action = deny_action  # type: ignore[method-assign]
    response = server.handle_message(
        _request(
            "tools/call",
            {"_meta": _meta(), "name": "virty.vm.get", "arguments": {"uuid": "vm-1"}},
        )
    )
    assert "error" not in response
    assert response["result"]["isError"] is True
    assert "scope_denied" in response["result"]["content"][0]["text"]


def test_success_response_redacts_write_only_value_embedded_in_free_text() -> None:
    server, _ = _server()
    password = "Aa1!secret-value"
    response = server.handle_message(
        _request(
            "tools/call",
            {
                "_meta": _meta(),
                "name": "virty.user.create",
                "arguments": {
                    "username": "alice",
                    "password": password,
                    "idempotencyKey": "stable-key-1",
                    "expectedGeneration": "0",
                },
            },
        )
    )
    serialized = json.dumps(response, ensure_ascii=False)
    assert password not in serialized
    assert "submitted=[REDACTED]" in serialized


def test_nested_cloud_init_write_only_value_is_redacted_from_free_text() -> None:
    server, _ = _server()
    user_data = "#cloud-config\nruncmd: ['use VM-Credential-Aa1!']"
    response = server.handle_message(
        _request(
            "tools/call",
            {
                "_meta": _meta(),
                "name": "virty.vm.create",
                "arguments": {
                    "type": "manual",
                    "name": "vm-1",
                    "nodeName": "node-1",
                    "projectId": "project-1",
                    "memoryMegaByte": 1024,
                    "cpu": 1,
                    "disks": [],
                    "interface": [],
                    "cloudInit": {"hostname": "vm-1", "userData": user_data},
                    "idempotencyKey": "stable-key-vm-create",
                    "expectedGeneration": "0",
                },
            },
        )
    )
    serialized = json.dumps(response, ensure_ascii=False)
    assert user_data not in serialized
    assert "cloud-init payload=[REDACTED]" in serialized
    # write-only入力は即時応答のredact後にserver stateへ保持しない。
    assert user_data not in repr(_retained_server_state(server))
    assert not hasattr(server, "_operation_secrets")


def test_terminal_operation_does_not_retain_write_only_input() -> None:
    server, client = _server()
    password = "Aa1!terminal-secret-value"

    def queued_user_create(**_: Any) -> dict[str, Any]:
        return {
            "operationId": "operation-1",
            "taskIds": ["operation-1"],
            "status": "queued",
            "risk": "R3",
            "leaseId": "lease-1",
            "correlationId": "correlation-1",
        }

    client.call_action = queued_user_create  # type: ignore[method-assign]
    response = server.handle_message(
        _request(
            "tools/call",
            {
                "_meta": _meta(tasks=True),
                "name": "virty.user.create",
                "arguments": {
                    "username": "alice",
                    "password": password,
                    "idempotencyKey": "stable-key-terminal-secret",
                    "expectedGeneration": "0",
                },
            },
        )
    )
    assert password not in json.dumps(response, ensure_ascii=False)
    assert password not in repr(_retained_server_state(server))
    assert not hasattr(server, "_operation_secrets")

    client.operation.update({
        "action": "user.create",
        "status": "succeeded",
        "message": "Agent direct operationが完了しました",
    })
    terminal = server.handle_message(
        _request("tasks/get", {"_meta": _meta(tasks=True), "taskId": "operation-1"}, 2)
    )
    assert terminal["result"]["status"] == "completed"
    assert password not in json.dumps(terminal, ensure_ascii=False)
    assert password not in repr(_retained_server_state(server))


def test_operation_log_redacts_active_lease_token_embedded_in_free_text() -> None:
    server, client = _server()
    token = "known-active-lease-token"
    server.repository.set_lease(
        LeaseCredential(
            token,
            "lease-1",
            "2099-08-22T01:30:00Z",
            20,
            "https://virty.internal/",
            "device-1",
        )
    )
    client.operation["message"] = f"accidental credential: {token}"
    response = server.handle_message(
        _request("tasks/get", {"_meta": _meta(tasks=True), "taskId": "operation-1"})
    )
    serialized = json.dumps(response, ensure_ascii=False)
    assert token not in serialized
    assert "accidental credential: [REDACTED]" in serialized


def test_tasks_get_and_cancel_bridge_to_durable_operations() -> None:
    server, client = _server()
    get_response = server.handle_message(
        _request("tasks/get", {"_meta": _meta(tasks=True), "taskId": "operation-1"})
    )
    task = get_response["result"]
    assert task["resultType"] == "complete"
    assert task["status"] == "completed"
    assert task["result"]["structuredContent"]["data"]["result"] == {"ok": True}
    power_tool = next(
        tool for tool in server.catalog.tools() if tool["name"] == "virty.vm.power.update"
    )
    Draft202012Validator(power_tool["outputSchema"]).validate(
        task["result"]["structuredContent"]
    )

    cancel_response = server.handle_message(
        _request("tasks/cancel", {"_meta": _meta(tasks=True), "taskId": "operation-1"}, 2)
    )
    assert cancel_response["result"] == {"resultType": "complete"}
    assert client.calls[-1] == ("cancel_operation", {"operationId": "operation-1"})


def test_task_creation_timestamp_is_stable_without_backend_timestamp() -> None:
    server, client = _server()
    server.repository.set_lease(
        LeaseCredential(
            "lease-token",
            "lease-1",
            "2099-08-22T01:30:00Z",
            20,
            "https://virty.internal/",
            "device-1",
        )
    )
    created = server.handle_message(
        _request(
            "tools/call",
            {
                "_meta": _meta(tasks=True),
                "name": "virty.vm.power.update",
                "arguments": {
                    "uuid": "vm-1",
                    "status": "off",
                    "idempotencyKey": "stable-key-1",
                    "expectedGeneration": "generation-1",
                },
            },
        )
    )["result"]
    client.operation.pop("createdAt")
    client.operation.pop("updatedAt")
    polled = server.handle_message(
        _request("tasks/get", {"_meta": _meta(tasks=True), "taskId": "operation-1"}, 2)
    )["result"]
    assert polled["createdAt"] == created["createdAt"]
    assert polled["ttlMs"] == created["ttlMs"]


def test_tasks_update_acknowledges_unknown_inputs_only_for_negotiated_extension() -> None:
    server, client = _server()
    response = server.handle_message(
        _request(
            "tasks/update",
            {
                "_meta": _meta(tasks=True),
                "taskId": "operation-1",
                "inputResponses": {"unused": {"resultType": "decline"}},
            },
        )
    )
    assert response["result"] == {"resultType": "complete"}
    assert client.calls[-1] == ("get_operation", {"operationId": "operation-1"})

    missing_capability = server.handle_message(
        _request("tasks/get", {"_meta": _meta(), "taskId": "operation-1"}, 2)
    )
    assert missing_capability["error"]["code"] == -32003


def test_pairing_tool_tells_operator_to_use_virty_web_ui() -> None:
    server, _ = _server()
    response = server.handle_message(
        _request(
            "tools/call",
            {
                "_meta": _meta(),
                "name": "virty.device.pair",
                "arguments": {"deviceName": "ops-laptop", "requestedScopes": ["vm.get"]},
            },
        )
    )
    structured = response["result"]["structuredContent"]
    assert structured["data"]["pairingCode"] == "ABCD-EFGH"
    assert "Virty Web UI" in structured["data"]["nextStep"]


def test_unknown_protocol_metadata_is_ignored_and_unknown_tool_is_a_protocol_error() -> None:
    server, _ = _server()
    unsupported_metadata = server.handle_message(
        _request(
            "tools/list",
            {
                "_meta": {
                    "io.modelcontextprotocol/protocolVersion": "1900-01-01",
                    "io.modelcontextprotocol/clientCapabilities": {},
                }
            },
        )
    )
    assert "error" not in unsupported_metadata

    missing_custom_client_info = server.handle_message(
        _request(
            "tools/list",
            {
                "_meta": {
                    "io.modelcontextprotocol/protocolVersion": PROTOCOL_VERSION,
                    "io.modelcontextprotocol/clientCapabilities": {},
                }
            },
            3,
        )
    )
    assert "error" not in missing_custom_client_info

    invalid_meta_shape = server.handle_message(
        _request("tools/list", {"_meta": ["not", "an", "object"]}, 4)  # type: ignore[dict-item]
    )
    assert invalid_meta_shape["error"]["code"] == -32002

    unknown = server.handle_message(
        _request(
            "tools/call",
            {"_meta": _meta(), "name": "virty.shell", "arguments": {}},
            2,
        )
    )
    assert unknown["error"]["code"] == -32602


def test_stdio_transport_is_newline_delimited_and_does_not_write_logs_to_stdout() -> None:
    server, _ = _server()
    request_one = _request("ping", {"_meta": _meta()}, 1)
    request_two = _request("tools/list", {"_meta": _meta()}, 2)
    stdin = io.BytesIO(
        (json.dumps(request_one) + "\n" + json.dumps(request_two) + "\n").encode()
    )
    stdout = io.StringIO()
    server.run_stdio(stdin=stdin, stdout=stdout)
    lines = stdout.getvalue().splitlines()
    assert len(lines) == 2
    assert [json.loads(line)["id"] for line in lines] == [1, 2]
