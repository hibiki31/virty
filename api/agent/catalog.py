"""Agentへ公開するactionの明示catalog。

既存OpenAPIへ自動追従させず、この一覧へreview済みactionを追加した場合だけ公開する。
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from .exceptions import NotFoundError

Risk = Literal["R0", "R1", "R2", "R3"]
ActionKind = Literal["read", "task", "direct"]


@dataclass(frozen=True)
class ActionDefinition:
    action_id: str
    title: str
    kind: ActionKind
    resource_type: str
    risk: Risk
    mutation: bool
    adapter: str
    input_model: str | None = None
    task_selector: tuple[str, str, str] | None = None
    requires_generation: bool = False
    destructive: bool = False
    network_change: bool = False
    secret_input: bool = False

    @property
    def required_scope(self) -> str:
        return self.action_id


def _read(
    action_id: str,
    title: str,
    resource: str,
    adapter: str,
    input_model: str | None = None,
) -> ActionDefinition:
    return ActionDefinition(
        action_id,
        title,
        "read",
        resource,
        "R0",
        False,
        adapter,
        input_model,
    )


def _direct(
    action_id: str,
    title: str,
    resource: str,
    adapter: str,
    input_model: str,
    *,
    risk: Risk = "R2",
    requires_generation: bool = False,
    destructive: bool = False,
    network_change: bool = False,
    secret_input: bool = False,
) -> ActionDefinition:
    return ActionDefinition(
        action_id,
        title,
        "direct",
        resource,
        risk,
        True,
        adapter,
        input_model,
        requires_generation=requires_generation,
        destructive=destructive,
        network_change=network_change,
        secret_input=secret_input,
    )


def _task(
    action_id: str,
    title: str,
    resource: str,
    selector: tuple[str, str, str],
    input_model: str | None = None,
    *,
    adapter: str = "enqueue_task",
    risk: Risk = "R2",
    requires_generation: bool = False,
    destructive: bool = False,
    network_change: bool = False,
) -> ActionDefinition:
    return ActionDefinition(
        action_id,
        title,
        "task",
        resource,
        risk,
        True,
        adapter,
        input_model,
        selector,
        requires_generation,
        destructive,
        network_change,
    )


_ACTIONS = [
    _read("node.list", "ノード一覧", "node", "node_list", "node.schemas.NodeForQuery"),
    _read("node.get", "ノード詳細", "node", "node_get"),
    _read("node.facts", "ノードfacts", "node", "node_facts"),
    _read("node.info", "ノード診断情報", "node", "node_info"),
    _read("node.ssh-public-key.get", "管理SSH公開鍵", "node", "node_ssh_public_key"),
    _direct(
        "node.ssh-key.write",
        "管理SSH鍵投入",
        "node",
        "node_ssh_key_write",
        "node.schemas.SSHKeyPair",
        risk="R3",
        destructive=True,
        secret_input=True,
    ),
    _task(
        "node.create",
        "ノード作成",
        "node",
        ("post", "node", "root"),
        "node.schemas.NodeForCreate",
        network_change=True,
    ),
    _task("node.delete", "ノード削除", "node", ("delete", "node", "root"), risk="R3", requires_generation=True, destructive=True),
    _task("node.role.update", "ノードrole更新", "node", ("patch", "node", "role"), "node.schemas.NodeRoleForUpdate", requires_generation=True, network_change=True),
    _read("vm.list", "VM一覧", "vm", "vm_list", "domain.schemas.DomainForQuery"),
    _read("vm.get", "VM詳細", "vm", "vm_get"),
    _read("vm.xml.get", "VM XML", "vm", "vm_xml"),
    _task("vm.refresh", "VM再検出", "vm", ("put", "vm", "list"), risk="R1"),
    _task(
        "vm.create",
        "VM作成",
        "vm",
        ("post", "vm", "root"),
        "agent.input_models.AgentDomainForCreate",
        network_change=True,
    ),
    _task("vm.delete", "VM削除", "vm", ("delete", "vm", "root"), risk="R3", requires_generation=True, destructive=True),
    _task("vm.power.update", "VM電源変更", "vm", ("patch", "vm", "power"), "domain.schemas.PowerStatusForUpdateDomain", risk="R3", requires_generation=True, destructive=True),
    _task("vm.cdrom.update", "VM CD-ROM変更", "vm", ("patch", "vm", "cdrom"), "domain.schemas.CdromForUpdateDomain", requires_generation=True),
    _task("vm.network.update", "VM network変更", "vm", ("patch", "vm", "network"), "domain.schemas.NetworkForUpdateDomain", risk="R3", requires_generation=True, destructive=True, network_change=True),
    _direct("vm.project.update", "VM project変更", "vm", "vm_project_update", "domain.schemas.DomainProjectForUpdate", risk="R2", requires_generation=True),
    _read("storage.list", "storage一覧", "storage", "storage_list", "storage.schemas.StorageForQuery"),
    _read("storage.get", "storage詳細", "storage", "storage_get"),
    _task("storage.create", "storage作成", "storage", ("post", "storage", "root"), "storage.schemas.StorageForCreate"),
    _task("storage.delete", "storage削除", "storage", ("delete", "storage", "root"), risk="R3", requires_generation=True, destructive=True),
    _direct("storage.metadata.update", "storage metadata更新", "storage", "storage_metadata_update", "storage.schemas.StorageMetadataForUpdate", risk="R1", requires_generation=True),
    _read("storage.pool.list", "storage pool一覧", "storage-pool", "storage_pool_list"),
    _direct("storage.pool.create", "storage pool作成", "storage-pool", "storage_pool_create", "storage.schemas.StoragePoolForCreate", risk="R2"),
    _direct("storage.pool.update", "storage pool更新", "storage-pool", "storage_pool_update", "storage.schemas.StoragePoolForUpdate", risk="R2", requires_generation=True),
    _read("image.list", "image一覧", "image", "image_list", "images.schemas.ImageForQuery"),
    _task("image.delete", "image削除", "image", ("delete", "image", "root"), "agent.input_models.ImageDeleteInput", risk="R3", requires_generation=True, destructive=True),
    _task("image.refresh", "image再検出", "image", ("put", "storage", "list"), risk="R1"),
    _task("image.download", "image download", "image", ("post", "image", "download"), "images.schemas.ImageDownloadForCreate"),
    _direct("image.flavor.update", "image flavor更新", "image", "image_flavor_update", "images.schemas.ImageForUpdateImageFlavor", risk="R1", requires_generation=True),
    _read("network.list", "network一覧", "network", "network_list", "network.schemas.NetworkForQuery"),
    _read("network.get", "network詳細", "network", "network_get"),
    _read("network.xml.get", "network XML", "network", "network_xml"),
    _task("network.refresh", "network再検出", "network", ("put", "network", "list"), risk="R1", network_change=True),
    _task("network.create", "network作成", "network", ("post", "network", "root"), "network.schemas.NetworkForCreate", risk="R3", destructive=True, network_change=True),
    _task("network.delete", "network削除", "network", ("delete", "network", "root"), risk="R3", requires_generation=True, destructive=True, network_change=True),
    _task("network.ovs.create", "OVS portgroup作成", "network", ("post", "network", "ovs"), "network.schemas.NetworkOVSForCreate", risk="R3", requires_generation=True, destructive=True, network_change=True),
    _task("network.ovs.delete", "OVS portgroup削除", "network", ("delete", "network", "ovs"), "agent.input_models.NetworkOvsDeleteInput", risk="R3", requires_generation=True, destructive=True, network_change=True),
    _task("network.provider.create", "provider network作成", "network", ("post", "network", "provider"), "network.schemas.NetworkProviderForCreate", risk="R3", destructive=True, network_change=True),
    _read("network.pool.list", "network pool一覧", "network-pool", "network_pool_list"),
    _direct("network.pool.create", "network pool作成", "network-pool", "network_pool_create", "network.schemas.NetworkPoolForCreate", risk="R2", network_change=True),
    _direct("network.pool.update", "network pool更新", "network-pool", "network_pool_update", "network.schemas.NetworkPoolForUpdate", risk="R2", requires_generation=True, network_change=True),
    _direct("network.pool.delete", "network pool削除", "network-pool", "network_pool_delete", "agent.input_models.NetworkPoolDeleteInput", risk="R3", requires_generation=True, destructive=True, network_change=True),
    _read("project.list", "project一覧", "project", "project_list", "project.schemas.ProjectForQuery"),
    _task("project.create", "project作成", "project", ("post", "project", "root"), "project.schemas.ProjectForCreate"),
    _task("project.delete", "project削除", "project", ("delete", "project", "root"), "agent.input_models.ProjectDeleteInput", risk="R3", requires_generation=True, destructive=True),
    _direct("project.member.add", "project member追加", "project", "project_member_add", "project.schemas.ProjectForUpdate", risk="R2", requires_generation=True),
    _read("user.me", "lease principal情報", "user", "user_me"),
    _read("user.list", "利用者一覧", "user", "user_list", "user.schemas.UserForQuery"),
    _direct("user.create", "利用者作成", "user", "user_create", "user.schemas.UserForCreate", risk="R3", destructive=True, secret_input=True),
    _direct("user.update", "利用者更新", "user", "user_update", "agent.input_models.AgentUserUpdateInput", risk="R3", requires_generation=True, destructive=True, secret_input=True),
    _direct("user.delete", "利用者削除", "user", "user_delete", "agent.input_models.UserDeleteInput", risk="R3", requires_generation=True, destructive=True),
    _read("task.list", "task一覧", "task", "task_list", "task.schemas.TaskForQuery"),
    _read("task.get", "task詳細", "task", "task_get"),
    _read("task.incomplete", "未完了task一覧", "task", "task_incomplete", "task.schemas.TaskIncompleteForQuery"),
    _direct("task.delete-all", "task履歴全削除", "task", "task_delete_all", "agent.input_models.EmptyInput", risk="R3", destructive=True),
    _read("flavor.list", "flavor一覧", "flavor", "flavor_list", "flavor.schemas.FlavorForQuery"),
    _direct("flavor.create", "flavor作成", "flavor", "flavor_create", "flavor.schemas.FlavorForCreate", risk="R1"),
    _direct("flavor.delete", "flavor削除", "flavor", "flavor_delete", "agent.input_models.FlavorDeleteInput", requires_generation=True, destructive=True),
    _read("metrics.get", "集約metrics", "metrics", "metrics_get"),
    _read("system.version", "Virty version", "system", "system_version"),
]

ACTIONS: dict[str, ActionDefinition] = {item.action_id: item for item in _ACTIONS}

# operation root配下でworker実行を許すinventory更新だけを明示する。
# catalog未登録selectorをcorrelationへ混入させてもdispatchさせない。
DEPENDENT_TASK_SELECTORS: dict[
    str,
    tuple[tuple[str, str, str], ...],
] = {
    "node.create": (
        ("patch", "node", "role"),
        ("put", "vm", "list"),
        ("put", "storage", "list"),
        ("put", "network", "list"),
    ),
    "vm.create": (("put", "vm", "list"), ("put", "storage", "list")),
    "vm.delete": (("put", "vm", "list"),),
    "vm.power.update": (("put", "vm", "list"),),
    "vm.cdrom.update": (("put", "vm", "list"),),
    "vm.network.update": (("put", "vm", "list"),),
    "storage.create": (("put", "storage", "list"),),
    "network.create": (("put", "network", "list"),),
    "network.delete": (("put", "network", "list"),),
    "network.ovs.create": (("put", "network", "list"),),
    "network.ovs.delete": (("put", "network", "list"),),
}
if len(ACTIONS) != len(_ACTIONS):  # pragma: no cover - import時の開発者error
    raise RuntimeError("Agent action IDが重複しています")


def get_action(action_id: str) -> ActionDefinition:
    try:
        return ACTIONS[action_id]
    except KeyError as exc:
        raise NotFoundError(
            "action_not_found",
            "許可catalogに存在しないactionです",
        ) from exc


def _load_public_catalog() -> dict[str, Any]:
    path = Path(__file__).with_name("action_catalog.json")
    with path.open(encoding="utf-8") as file:
        document = json.load(file)
    public_actions = {
        item["action"]: item
        for item in document.get("actions", [])
    }
    if set(public_actions) != set(ACTIONS):
        raise RuntimeError("Agent public catalogとdispatcher actionが一致しません")
    for action_id, definition in ACTIONS.items():
        public = public_actions[action_id]
        expected = (
            definition.risk,
            definition.mutation,
            definition.destructive,
            definition.resource_type,
        )
        actual = (
            public.get("risk"),
            public.get("mutation"),
            public.get("destructive"),
            public.get("target", {}).get("resourceType"),
        )
        if expected != actual:
            raise RuntimeError(
                f"Agent public catalog metadataが一致しません: {action_id}: "
                f"expected={expected}, actual={actual}"
            )
    return document


PUBLIC_CATALOG = _load_public_catalog()


def catalog_document() -> dict[str, Any]:
    """MCP helperがmirrorするstrict JSON Schema catalogを返す。"""

    return PUBLIC_CATALOG
