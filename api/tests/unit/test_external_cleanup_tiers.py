import pytest

from tests.external.conftest import _run_cleanup_tiers
from tests.external.support.manifest import (
    CleanupPlanner,
    ManifestEntry,
    ResourceManifest,
)


pytestmark = [pytest.mark.unit, pytest.mark.timeout(10)]
RUN_ID = "run-123456"


def _planner() -> CleanupPlanner:
    node = f"{RUN_ID}-node"
    return CleanupPlanner(
        ResourceManifest(
            run_id=RUN_ID,
            lab_id="dedicated-lab",
            project_id="virty-test-infra-1",
            entries=[
                ManifestEntry(kind="vm", node=node, name=f"{RUN_ID}-vm-one"),
                ManifestEntry(kind="vm", node=node, name=f"{RUN_ID}-vm-two"),
                ManifestEntry(
                    kind="storage",
                    node=node,
                    name=f"{RUN_ID}-storage",
                    path=f"/var/lib/libvirt/test/{RUN_ID}-storage",
                ),
                ManifestEntry(kind="node", name=node),
            ],
        )
    )


def test_cleanup_failure_finishes_current_tier_and_blocks_lower_tiers() -> None:
    calls: list[str] = []

    def cleanup_entry(entry: ManifestEntry) -> bool:
        assert entry.name is not None
        calls.append(entry.name)
        return entry.name != f"{RUN_ID}-vm-one"

    succeeded = _run_cleanup_tiers(_planner(), cleanup_entry)

    assert succeeded is False
    assert calls == [f"{RUN_ID}-vm-one", f"{RUN_ID}-vm-two"]


def test_cleanup_success_advances_through_all_tiers() -> None:
    calls: list[str] = []

    def cleanup_entry(entry: ManifestEntry) -> bool:
        calls.append(entry.kind)
        return True

    succeeded = _run_cleanup_tiers(_planner(), cleanup_entry)

    assert succeeded is True
    assert calls == ["vm", "vm", "storage", "node"]
