import json
import traceback

import pytest

from tests.external.support.scenario import (
    ScenarioError,
    check_phase,
    checkpoint_path,
    control_path,
    wait_for_control,
    write_checkpoint,
)


pytestmark = [pytest.mark.unit, pytest.mark.timeout(10)]


def _set_identity(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("VIRTY_TEST_RUN_ID", "run-123456")
    monkeypatch.setenv("VIRTY_INFRA_PROJECT", "virty-infra-project")
    monkeypatch.setenv("VIRTY_INFRA_SCENARIO", "worker-stop")
    monkeypatch.setenv("VIRTY_INFRA_PHASE_MARKER", str(tmp_path / "infra-phase"))


def test_checkpoint_and_control_share_one_identity_checked_file(
    monkeypatch,
    tmp_path,
) -> None:
    _set_identity(monkeypatch, tmp_path)

    started = write_checkpoint("worker-task-started")
    assert checkpoint_path() == control_path()
    assert started.phase == "worker-task-started"

    controlled = write_checkpoint("worker-restarted")
    wait_for_control("worker-restarted", timeout_seconds=0.1)
    assert check_phase("worker-restarted") == controlled
    assert controlled.run_id == "run-123456"
    assert controlled.project_id == "virty-infra-project"


def test_control_rejects_mismatched_identity(monkeypatch, tmp_path) -> None:
    _set_identity(monkeypatch, tmp_path)
    checkpoint = write_checkpoint("worker-restarted").model_dump(mode="json")
    checkpoint["project_id"] = "different-infra-project"
    control_path().write_text(json.dumps(checkpoint), encoding="utf-8")

    with pytest.raises(ScenarioError, match="identity"):
        wait_for_control("worker-restarted", timeout_seconds=0.1)


def test_phase_check_requires_an_exact_phase(monkeypatch, tmp_path) -> None:
    _set_identity(monkeypatch, tmp_path)
    write_checkpoint("worker-task-started")

    with pytest.raises(ScenarioError, match="一致"):
        check_phase("worker-restarted")


def test_corrupt_control_does_not_expose_content(monkeypatch, tmp_path) -> None:
    _set_identity(monkeypatch, tmp_path)
    secret_seed = "scenario-control-secret"
    control_path().write_text(f'{{"secret": "{secret_seed}"', encoding="utf-8")

    with pytest.raises(ScenarioError) as caught:
        wait_for_control("worker-restarted", timeout_seconds=0.1)

    rendered = "".join(traceback.format_exception(caught.value))
    assert secret_seed not in rendered
    assert caught.value.__cause__ is None
