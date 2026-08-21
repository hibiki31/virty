"""明示的にreviewされたVirty action catalogのloader。"""

from __future__ import annotations

import json
from collections.abc import Iterable
from copy import deepcopy
from dataclasses import dataclass
from importlib.resources import files
from typing import Any

MUTATION_ENVELOPE_PROPERTIES: dict[str, dict[str, Any]] = {
    "idempotencyKey": {
        "type": "string",
        "minLength": 8,
        "maxLength": 128,
        "pattern": "^[A-Za-z0-9][A-Za-z0-9._:-]*$",
        "description": "Retry時にも変更しない一意なkey。operation確認前に新しいkeyを作らない。",
    },
    "expectedGeneration": {
        "type": "string",
        "minLength": 1,
        "maxLength": 256,
        "description": (
            "直前のreadで取得したresource generation。create、refresh等の"
            "既存target generationがないactionでは文字列0。"
        ),
    },
}

ACTION_OUTPUT_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "action": {"type": "string"},
        "data": {"type": "object"},
    },
    "required": ["action", "data"],
    "additionalProperties": False,
}


@dataclass(frozen=True)
class TargetMapping:
    """tool argumentからAgent APIの認可targetを組み立てる規則。"""

    resource_type: str
    resource_id_field: str | None = None
    project_id_field: str | None = None
    node_id_field: str | None = None

    def resolve(self, arguments: dict[str, Any]) -> dict[str, Any]:
        target: dict[str, Any] = {"resourceType": self.resource_type}
        for target_name, source_name in (
            ("resourceId", self.resource_id_field),
            ("projectId", self.project_id_field),
            ("nodeId", self.node_id_field),
        ):
            if source_name is not None and arguments.get(source_name) is not None:
                target[target_name] = str(arguments[source_name])
        return target


@dataclass(frozen=True)
class ActionDefinition:
    """一つのMCP toolと一つのAgent actionの固定mapping。"""

    action: str
    tool_name: str
    title: str
    description: str
    source_method: str
    source_path: str
    operation_id: str
    mutation: bool
    destructive: bool
    risk: str
    open_world: bool
    parameters: dict[str, Any]
    required: tuple[str, ...]
    target: TargetMapping

    @property
    def input_schema(self) -> dict[str, Any]:
        properties = dict(self.parameters)
        required = list(self.required)
        if self.mutation:
            properties.update(MUTATION_ENVELOPE_PROPERTIES)
            required.extend(MUTATION_ENVELOPE_PROPERTIES)
        return {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False,
        }

    def as_mcp_tool(self) -> dict[str, Any]:
        risk_note = f"Virty risk={self.risk}. "
        output_schema = deepcopy(ACTION_OUTPUT_SCHEMA)
        output_schema["properties"]["action"]["const"] = self.action
        return {
            "name": self.tool_name,
            "title": self.title,
            "description": risk_note + self.description,
            "inputSchema": self.input_schema,
            "outputSchema": output_schema,
            "annotations": {
                "title": self.title,
                "readOnlyHint": not self.mutation,
                "destructiveHint": self.destructive,
                "idempotentHint": True,
                "openWorldHint": self.open_world,
            },
            "_meta": {
                "jp.virty/action": self.action,
                "jp.virty/risk": self.risk,
                "jp.virty/sourceOperationId": self.operation_id,
            },
        }

    def split_arguments(
        self, arguments: dict[str, Any]
    ) -> tuple[dict[str, Any], dict[str, Any], str | None, str | None]:
        action_input = {
            name: value
            for name, value in arguments.items()
            if name not in MUTATION_ENVELOPE_PROPERTIES
        }
        return (
            action_input,
            self.target.resolve(action_input),
            arguments.get("idempotencyKey"),
            arguments.get("expectedGeneration"),
        )


class ActionCatalog:
    """重複や暗黙公開を拒否するimmutable catalog。"""

    def __init__(self, actions: Iterable[ActionDefinition]) -> None:
        ordered = tuple(actions)
        self._by_tool = {action.tool_name: action for action in ordered}
        self._by_action = {action.action: action for action in ordered}
        if len(self._by_tool) != len(ordered):
            raise ValueError("action catalogに重複したtool名があります")
        if len(self._by_action) != len(ordered):
            raise ValueError("action catalogに重複したaction IDがあります")
        self.actions = tuple(sorted(ordered, key=lambda item: item.tool_name))

    @classmethod
    def load_default(cls) -> ActionCatalog:
        resource = files("virty_mcp").joinpath("action_catalog.json")
        raw = json.loads(resource.read_text(encoding="utf-8"))
        if raw.get("catalogVersion") != 1 or not isinstance(raw.get("actions"), list):
            raise ValueError("未対応のaction catalog形式です")
        parameter_sets = raw.get("parameterSets", {})
        actions: list[ActionDefinition] = []
        for item in raw["actions"]:
            target = item["target"]
            source = item["source"]
            parameter_set = parameter_sets.get(item.get("parameterSet"), {})
            parameters = deepcopy(parameter_set.get("parameters", {}))
            parameters.update(deepcopy(item.get("parameters", {})))
            required = [*parameter_set.get("required", []), *item.get("required", [])]
            actions.append(
                ActionDefinition(
                    action=item["action"],
                    tool_name=item["toolName"],
                    title=item["title"],
                    description=item["description"],
                    source_method=source["method"],
                    source_path=source["path"],
                    operation_id=source["operationId"],
                    mutation=item["mutation"],
                    destructive=item["destructive"],
                    risk=item["risk"],
                    open_world=item.get("openWorld", False),
                    parameters=parameters,
                    required=tuple(dict.fromkeys(required)),
                    target=TargetMapping(
                        resource_type=target["resourceType"],
                        resource_id_field=target.get("resourceIdField"),
                        project_id_field=target.get("projectIdField"),
                        node_id_field=target.get("nodeIdField"),
                    ),
                )
            )
        return cls(actions)

    def get_by_tool(self, tool_name: str) -> ActionDefinition | None:
        return self._by_tool.get(tool_name)

    def get_by_action(self, action: str) -> ActionDefinition | None:
        return self._by_action.get(action)

    def tools(self) -> list[dict[str, Any]]:
        return [action.as_mcp_tool() for action in self.actions]
