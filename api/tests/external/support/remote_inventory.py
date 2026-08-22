"""external testのAPI結果を別経路SSH/libvirtでexact確認する。"""

from __future__ import annotations

import json
import logging
import re
import shlex
from contextlib import contextmanager
from typing import Iterator, Literal, Protocol
from uuid import UUID
from xml.etree import ElementTree

from module.paramikolib import ParamikoManager, RemoteCommandResult


SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
LIBVIRT_LIST_COMMANDS = {
    "vm": ("virsh list --all --name", "virsh list --all --uuid"),
    "network": ("virsh net-list --all --name", "virsh net-list --all --uuid"),
    "storage": ("virsh pool-list --all --name", "virsh pool-list --all --uuid"),
}
LIBVIRT_UUID_COMMANDS = {
    "vm": "virsh domuuid",
    "network": "virsh net-uuid",
    "storage": "virsh pool-uuid",
}
LIBVIRT_ACTIVE_UUID_COMMANDS = {
    "vm": "virsh list --uuid",
    "network": "virsh net-list --uuid",
    "storage": "virsh pool-list --uuid",
}
LIBVIRT_DESTROY_COMMANDS = {
    "vm": "virsh destroy",
    "network": "virsh net-destroy",
    "storage": "virsh pool-destroy",
}
LIBVIRT_UNDEFINE_COMMANDS = {
    "vm": "virsh undefine",
    "network": "virsh net-undefine",
    "storage": "virsh pool-undefine",
}
LibvirtKind = Literal["vm", "network", "storage"]


class RemoteInventoryError(RuntimeError):
    """selectorやremote出力を含めないpostcondition error。"""


class RemoteCommandManager(Protocol):
    def run_cmd(self, command: str) -> RemoteCommandResult: ...


def logical_libvirt_name(kind: str, raw_name: str) -> str:
    """VMのlibvirt owner/UUID suffixだけを固定区切りで除く。"""

    if kind == "vm":
        return raw_name.partition("@")[0]
    return raw_name


@contextmanager
def muted_paramiko_logging() -> Iterator[None]:
    logger = logging.getLogger("module.paramikolib")
    previous = logger.disabled
    logger.disabled = True
    try:
        yield
    finally:
        logger.disabled = previous


@contextmanager
def remote_inventory_manager(
    *,
    user: str,
    domain: str,
    server_index: int,
) -> Iterator[ParamikoManager]:
    manager = None
    try:
        with muted_paramiko_logging():
            manager = ParamikoManager(
                user=user,
                domain=domain,
                port=22,
                connect_timeout=10,
                operation_timeout=60,
            )
            yield manager
    except RemoteInventoryError:
        raise
    except Exception:
        raise RemoteInventoryError(
            f"remote inventory failed: kind=ssh "
            f"server_index={server_index} count=1"
        ) from None
    finally:
        if manager is not None:
            try:
                with muted_paramiko_logging():
                    manager.close()
            except Exception:
                pass


def _run(
    manager: RemoteCommandManager,
    command: str,
    *,
    kind: str,
    server_index: int,
) -> RemoteCommandResult:
    try:
        with muted_paramiko_logging():
            return manager.run_cmd(command)
    except Exception:
        raise RemoteInventoryError(
            f"remote inventory failed: kind={kind} "
            f"server_index={server_index} count=1"
        ) from None


def assert_libvirt_present(
    manager: RemoteCommandManager,
    *,
    kind: str,
    name: str,
    resource_uuid: str,
    server_index: int,
) -> None:
    list_command = LIBVIRT_LIST_COMMANDS[kind][0]
    raw_names = set(
        _run(
            manager,
            list_command,
            kind=kind,
            server_index=server_index,
        ).stdout.splitlines()
    )
    selectors = [
        raw_name
        for raw_name in raw_names
        if logical_libvirt_name(kind, raw_name) == name
    ]
    if len(selectors) != 1:
        raise RemoteInventoryError(
            f"remote postcondition failed: kind={kind} "
            f"server_index={server_index} count={len(selectors)}"
        )
    actual_uuid = _run(
        manager,
        f"{LIBVIRT_UUID_COMMANDS[kind]} {shlex.quote(selectors[0])}",
        kind=kind,
        server_index=server_index,
    ).stdout.strip()
    if actual_uuid != resource_uuid:
        raise RemoteInventoryError(
            f"remote identity mismatch: kind={kind} "
            f"server_index={server_index} count=1"
        )


def assert_libvirt_absent(
    manager: RemoteCommandManager,
    *,
    kind: str,
    name: str,
    resource_uuid: str | None,
    server_index: int,
) -> None:
    name_command, uuid_command = LIBVIRT_LIST_COMMANDS[kind]
    names = {
        logical_libvirt_name(kind, raw_name)
        for raw_name in _run(
            manager,
            name_command,
            kind=kind,
            server_index=server_index,
        ).stdout.splitlines()
    }
    uuids = set(
        _run(
            manager,
            uuid_command,
            kind=kind,
            server_index=server_index,
        ).stdout.splitlines()
    )
    remains = int(name in names) + int(
        resource_uuid is not None and resource_uuid in uuids
    )
    if remains:
        raise RemoteInventoryError(
            f"remote postcondition failed: kind={kind} "
            f"server_index={server_index} count={remains}"
        )


def _validated_uuid(value: str, *, kind: str, server_index: int) -> str:
    try:
        return str(UUID(value.strip()))
    except (ValueError, AttributeError, TypeError):
        raise RemoteInventoryError(
            f"remote identity invalid: kind={kind} "
            f"server_index={server_index} count=1"
        ) from None


def _resolve_manifest_libvirt_uuid(
    manager: RemoteCommandManager,
    *,
    kind: LibvirtKind,
    name: str,
    expected_uuid: str | None,
    server_index: int,
) -> str | None:
    """manifestのexact name/UUIDだけをremote削除selectorへ解決する。"""

    name_command, uuid_command = LIBVIRT_LIST_COMMANDS[kind]
    raw_names = [
        raw_name
        for raw_name in _run(
            manager,
            name_command,
            kind=kind,
            server_index=server_index,
        ).stdout.splitlines()
        if raw_name
    ]
    exact_selectors = [
        raw_name
        for raw_name in raw_names
        if logical_libvirt_name(kind, raw_name) == name
    ]
    if len(exact_selectors) > 1:
        raise RemoteInventoryError(
            f"remote cleanup identity ambiguous: kind={kind} "
            f"server_index={server_index} count={len(exact_selectors)}"
        )

    normalized_expected = (
        _validated_uuid(expected_uuid, kind=kind, server_index=server_index)
        if expected_uuid is not None
        else None
    )
    known_uuids = {
        value.strip()
        for value in _run(
            manager,
            uuid_command,
            kind=kind,
            server_index=server_index,
        ).stdout.splitlines()
        if value.strip()
    }

    if not exact_selectors:
        if normalized_expected is not None and normalized_expected in known_uuids:
            # created entryはUUIDを最優先する。remote側でrenameされても別資源へ
            # selectorを広げず、manifestに記録済みのUUIDだけを対象にする。
            return normalized_expected
        return None

    actual_uuid = _validated_uuid(
        _run(
            manager,
            f"{LIBVIRT_UUID_COMMANDS[kind]} {shlex.quote(exact_selectors[0])}",
            kind=kind,
            server_index=server_index,
        ).stdout,
        kind=kind,
        server_index=server_index,
    )
    if normalized_expected is not None and actual_uuid != normalized_expected:
        raise RemoteInventoryError(
            f"remote cleanup identity mismatch: kind={kind} "
            f"server_index={server_index} count=1"
        )
    return actual_uuid


def delete_manifest_libvirt_target(
    manager: RemoteCommandManager,
    *,
    kind: LibvirtKind,
    name: str,
    resource_uuid: str | None,
    server_index: int,
) -> str | None:
    """DB未記録の部分作成もmanifest exact allowlist内だけで回収する。"""

    resolved_uuid = _resolve_manifest_libvirt_uuid(
        manager,
        kind=kind,
        name=name,
        expected_uuid=resource_uuid,
        server_index=server_index,
    )
    if resolved_uuid is None:
        assert_libvirt_absent(
            manager,
            kind=kind,
            name=name,
            resource_uuid=resource_uuid,
            server_index=server_index,
        )
        return None

    active_uuids = {
        value.strip()
        for value in _run(
            manager,
            LIBVIRT_ACTIVE_UUID_COMMANDS[kind],
            kind=kind,
            server_index=server_index,
        ).stdout.splitlines()
        if value.strip()
    }
    quoted_uuid = shlex.quote(resolved_uuid)
    if resolved_uuid in active_uuids:
        _run(
            manager,
            f"{LIBVIRT_DESTROY_COMMANDS[kind]} {quoted_uuid}",
            kind=kind,
            server_index=server_index,
        )
    _run(
        manager,
        f"{LIBVIRT_UNDEFINE_COMMANDS[kind]} {quoted_uuid}",
        kind=kind,
        server_index=server_index,
    )
    assert_libvirt_absent(
        manager,
        kind=kind,
        name=name,
        resource_uuid=resolved_uuid,
        server_index=server_index,
    )
    return resolved_uuid


def domain_state(
    manager: RemoteCommandManager,
    *,
    resource_uuid: str,
    server_index: int,
) -> str:
    raw_state = _run(
        manager,
        f"LC_ALL=C virsh domstate --reason {shlex.quote(resource_uuid)}",
        kind="vm-state",
        server_index=server_index,
    ).stdout.strip().lower()
    state = raw_state.split(maxsplit=1)[0] if raw_state else ""
    if state not in {"running", "shut", "paused", "blocked", "idle", "crashed"}:
        raise RemoteInventoryError(
            f"remote postcondition failed: kind=vm-state "
            f"server_index={server_index} count=1"
        )
    return state


def domain_xml(
    manager: RemoteCommandManager,
    *,
    resource_uuid: str,
    server_index: int,
) -> ElementTree.Element:
    raw_xml = _run(
        manager,
        f"virsh dumpxml {shlex.quote(resource_uuid)}",
        kind="vm-xml",
        server_index=server_index,
    ).stdout
    try:
        return ElementTree.fromstring(raw_xml)
    except ElementTree.ParseError:
        raise RemoteInventoryError(
            f"remote postcondition failed: kind=vm-xml "
            f"server_index={server_index} count=1"
        ) from None


def network_xml(
    manager: RemoteCommandManager,
    *,
    resource_uuid: str,
    server_index: int,
) -> ElementTree.Element:
    raw_xml = _run(
        manager,
        f"virsh net-dumpxml {shlex.quote(resource_uuid)}",
        kind="network-xml",
        server_index=server_index,
    ).stdout
    try:
        return ElementTree.fromstring(raw_xml)
    except ElementTree.ParseError:
        raise RemoteInventoryError(
            f"remote postcondition failed: kind=network-xml "
            f"server_index={server_index} count=1"
        ) from None


def storage_pool_xml(
    manager: RemoteCommandManager,
    *,
    resource_uuid: str,
    server_index: int,
) -> ElementTree.Element:
    raw_xml = _run(
        manager,
        f"virsh pool-dumpxml {shlex.quote(resource_uuid)}",
        kind="storage-xml",
        server_index=server_index,
    ).stdout
    try:
        return ElementTree.fromstring(raw_xml)
    except ElementTree.ParseError:
        raise RemoteInventoryError(
            f"remote postcondition failed: kind=storage-xml "
            f"server_index={server_index} count=1"
        ) from None


def storage_pool_state(
    manager: RemoteCommandManager,
    *,
    resource_uuid: str,
    server_index: int,
) -> tuple[str, bool]:
    raw_info = _run(
        manager,
        f"LC_ALL=C virsh pool-info {shlex.quote(resource_uuid)}",
        kind="storage-state",
        server_index=server_index,
    ).stdout
    fields: dict[str, str] = {}
    for line in raw_info.splitlines():
        key, separator, value = line.partition(":")
        if separator:
            fields[key.strip().lower()] = value.strip().lower()
    state = fields.get("state", "")
    autostart = fields.get("autostart", "")
    if state != "running" or autostart not in {"yes", "no"}:
        raise RemoteInventoryError(
            f"remote postcondition failed: kind=storage-state "
            f"server_index={server_index} count=1"
        )
    return state, autostart == "yes"


def remote_file_metadata(
    manager: RemoteCommandManager,
    *,
    path: str,
    server_index: int,
) -> tuple[int, str]:
    quoted_path = shlex.quote(path)
    result = _run(
        manager,
        f"stat -Lc '%s' -- {quoted_path} && sha256sum -- {quoted_path}",
        kind="remote-file",
        server_index=server_index,
    )
    lines = result.stdout.splitlines()
    if len(lines) != 2:
        raise RemoteInventoryError(
            f"remote postcondition failed: kind=remote-file "
            f"server_index={server_index} count=1"
        )
    size_raw = lines[0].strip()
    digest = lines[1].split(maxsplit=1)[0]
    if not size_raw.isdigit() or int(size_raw) <= 0 or SHA256_PATTERN.fullmatch(digest) is None:
        raise RemoteInventoryError(
            f"remote postcondition failed: kind=remote-file "
            f"server_index={server_index} count=1"
        )
    return int(size_raw), digest


def qemu_virtual_size(
    manager: RemoteCommandManager,
    *,
    path: str,
    server_index: int,
) -> int:
    result = _run(
        manager,
        f"qemu-img info --output=json {shlex.quote(path)}",
        kind="vm-disk",
        server_index=server_index,
    )
    try:
        payload = json.loads(result.stdout)
        size = payload["virtual-size"]
    except (json.JSONDecodeError, KeyError, TypeError):
        raise RemoteInventoryError(
            f"remote postcondition failed: kind=vm-disk "
            f"server_index={server_index} count=1"
        ) from None
    if not isinstance(size, int) or isinstance(size, bool) or size <= 0:
        raise RemoteInventoryError(
            f"remote postcondition failed: kind=vm-disk "
            f"server_index={server_index} count=1"
        )
    return size


def assert_remote_path_absent(
    manager: RemoteCommandManager,
    *,
    path: str,
    server_index: int,
) -> None:
    _run(
        manager,
        f"test ! -e {shlex.quote(path)}",
        kind="remote-path",
        server_index=server_index,
    )
