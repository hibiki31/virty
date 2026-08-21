from __future__ import annotations

import tomllib
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
from packaging.version import Version

PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def _locked_versions() -> dict[str, Version]:
    versions: dict[str, Version] = {}
    for raw_line in (PACKAGE_ROOT / "requirements.lock").read_text(
        encoding="utf-8"
    ).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        name, separator, version = line.partition("==")
        assert separator == "==", f"lockはexact pinではありません: {line}"
        normalized = canonicalize_name(name)
        assert normalized not in versions, f"lock内のdependencyが重複しています: {name}"
        versions[normalized] = Version(version)
    return versions


def test_declared_runtime_and_test_dependencies_are_locked() -> None:
    project = tomllib.loads(
        (PACKAGE_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]
    declared = [
        *project["dependencies"],
        *project["optional-dependencies"]["test"],
    ]
    locked = _locked_versions()

    for raw_requirement in declared:
        requirement = Requirement(raw_requirement)
        if requirement.marker is not None and not requirement.marker.evaluate():
            continue
        name = canonicalize_name(requirement.name)
        assert name in locked, f"direct dependencyがlockにありません: {requirement.name}"
        assert requirement.specifier.contains(locked[name], prereleases=True), (
            f"lock versionがmanifestの範囲外です: {requirement.name}=={locked[name]}"
        )
