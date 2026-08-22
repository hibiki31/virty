import json

import pytest
from pydantic import ValidationError

from tests.external.support.manifest import (
    CleanupPlanner,
    ManifestEntry,
    ManifestError,
    ResourceManifest,
    initialize_manifest,
    load_manifest,
    mark_entry_created,
    mark_entry_removed,
    update_entry_state,
)


pytestmark = [pytest.mark.unit, pytest.mark.timeout(10)]
RUN_ID = "run-123456"
LAB_ID = "dedicated-lab"
PROJECT_ID = "virty-test-infra-1"


def _entries() -> list[ManifestEntry]:
    return [
        ManifestEntry(
            kind="vm",
            node=f"{RUN_ID}-node",
            name=f"{RUN_ID}-vm-node",
        ),
        ManifestEntry(
            kind="storage",
            node=f"{RUN_ID}-node",
            name=f"{RUN_ID}-test-img",
            path=f"/var/lib/libvirt/test/{RUN_ID}-images",
        ),
        ManifestEntry(
            kind="remote_path",
            node=f"{RUN_ID}-node",
            path=f"/tmp/{RUN_ID}-file",
        ),
        ManifestEntry(kind="node", name=f"{RUN_ID}-node"),
    ]


def _initialize(path):
    return initialize_manifest(
        path,
        run_id=RUN_ID,
        lab_id=LAB_ID,
        project_id=PROJECT_ID,
        entries=_entries(),
    )


def test_planned_partial_creation_is_cleanup_allowlisted(tmp_path) -> None:
    path = tmp_path / "manifest.json"
    manifest = _initialize(path)
    planner = CleanupPlanner(manifest)

    assert [entry.kind for entry in planner.pending_entries()] == [
        "vm",
        "storage",
        "remote_path",
        "node",
    ]
    assert planner.allows(_entries()[0]) is True
    assert planner.allows(
        ManifestEntry(
            kind="vm",
            node=f"{RUN_ID}-node",
            name=f"{RUN_ID}-unrecorded",
        )
    ) is False


def test_cleanup_planner_groups_pending_entries_by_dependency_tier(tmp_path) -> None:
    path = tmp_path / "manifest.json"
    entries = [
        _entries()[0],
        ManifestEntry(
            kind="vm",
            node=f"{RUN_ID}-node",
            name=f"{RUN_ID}-second-vm-node",
        ),
        *_entries()[1:],
    ]
    manifest = initialize_manifest(
        path,
        run_id=RUN_ID,
        lab_id=LAB_ID,
        project_id=PROJECT_ID,
        entries=entries,
    )

    tiers = CleanupPlanner(manifest).pending_tiers()

    assert [[entry.kind for entry in tier] for tier in tiers] == [
        ["vm", "vm"],
        ["storage"],
        ["remote_path"],
        ["node"],
    ]


def test_created_uuid_is_recorded_but_not_part_of_target_identity(tmp_path) -> None:
    path = tmp_path / "manifest.json"
    _initialize(path)
    vm_entry = _entries()[0]

    manifest = mark_entry_created(
        path,
        entry=vm_entry,
        resource_uuid="11111111-1111-4111-8111-111111111111",
        expected_run_id=RUN_ID,
        expected_lab_id=LAB_ID,
        expected_project_id=PROJECT_ID,
    )

    created = next(entry for entry in manifest.entries if entry.target_key() == vm_entry.target_key())
    assert created.state == "created"
    assert created.resource_uuid == "11111111-1111-4111-8111-111111111111"
    assert created.target_key() == vm_entry.target_key()


def test_created_retry_requires_the_same_uuid(tmp_path) -> None:
    path = tmp_path / "manifest.json"
    _initialize(path)
    vm_entry = _entries()[0]
    first_uuid = "11111111-1111-4111-8111-111111111111"
    mark_entry_created(
        path,
        entry=vm_entry,
        resource_uuid=first_uuid,
        expected_run_id=RUN_ID,
        expected_lab_id=LAB_ID,
        expected_project_id=PROJECT_ID,
    )

    retried = mark_entry_created(
        path,
        entry=vm_entry,
        resource_uuid=first_uuid.upper(),
        expected_run_id=RUN_ID,
        expected_lab_id=LAB_ID,
        expected_project_id=PROJECT_ID,
    )
    assert next(
        entry for entry in retried.entries if entry.target_key() == vm_entry.target_key()
    ).resource_uuid == first_uuid

    with pytest.raises(ManifestError, match="UUID"):
        mark_entry_created(
            path,
            entry=vm_entry,
            resource_uuid="22222222-2222-4222-8222-222222222222",
            expected_run_id=RUN_ID,
            expected_lab_id=LAB_ID,
            expected_project_id=PROJECT_ID,
        )


def test_retry_preserves_state_and_removed_is_idempotent(tmp_path) -> None:
    path = tmp_path / "manifest.json"
    _initialize(path)
    entry = _entries()[2]
    mark_entry_removed(
        path,
        entry=entry,
        expected_run_id=RUN_ID,
        expected_lab_id=LAB_ID,
        expected_project_id=PROJECT_ID,
    )

    retried = _initialize(path)
    assert next(item for item in retried.entries if item.target_key() == entry.target_key()).state == "removed"

    second = mark_entry_removed(
        path,
        entry=entry,
        expected_run_id=RUN_ID,
        expected_lab_id=LAB_ID,
        expected_project_id=PROJECT_ID,
    )
    assert CleanupPlanner(second).pending_entries()
    assert entry.target_key() not in {
        item.target_key() for item in CleanupPlanner(second).pending_entries()
    }
    assert entry.target_key() in {
        item.target_key() for item in CleanupPlanner(second).all_entries()
    }


def test_state_cannot_regress_and_created_vm_requires_uuid(tmp_path) -> None:
    path = tmp_path / "manifest.json"
    _initialize(path)
    vm_entry = _entries()[0]

    with pytest.raises(ManifestError, match="UUID"):
        mark_entry_created(
            path,
            entry=vm_entry,
            resource_uuid=None,
            expected_run_id=RUN_ID,
            expected_lab_id=LAB_ID,
            expected_project_id=PROJECT_ID,
        )

    mark_entry_removed(
        path,
        entry=vm_entry,
        expected_run_id=RUN_ID,
        expected_lab_id=LAB_ID,
        expected_project_id=PROJECT_ID,
    )
    with pytest.raises(ManifestError, match="逆行"):
        update_entry_state(
            path,
            target_key=vm_entry.target_key(),
            state="created",
            resource_uuid="11111111-1111-4111-8111-111111111111",
            expected_run_id=RUN_ID,
            expected_lab_id=LAB_ID,
            expected_project_id=PROJECT_ID,
        )


def test_corruption_and_identity_mismatch_fail_closed_without_content(tmp_path) -> None:
    path = tmp_path / "manifest.json"
    secret_seed = "manifest-secret-seed"
    path.write_text(f'{{"broken": "{secret_seed}"', encoding="utf-8")

    with pytest.raises(ManifestError) as caught:
        load_manifest(path)
    assert secret_seed not in str(caught.value)
    assert caught.value.__cause__ is None

    path.unlink()
    _initialize(path)
    with pytest.raises(ManifestError, match="project identity"):
        load_manifest(path, expected_project_id="virty-other-infra")


def test_duplicate_or_non_run_owned_targets_are_rejected() -> None:
    duplicate = _entries()[0]
    with pytest.raises(ValidationError):
        ResourceManifest(
            run_id=RUN_ID,
            lab_id=LAB_ID,
            project_id=PROJECT_ID,
            entries=[duplicate, duplicate.model_copy()],
        )

    with pytest.raises(ValidationError):
        ResourceManifest(
            run_id=RUN_ID,
            lab_id=LAB_ID,
            project_id=PROJECT_ID,
            entries=[ManifestEntry(kind="node", name="unowned-node")],
        )

    with pytest.raises(ValidationError):
        ManifestEntry(
            kind="vm",
            node=f"{RUN_ID}-node",
            name=f"{RUN_ID}-vm-node",
            path=f"/tmp/{RUN_ID}-unexpected",
        )


def test_manifest_rejects_secret_or_unknown_fields(tmp_path) -> None:
    path = tmp_path / "manifest.json"
    payload = {
        "version": 1,
        "run_id": RUN_ID,
        "lab_id": LAB_ID,
        "project_id": PROJECT_ID,
        "entries": [
            {
                "kind": "node",
                "name": f"{RUN_ID}-node",
                "password": "must-not-be-stored",
            }
        ],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ManifestError):
        load_manifest(path)


def test_manifest_rejects_unsafe_mode_and_symlink(tmp_path) -> None:
    path = tmp_path / "manifest.json"
    _initialize(path)
    path.chmod(0o644)

    with pytest.raises(ManifestError, match="安全"):
        load_manifest(path)

    path.unlink()
    real_path = tmp_path / "real-manifest.json"
    _initialize(real_path)
    path.symlink_to(real_path)
    with pytest.raises(ManifestError, match="安全"):
        load_manifest(path)


@pytest.mark.parametrize(
    ("state", "resource_uuid"),
    [
        ("planned", "11111111-1111-4111-8111-111111111111"),
        ("created", None),
        ("created", "not-a-uuid"),
    ],
)
def test_corrupt_manifest_rejects_invalid_state_uuid_combinations(
    tmp_path,
    state: str,
    resource_uuid: str | None,
) -> None:
    path = tmp_path / "manifest.json"
    entry = {
        "kind": "vm",
        "state": state,
        "node": f"{RUN_ID}-node",
        "name": f"{RUN_ID}-vm-node",
        "path": None,
        "resource_uuid": resource_uuid,
    }
    path.write_text(
        json.dumps(
            {
                "version": 1,
                "run_id": RUN_ID,
                "lab_id": LAB_ID,
                "project_id": PROJECT_ID,
                "entries": [entry],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ManifestError):
        load_manifest(path)
