"""host orchestrationとexternal scenarioを結ぶsecret-free checkpoint。"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path
from typing import Literal, cast

from pydantic import BaseModel, ConfigDict

from tests.external.support.config import validate_run_id
from tests.external.support.manifest import infra_project_id


ScenarioName = Literal[
    "happy",
    "task-failure",
    "worker-stop",
    "signal-int",
    "signal-term",
]
SCENARIO_NAMES = {
    "happy",
    "task-failure",
    "worker-stop",
    "signal-int",
    "signal-term",
}
PHASE_PATTERN = re.compile(r"[a-z][a-z0-9-]{0,63}")


class ScenarioError(RuntimeError):
    """checkpoint本文を含めないscenario error。"""


class ScenarioCheckpoint(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    version: Literal[1] = 1
    run_id: str
    project_id: str
    scenario: ScenarioName
    phase: str


def scenario_name() -> ScenarioName:
    name = os.getenv("VIRTY_INFRA_SCENARIO", "happy")
    if name not in SCENARIO_NAMES:
        raise ScenarioError("infra scenarioが不正です")
    return cast(ScenarioName, name)


def phase_marker_path() -> Path:
    return Path(
        os.getenv(
            "VIRTY_INFRA_PHASE_MARKER",
            "/workspace/api/data/infra-phase",
        )
    )


def checkpoint_path() -> Path:
    """後方互換名。checkpointとhost controlは同じidentity付きfileを使う。"""

    return phase_marker_path()


def control_path() -> Path:
    """host側も単一のphase markerをatomic replaceする。"""

    return phase_marker_path()


def _atomic_write(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False)
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


def write_checkpoint(phase: str) -> ScenarioCheckpoint:
    if PHASE_PATTERN.fullmatch(phase) is None:
        raise ScenarioError("scenario phaseが不正です")
    run_id = os.environ.get("VIRTY_TEST_RUN_ID", "")
    try:
        validate_run_id(run_id)
    except ValueError:
        raise ScenarioError("scenario run identityが不正です") from None
    checkpoint = ScenarioCheckpoint(
        run_id=run_id,
        project_id=infra_project_id(),
        scenario=scenario_name(),
        phase=phase,
    )
    _atomic_write(checkpoint_path(), checkpoint.model_dump(mode="json"))
    return checkpoint


def _load_control() -> ScenarioCheckpoint | None:
    path = control_path()
    if not path.is_file():
        return None
    try:
        checkpoint = ScenarioCheckpoint.model_validate_json(
            path.read_text(encoding="utf-8")
        )
    except Exception:
        raise ScenarioError("scenario controlを安全に読み取れません") from None
    expected_run_id = os.environ.get("VIRTY_TEST_RUN_ID", "")
    expected_project = infra_project_id()
    if (
        checkpoint.run_id != expected_run_id
        or checkpoint.project_id != expected_project
        or checkpoint.scenario != scenario_name()
    ):
        raise ScenarioError("scenario control identityが一致しません")
    return checkpoint


def wait_for_control(phase: str, timeout_seconds: float = 120) -> None:
    if PHASE_PATTERN.fullmatch(phase) is None or timeout_seconds <= 0:
        raise ScenarioError("scenario control待機条件が不正です")
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        checkpoint = _load_control()
        if checkpoint is not None and checkpoint.phase == phase:
            return
        time.sleep(0.2)
    raise ScenarioError("scenario control待機がtimeoutしました")


def check_phase(phase: str) -> ScenarioCheckpoint:
    if PHASE_PATTERN.fullmatch(phase) is None:
        raise ScenarioError("scenario phase確認条件が不正です")
    checkpoint = _load_control()
    if checkpoint is None or checkpoint.phase != phase:
        raise ScenarioError("scenario phaseが一致しません")
    return checkpoint


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("write", "check"))
    parser.add_argument("phase")
    args = parser.parse_args()
    try:
        if args.action == "write":
            write_checkpoint(args.phase)
        else:
            check_phase(args.phase)
    except ScenarioError as exc:
        raise SystemExit(str(exc)) from None


if __name__ == "__main__":
    main()
