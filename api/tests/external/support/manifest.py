"""run固有資源だけをcleanup対象にする永続manifest。"""

from __future__ import annotations

import json
import os
import re
import stat
from pathlib import Path, PurePosixPath
from typing import Literal, Self
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)

from tests.external.support.config import EnvConfig, derive_resource_name, validate_run_id


MANIFEST_VERSION = 1
PROJECT_ID_PATTERN = re.compile(r"[a-z0-9][a-z0-9_-]{0,127}")
ResourceKind = Literal[
    "vm",
    "network",
    "storage",
    "remote_path",
    "project",
    "node",
    "user",
]
ResourceState = Literal["planned", "created", "removed"]
CLEANUP_ORDER: dict[ResourceKind, int] = {
    "vm": 0,
    "network": 1,
    "storage": 2,
    "remote_path": 3,
    "project": 4,
    "node": 5,
    "user": 6,
}


class ManifestError(RuntimeError):
    """manifest本文を含めないfail-closed error。"""


class ManifestEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    kind: ResourceKind
    state: ResourceState = "planned"
    node: str | None = None
    name: str | None = None
    path: str | None = None
    resource_uuid: str | None = None

    @field_validator("resource_uuid")
    @classmethod
    def validate_resource_uuid(cls, value: str | None) -> str | None:
        if value is None:
            return None
        try:
            return str(UUID(value))
        except (ValueError, AttributeError, TypeError):
            raise ValueError("resource UUIDの形式が不正です") from None

    @model_validator(mode="after")
    def validate_shape(self) -> Self:
        if self.kind == "remote_path":
            if (
                self.node is None
                or self.path is None
                or self.name is not None
                or self.resource_uuid is not None
            ):
                raise ValueError("remote_path entryの形が不正です")
        elif self.kind in {"vm", "network", "storage"}:
            if self.node is None or self.name is None:
                raise ValueError("node resource entryの形が不正です")
            if self.kind == "storage" and self.path is None:
                raise ValueError("storage entryにはpathが必要です")
            if self.kind in {"vm", "network"} and self.path is not None:
                raise ValueError("VM/network entryにpathを記録できません")
        elif (
            self.name is None
            or self.node is not None
            or self.path is not None
            or self.resource_uuid is not None
        ):
            raise ValueError("local resource entryの形が不正です")
        if self.state == "planned" and self.resource_uuid is not None:
            raise ValueError("planned resourceへUUIDを記録できません")
        if (
            self.state == "created"
            and self.kind in {"vm", "network", "storage"}
            and self.resource_uuid is None
        ):
            raise ValueError("created resourceにはUUIDが必要です")
        return self

    def target_key(self) -> tuple[str, str, str, str]:
        return (self.kind, self.node or "", self.name or "", self.path or "")


class ResourceManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    version: Literal[1] = 1
    run_id: str
    lab_id: str
    project_id: str
    entries: list[ManifestEntry] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_targets(self) -> Self:
        try:
            validate_run_id(self.run_id)
        except ValueError as exc:
            raise ValueError("manifest run IDが不正です") from exc
        if PROJECT_ID_PATTERN.fullmatch(self.project_id) is None:
            raise ValueError("manifest project identityが不正です")
        keys = [entry.target_key() for entry in self.entries]
        if len(keys) != len(set(keys)):
            raise ValueError("manifest targetは重複できません")
        prefix = f"{self.run_id}-"
        for entry in self.entries:
            if entry.node is not None and not entry.node.startswith(prefix):
                raise ValueError("manifest nodeがrun固有ではありません")
            if entry.name is not None and not entry.name.startswith(prefix):
                raise ValueError("manifest nameがrun固有ではありません")
            if entry.path is not None:
                basename = PurePosixPath(entry.path).name
                if not PurePosixPath(entry.path).is_absolute() or not basename.startswith(prefix):
                    raise ValueError("manifest pathがrun固有ではありません")
        return self


def manifest_path() -> Path:
    return Path(
        os.getenv(
            "VIRTY_INFRA_MANIFEST",
            "/workspace/api/data/infra-resource-manifest.json",
        )
    )


def infra_project_id() -> str:
    project_id = os.getenv("VIRTY_INFRA_PROJECT", "")
    if PROJECT_ID_PATTERN.fullmatch(project_id) is None:
        raise ManifestError("infra project identityが不正です")
    return project_id


def _write_manifest(path: Path, manifest: ResourceManifest) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(manifest.model_dump(mode="json"), stream, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        os.chmod(path, 0o600)
        directory_descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    finally:
        temporary.unlink(missing_ok=True)


def load_manifest(
    path: Path,
    *,
    expected_run_id: str | None = None,
    expected_lab_id: str | None = None,
    expected_project_id: str | None = None,
) -> ResourceManifest:
    try:
        metadata = path.lstat()
        if (
            not stat.S_ISREG(metadata.st_mode)
            or path.is_symlink()
            or stat.S_IMODE(metadata.st_mode) != 0o600
            or metadata.st_uid != os.getuid()
        ):
            raise OSError("unsafe manifest metadata")
        payload = json.loads(path.read_text(encoding="utf-8"))
        manifest = ResourceManifest.model_validate(payload)
    except (OSError, json.JSONDecodeError, ValidationError):
        raise ManifestError("resource manifestを安全に読み取れません") from None
    if expected_run_id is not None and manifest.run_id != expected_run_id:
        raise ManifestError("resource manifestのrun identityが一致しません")
    if expected_lab_id is not None and manifest.lab_id != expected_lab_id:
        raise ManifestError("resource manifestのlab identityが一致しません")
    if expected_project_id is not None and manifest.project_id != expected_project_id:
        raise ManifestError("resource manifestのproject identityが一致しません")
    return manifest


def initialize_manifest(
    path: Path,
    *,
    run_id: str,
    lab_id: str,
    project_id: str,
    entries: list[ManifestEntry],
) -> ResourceManifest:
    proposed = ResourceManifest(
        run_id=run_id,
        lab_id=lab_id,
        project_id=project_id,
        entries=entries,
    )
    if path.exists():
        existing = load_manifest(
            path,
            expected_run_id=run_id,
            expected_lab_id=lab_id,
            expected_project_id=project_id,
        )
        if {entry.target_key() for entry in existing.entries} != {
            entry.target_key() for entry in proposed.entries
        }:
            raise ManifestError("resource manifestのallowlistが一致しません")
        return existing
    _write_manifest(path, proposed)
    return proposed


def update_entry_state(
    path: Path,
    *,
    target_key: tuple[str, str, str, str],
    state: ResourceState,
    expected_run_id: str,
    expected_lab_id: str,
    expected_project_id: str,
    resource_uuid: str | None = None,
) -> ResourceManifest:
    manifest = load_manifest(
        path,
        expected_run_id=expected_run_id,
        expected_lab_id=expected_lab_id,
        expected_project_id=expected_project_id,
    )
    matches = [entry for entry in manifest.entries if entry.target_key() == target_key]
    if len(matches) != 1:
        raise ManifestError("resource manifest targetがallowlistにありません")
    entry = matches[0]
    transitions: dict[ResourceState, set[ResourceState]] = {
        "planned": {"planned", "created", "removed"},
        "created": {"created", "removed"},
        "removed": {"removed"},
    }
    if state not in transitions[entry.state]:
        raise ManifestError("resource manifest stateを逆行できません")
    if state == "created":
        if entry.kind in {"vm", "network", "storage"} and not resource_uuid:
            raise ManifestError("作成済みresourceにはUUIDが必要です")
        normalized_uuid = None
        if resource_uuid is not None:
            try:
                normalized_uuid = str(UUID(resource_uuid))
            except (ValueError, AttributeError, TypeError):
                raise ManifestError("resource UUIDの形式が不正です") from None
        if entry.state == "created" and entry.resource_uuid != normalized_uuid:
            raise ManifestError("作成済みresourceのUUIDを変更できません")
        if normalized_uuid is not None:
            entry.resource_uuid = normalized_uuid
    elif resource_uuid is not None:
        raise ManifestError("resource UUIDはcreated遷移でだけ記録できます")
    entry.state = state
    try:
        manifest = ResourceManifest.model_validate(manifest.model_dump())
    except ValidationError:
        raise ManifestError("resource manifest stateの検証に失敗しました") from None
    _write_manifest(path, manifest)
    return manifest


def mark_entry_created(
    path: Path,
    *,
    entry: ManifestEntry,
    resource_uuid: str | None,
    expected_run_id: str,
    expected_lab_id: str,
    expected_project_id: str,
) -> ResourceManifest:
    return update_entry_state(
        path,
        target_key=entry.target_key(),
        state="created",
        resource_uuid=resource_uuid,
        expected_run_id=expected_run_id,
        expected_lab_id=expected_lab_id,
        expected_project_id=expected_project_id,
    )


def mark_entry_removed(
    path: Path,
    *,
    entry: ManifestEntry,
    expected_run_id: str,
    expected_lab_id: str,
    expected_project_id: str,
) -> ResourceManifest:
    return update_entry_state(
        path,
        target_key=entry.target_key(),
        state="removed",
        expected_run_id=expected_run_id,
        expected_lab_id=expected_lab_id,
        expected_project_id=expected_project_id,
    )


def mark_current_entry_created(
    env: EnvConfig,
    entry: ManifestEntry,
    resource_uuid: str | None = None,
) -> ResourceManifest:
    return mark_entry_created(
        manifest_path(),
        entry=entry,
        resource_uuid=resource_uuid,
        expected_run_id=os.environ["VIRTY_TEST_RUN_ID"],
        expected_lab_id=env.lab_id,
        expected_project_id=infra_project_id(),
    )


def mark_current_entry_removed(
    env: EnvConfig,
    entry: ManifestEntry,
) -> ResourceManifest:
    return mark_entry_removed(
        manifest_path(),
        entry=entry,
        expected_run_id=os.environ["VIRTY_TEST_RUN_ID"],
        expected_lab_id=env.lab_id,
        expected_project_id=infra_project_id(),
    )


class CleanupPlanner:
    def __init__(self, manifest: ResourceManifest):
        self.manifest = manifest
        self._targets = {entry.target_key() for entry in manifest.entries}

    def allows(self, candidate: ManifestEntry) -> bool:
        return candidate.target_key() in self._targets

    def pending_entries(self) -> list[ManifestEntry]:
        entries = [entry for entry in self.manifest.entries if entry.state != "removed"]
        return sorted(entries, key=lambda entry: CLEANUP_ORDER[entry.kind])

    def all_entries(self) -> list[ManifestEntry]:
        """独立inventory用にremovedを含む全allowlistを返す。"""

        return sorted(self.manifest.entries, key=lambda entry: CLEANUP_ORDER[entry.kind])


def build_expected_manifest_entries(
    env: EnvConfig,
    run_id: str,
    remote_paths: list[str],
) -> list[ManifestEntry]:
    """現行happy suiteが作成し得るtargetをmutation前に列挙する。"""

    entries: list[ManifestEntry] = []
    for server in env.servers:
        entries.append(ManifestEntry(kind="node", name=server.name))
        for vm in env.vms:
            entries.append(
                ManifestEntry(
                    kind="vm",
                    node=server.name,
                    name=derive_resource_name(run_id, vm.name, server.name),
                )
            )
        for network in env.networks:
            entries.append(
                ManifestEntry(kind="network", node=server.name, name=network.name)
            )
        for storage in env.storages:
            entries.append(
                ManifestEntry(
                    kind="storage",
                    node=server.name,
                    name=storage.name,
                    path=storage.path,
                )
            )
        for remote_path in remote_paths:
            entries.append(
                ManifestEntry(kind="remote_path", node=server.name, path=remote_path)
            )
    entries.append(ManifestEntry(kind="user", name=env.username))
    entries.extend(ManifestEntry(kind="user", name=user.username) for user in env.users)
    entries.extend(
        ManifestEntry(kind="project", name=project.name) for project in env.projects
    )
    return entries
