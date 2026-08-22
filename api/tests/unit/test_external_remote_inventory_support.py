from typing import Literal

import pytest

from module.paramikolib import RemoteCommandResult
from tests.external.support.remote_inventory import (
    RemoteInventoryError,
    assert_libvirt_absent,
    assert_libvirt_present,
    delete_manifest_libvirt_target,
    logical_libvirt_name,
    qemu_virtual_size,
)


pytestmark = [pytest.mark.unit, pytest.mark.timeout(10)]


class _FakeManager:
    def __init__(self, responses: dict[str, str]) -> None:
        self.responses = responses

    def run_cmd(self, command: str) -> RemoteCommandResult:
        for prefix, stdout in self.responses.items():
            if command.startswith(prefix):
                return RemoteCommandResult(stdout=stdout, stderr="", rc=0)
        raise RuntimeError("unexpected command")


class _MutableLibvirtManager:
    def __init__(
        self,
        *,
        kind: str,
        raw_name: str | None,
        resource_uuid: str,
        active: bool = True,
    ) -> None:
        self.kind = kind
        self.raw_name = raw_name
        self.resource_uuid = resource_uuid
        self.active = active
        self.commands: list[str] = []

    @property
    def defined(self) -> bool:
        return self.raw_name is not None

    def run_cmd(self, command: str) -> RemoteCommandResult:
        self.commands.append(command)
        prefixes = {
            "vm": {
                "names": "virsh list --all --name",
                "uuids": "virsh list --all --uuid",
                "active": "virsh list --uuid",
                "lookup": "virsh domuuid",
                "destroy": "virsh destroy",
                "undefine": "virsh undefine",
            },
            "network": {
                "names": "virsh net-list --all --name",
                "uuids": "virsh net-list --all --uuid",
                "active": "virsh net-list --uuid",
                "lookup": "virsh net-uuid",
                "destroy": "virsh net-destroy",
                "undefine": "virsh net-undefine",
            },
            "storage": {
                "names": "virsh pool-list --all --name",
                "uuids": "virsh pool-list --all --uuid",
                "active": "virsh pool-list --uuid",
                "lookup": "virsh pool-uuid",
                "destroy": "virsh pool-destroy",
                "undefine": "virsh pool-undefine",
            },
        }[self.kind]
        if command == prefixes["names"]:
            stdout = f"{self.raw_name}\n" if self.defined else ""
        elif command == prefixes["uuids"]:
            stdout = f"{self.resource_uuid}\n" if self.defined else ""
        elif command == prefixes["active"]:
            stdout = f"{self.resource_uuid}\n" if self.defined and self.active else ""
        elif command.startswith(prefixes["lookup"]):
            stdout = f"{self.resource_uuid}\n"
        elif command.startswith(prefixes["destroy"]):
            self.active = False
            stdout = ""
        elif command.startswith(prefixes["undefine"]):
            self.raw_name = None
            self.active = False
            stdout = ""
        else:
            raise RuntimeError("unexpected command")
        return RemoteCommandResult(stdout=stdout, stderr="", rc=0)


def test_vm_logical_name_uses_fixed_owner_suffix_and_exact_uuid() -> None:
    resource_uuid = "11111111-1111-4111-8111-111111111111"
    manager = _FakeManager(
        {
            "virsh list --all --name": "run-123456-vm-node@owner#opaque\n",
            "virsh domuuid": f"{resource_uuid}\n",
        }
    )

    assert logical_libvirt_name("vm", "run-123456-vm-node@owner#opaque") == (
        "run-123456-vm-node"
    )
    assert_libvirt_present(
        manager,
        kind="vm",
        name="run-123456-vm-node",
        resource_uuid=resource_uuid,
        server_index=0,
    )


def test_absence_failure_does_not_expose_name_or_uuid() -> None:
    resource_uuid = "11111111-1111-4111-8111-111111111111"
    resource_name = "run-123456-vm-node"
    manager = _FakeManager(
        {
            "virsh list --all --name": f"{resource_name}@owner#opaque\n",
            "virsh list --all --uuid": f"{resource_uuid}\n",
        }
    )

    with pytest.raises(RemoteInventoryError) as caught:
        assert_libvirt_absent(
            manager,
            kind="vm",
            name=resource_name,
            resource_uuid=resource_uuid,
            server_index=2,
        )

    assert resource_name not in str(caught.value)
    assert resource_uuid not in str(caught.value)
    assert "server_index=2" in str(caught.value)


def test_qemu_virtual_size_requires_positive_integer() -> None:
    manager = _FakeManager(
        {"qemu-img info": '{"virtual-size": 68719476736}\n'}
    )

    assert qemu_virtual_size(
        manager,
        path="/run-owned/disk.img",
        server_index=0,
    ) == 64 * 1024**3


@pytest.mark.parametrize("kind", ["vm", "network", "storage"])
def test_partial_creation_cleanup_uses_exact_manifest_name(
    kind: Literal["vm", "network", "storage"],
) -> None:
    resource_uuid = "11111111-1111-4111-8111-111111111111"
    name = "run-123456-resource-node"
    raw_name = f"{name}@owner#opaque" if kind == "vm" else name
    manager = _MutableLibvirtManager(
        kind=kind,
        raw_name=raw_name,
        resource_uuid=resource_uuid,
    )

    deleted_uuid = delete_manifest_libvirt_target(
        manager,
        kind=kind,
        name=name,
        resource_uuid=None,
        server_index=0,
    )

    assert deleted_uuid == resource_uuid
    assert not manager.defined
    assert any("destroy" in command for command in manager.commands)
    assert any("undefine" in command for command in manager.commands)


def test_cleanup_retry_is_idempotent_when_exact_target_is_absent() -> None:
    resource_uuid = "11111111-1111-4111-8111-111111111111"
    manager = _MutableLibvirtManager(
        kind="vm",
        raw_name=None,
        resource_uuid=resource_uuid,
        active=False,
    )

    assert (
        delete_manifest_libvirt_target(
            manager,
            kind="vm",
            name="run-123456-vm-node",
            resource_uuid=resource_uuid,
            server_index=0,
        )
        is None
    )
    assert not any(
        command.startswith(("virsh destroy", "virsh undefine"))
        for command in manager.commands
    )


def test_unrecorded_remote_resource_is_never_deleted() -> None:
    resource_uuid = "11111111-1111-4111-8111-111111111111"
    manager = _MutableLibvirtManager(
        kind="network",
        raw_name="run-123456-unrecorded-network",
        resource_uuid=resource_uuid,
    )

    assert (
        delete_manifest_libvirt_target(
            manager,
            kind="network",
            name="run-123456-manifest-network",
            resource_uuid=None,
            server_index=1,
        )
        is None
    )
    assert manager.defined
    assert not any(
        command.startswith(("virsh net-destroy", "virsh net-undefine"))
        for command in manager.commands
    )


def test_config_drift_identity_mismatch_refuses_destructive_commands() -> None:
    manifest_uuid = "11111111-1111-4111-8111-111111111111"
    remote_uuid = "22222222-2222-4222-8222-222222222222"
    name = "run-123456-storage-node"
    manager = _MutableLibvirtManager(
        kind="storage",
        raw_name=name,
        resource_uuid=remote_uuid,
    )

    with pytest.raises(RemoteInventoryError) as caught:
        delete_manifest_libvirt_target(
            manager,
            kind="storage",
            name=name,
            resource_uuid=manifest_uuid,
            server_index=2,
        )

    message = str(caught.value)
    assert name not in message
    assert manifest_uuid not in message
    assert remote_uuid not in message
    assert manager.defined
    assert not any(
        command.startswith(("virsh pool-destroy", "virsh pool-undefine"))
        for command in manager.commands
    )


def test_created_entry_prefers_recorded_uuid_after_remote_rename() -> None:
    resource_uuid = "11111111-1111-4111-8111-111111111111"
    manager = _MutableLibvirtManager(
        kind="vm",
        raw_name="run-123456-renamed-vm@owner#opaque",
        resource_uuid=resource_uuid,
    )

    assert (
        delete_manifest_libvirt_target(
            manager,
            kind="vm",
            name="run-123456-original-vm",
            resource_uuid=resource_uuid,
            server_index=0,
        )
        == resource_uuid
    )
    assert not manager.defined
