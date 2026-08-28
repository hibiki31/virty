from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

from virty_mcp.catalog import ActionCatalog

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
API_ROOT = REPOSITORY_ROOT / "api"
sys.path.insert(0, str(REPOSITORY_ROOT))


def _literal_string(node: ast.AST | None, default: str = "") -> str:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return default


def _router_prefix(tree: ast.Module) -> str:
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "app" for target in node.targets):
            continue
        if not isinstance(node.value, ast.Call):
            continue
        for keyword in node.value.keywords:
            if keyword.arg == "prefix":
                return _literal_string(keyword.value)
    return ""


def _routes(path: Path) -> set[tuple[str, str, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    prefix = _router_prefix(tree)
    routes: set[tuple[str, str, str]] = set()
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call) or not isinstance(decorator.func, ast.Attribute):
                continue
            if not isinstance(decorator.func.value, ast.Name) or decorator.func.value.id != "app":
                continue
            method = decorator.func.attr.upper()
            if method not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
                continue
            suffix = _literal_string(decorator.args[0] if decorator.args else None)
            routes.add((method, prefix + suffix, node.name))
    return routes


def test_catalog_covers_reviewed_management_routes_and_only_excludes_sensitive_routes() -> None:
    files = [
        API_ROOT / area / filename
        for area in (
            "task",
            "node",
            "domain",
            "storage",
            "images",
            "network",
            "user",
            "project",
            "flavor",
            "exporter",
            "mixin",
        )
        for filename in ("router.py", "router_task.py")
        if (API_ROOT / area / filename).exists()
    ]
    implementation_routes = set().union(*(_routes(path) for path in files))
    excluded = {
        ("GET", "/api/vms/vnc/{token}", "get_vnc_address"),
        ("POST", "/api/vms/{uuid}/console-ticket", "create_console_ticket"),
    }
    catalog = ActionCatalog.load_default()
    catalog_routes = {
        (action.source_method, action.source_path, action.operation_id)
        for action in catalog.actions
    }

    assert implementation_routes - excluded == catalog_routes
    assert catalog_routes.isdisjoint(excluded)


def test_auth_setup_and_generic_execution_are_not_exposed() -> None:
    catalog = ActionCatalog.load_default()
    searchable = " ".join(
        f"{action.action} {action.tool_name} {action.source_path}" for action in catalog.actions
    ).lower()
    assert "/api/auth" not in searchable
    assert "/vnc/" not in searchable
    assert all(term not in searchable for term in ("shell", "proxy", "arbitrary-api", "setup"))


def test_all_tool_schemas_are_valid_strict_root_objects() -> None:
    catalog = ActionCatalog.load_default()
    assert len(catalog.actions) == 69
    assert catalog.get_by_action("network.provider.create") is None
    for action in catalog.actions:
        tool = action.as_mcp_tool()
        Draft202012Validator.check_schema(tool["inputSchema"])
        Draft202012Validator.check_schema(tool["outputSchema"])
        assert tool["inputSchema"]["type"] == "object"
        assert tool["inputSchema"]["additionalProperties"] is False
        assert tool["outputSchema"]["additionalProperties"] is False
        annotations = tool["annotations"]
        assert set(annotations) == {
            "title",
            "readOnlyHint",
            "destructiveHint",
            "idempotentHint",
            "openWorldHint",
        }
        if action.mutation:
            assert {"idempotencyKey", "expectedGeneration"} <= set(
                tool["inputSchema"]["required"]
            )
            assert tool["inputSchema"]["properties"]["expectedGeneration"]["type"] == "string"


def test_all_nested_input_objects_are_closed_and_sensitive_cloud_init_is_write_only() -> None:
    def assert_closed_objects(schema: object) -> None:
        if isinstance(schema, dict):
            schema_type = schema.get("type")
            if schema_type == "object" or (
                isinstance(schema_type, list) and "object" in schema_type
            ):
                assert schema.get("additionalProperties") is False
            for child in schema.values():
                assert_closed_objects(child)
        elif isinstance(schema, list):
            for child in schema:
                assert_closed_objects(child)

    catalog = ActionCatalog.load_default()
    for action in catalog.actions:
        assert_closed_objects(action.input_schema)

    vm_create = catalog.get_by_action("vm.create")
    assert vm_create is not None
    user_data = vm_create.input_schema["properties"]["cloudInit"]["properties"]["userData"]
    assert user_data["writeOnly"] is True

    image_download = catalog.get_by_action("image.download")
    assert image_download is not None
    assert image_download.input_schema["properties"]["imageUrl"]["writeOnly"] is True

    grant_candidates = catalog.get_by_action(
        "project.resource-grant-candidates.get",
    )
    assert grant_candidates is not None
    assert grant_candidates.mutation is False
    assert grant_candidates.risk == "R0"
    assert grant_candidates.required == ("projectId",)


def test_catalog_order_and_identifiers_are_deterministic_and_unique() -> None:
    catalog = ActionCatalog.load_default()
    tools = catalog.tools()
    tool_names = [tool["name"] for tool in tools]
    action_names = [action.action for action in catalog.actions]
    assert tool_names == sorted(tool_names)
    assert len(tool_names) == len(set(tool_names))
    assert len(action_names) == len(set(action_names))


def test_helper_catalog_security_metadata_matches_agent_api_source_of_truth() -> None:
    """Server側catalog更新時にhelperへの暗黙公開・risk driftを検出する。"""

    from api.agent.catalog import ACTIONS as SERVER_ACTIONS

    helper = {action.action: action for action in ActionCatalog.load_default().actions}
    assert set(helper) == set(SERVER_ACTIONS)
    for action_id, server_action in SERVER_ACTIONS.items():
        helper_action = helper[action_id]
        assert helper_action.mutation == server_action.mutation, action_id
        assert helper_action.destructive == server_action.destructive, action_id
        assert helper_action.risk == server_action.risk, action_id
        assert helper_action.target.resource_type == server_action.resource_type, action_id


def test_checked_in_helper_catalog_exactly_matches_agent_api_catalog_document() -> None:
    """input schemaを含む公開契約全体のdriftを一byte相当の構造比較で検出する。"""

    from api.agent.catalog import catalog_document

    helper_document = json.loads(
        (REPOSITORY_ROOT / "virty_mcp/src/virty_mcp/action_catalog.json").read_text(
            encoding="utf-8"
        )
    )
    assert helper_document == catalog_document()


def test_agent_operation_response_supports_durable_mcp_task_recovery() -> None:
    """helper再起動後もactionと最終resultをAgent APIから復元できる。"""

    tree = ast.parse(
        (API_ROOT / "agent/schemas.py").read_text(encoding="utf-8"),
        filename=str(API_ROOT / "agent/schemas.py"),
    )
    operation_response = next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "OperationResponse"
    )
    fields = {
        node.target.id
        for node in operation_response.body
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
    }
    assert {"action", "created_at", "updated_at", "result"} <= fields
