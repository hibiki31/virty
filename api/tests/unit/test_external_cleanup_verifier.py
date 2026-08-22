from pathlib import Path
from types import SimpleNamespace

import pytest

import tests.external.verify_cleanup as cleanup_verifier
from domain.models import DomainModel
from module.paramikolib import RemoteCommandResult
from network.models import NetworkModel
from node.models import NodeModel
from project.models import ProjectModel
from storage.models import StorageModel
from tests.external.support.manifest import (
    CleanupPlanner,
    ManifestEntry,
    ResourceManifest,
)
from user.models import UserModel


pytestmark = [pytest.mark.unit, pytest.mark.timeout(10)]
RUN_ID = "run-123456"


def _planner() -> CleanupPlanner:
    entries = [
        ManifestEntry(
            kind="vm",
            state="created",
            node=f"{RUN_ID}-node",
            name=f"{RUN_ID}-vm-node",
            resource_uuid="11111111-1111-4111-8111-111111111111",
        ),
        ManifestEntry(
            kind="network",
            state="created",
            node=f"{RUN_ID}-node",
            name=f"{RUN_ID}-network",
            resource_uuid="22222222-2222-4222-8222-222222222222",
        ),
        ManifestEntry(
            kind="storage",
            state="created",
            node=f"{RUN_ID}-node",
            name=f"{RUN_ID}-storage",
            path=f"/var/lib/libvirt/{RUN_ID}-storage",
            resource_uuid="33333333-3333-4333-8333-333333333333",
        ),
    ]
    return CleanupPlanner(
        ResourceManifest(
            run_id=RUN_ID,
            lab_id="dedicated-lab",
            project_id="virty-infra-project",
            entries=entries,
        )
    )


class _FakeQuery:
    def __init__(self, model, counts, queried, call_counts) -> None:
        self.model = model
        self.counts = counts
        self.queried = queried
        self.call_counts = call_counts

    def filter(self, *_conditions):
        self.queried.append(self.model)
        return self

    def count(self) -> int:
        index = self.call_counts.get(self.model, 0)
        self.call_counts[self.model] = index + 1
        configured = self.counts.get(self.model, 0)
        if isinstance(configured, list):
            return configured[index] if index < len(configured) else 0
        return configured


class _FakeSession:
    def __init__(self, counts) -> None:
        self.counts = counts
        self.queried: list[type] = []
        self.call_counts: dict[type, int] = {}

    def __enter__(self):
        return self

    def __exit__(self, *_args) -> None:
        return None

    def query(self, model):
        return _FakeQuery(model, self.counts, self.queried, self.call_counts)


def test_database_inventory_checks_vm_network_and_storage(monkeypatch) -> None:
    session = _FakeSession({})
    monkeypatch.setattr(cleanup_verifier, "SessionLocal", lambda: session)

    assert cleanup_verifier._verify_database_absence(_planner()) == 9
    assert set(session.queried) == {
        DomainModel,
        NetworkModel,
        NodeModel,
        ProjectModel,
        StorageModel,
        UserModel,
    }


def test_database_inventory_failure_does_not_expose_target(monkeypatch) -> None:
    session = _FakeSession({DomainModel: 1})
    monkeypatch.setattr(cleanup_verifier, "SessionLocal", lambda: session)

    with pytest.raises(cleanup_verifier.CleanupVerificationError) as caught:
        cleanup_verifier._verify_database_absence(_planner())

    assert f"{RUN_ID}-vm-node" not in str(caught.value)
    assert "kind=vm" in str(caught.value)


def test_database_inventory_detects_unrecorded_run_owned_resource(
    monkeypatch,
) -> None:
    session = _FakeSession({DomainModel: [0, 1]})
    monkeypatch.setattr(cleanup_verifier, "SessionLocal", lambda: session)

    with pytest.raises(cleanup_verifier.CleanupVerificationError) as caught:
        cleanup_verifier._verify_database_absence(_planner())

    assert RUN_ID not in str(caught.value)
    assert "kind=vm" in str(caught.value)


class _RemoteRunInventory:
    def __init__(self) -> None:
        self.commands: list[str] = []

    def run_cmd(self, command: str) -> RemoteCommandResult:
        self.commands.append(command)
        responses = {
            "virsh list --all --name": "",
            "virsh net-list --all --name": f"{RUN_ID}-unrecorded-network\n",
            "virsh pool-list --all --name": "",
            "virsh list --all --uuid": "",
            "virsh net-list --all --uuid": "",
            "virsh pool-list --all --uuid": "",
        }
        if command not in responses:
            raise RuntimeError("unexpected command")
        return RemoteCommandResult(stdout=responses[command], stderr="", rc=0)

    def close(self) -> None:
        return None


def test_remote_inventory_detects_unrecorded_run_owned_resource_without_deleting(
    monkeypatch,
) -> None:
    import module.paramikolib as paramikolib

    manager = _RemoteRunInventory()
    env = SimpleNamespace(
        servers=[
            SimpleNamespace(
                name=f"{RUN_ID}-node",
                username="secret-user",
                domain="secret-host",
            )
        ]
    )
    monkeypatch.setattr(paramikolib, "ParamikoManager", lambda **_kwargs: manager)

    with pytest.raises(cleanup_verifier.CleanupVerificationError) as caught:
        cleanup_verifier._verify_remote_absence(env, _planner())

    assert RUN_ID not in str(caught.value)
    assert "kind=network" in str(caught.value)
    assert not any(
        "destroy" in command or "undefine" in command
        for command in manager.commands
    )


def _write_key_pair(home: Path) -> tuple[Path, Path]:
    ssh_directory = home / ".ssh"
    ssh_directory.mkdir(mode=0o700)
    private_path = ssh_directory / "id_ed25519"
    public_path = ssh_directory / "id_ed25519.pub"
    private_path.write_text("private-placeholder", encoding="utf-8")
    public_path.write_text("public-placeholder", encoding="utf-8")
    private_path.chmod(0o600)
    public_path.chmod(0o600)
    return private_path, public_path


def test_ssh_inventory_is_read_only_and_requires_exact_modes(tmp_path) -> None:
    private_path, public_path = _write_key_pair(tmp_path)
    original_private = private_path.read_text(encoding="utf-8")

    cleanup_verifier._verify_existing_ssh_key_files(tmp_path)

    assert private_path.read_text(encoding="utf-8") == original_private
    public_path.chmod(0o644)
    with pytest.raises(cleanup_verifier.CleanupVerificationError):
        cleanup_verifier._verify_existing_ssh_key_files(tmp_path)

    public_path.chmod(0o600)
    (tmp_path / ".ssh").chmod(0o755)
    with pytest.raises(cleanup_verifier.CleanupVerificationError):
        cleanup_verifier._verify_existing_ssh_key_files(tmp_path)
