from pathlib import Path

import pytest

import worker


pytestmark = pytest.mark.unit


def test_worker_recreates_ready_marker_after_scheduler_recovery(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    ready_file = tmp_path / "worker.ready"
    ready_file.write_text("stale", encoding="utf-8")
    observations: list[tuple[str, bool]] = []

    monkeypatch.setenv("VIRTY_WORKER_READY_FILE", str(ready_file))
    monkeypatch.setattr(worker.mp, "set_start_method", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(worker.os, "makedirs", lambda *_args, **_kwargs: None)

    def init_scheduler() -> None:
        observations.append(("init", ready_file.exists()))

    def stop_after_ready(_: object) -> None:
        observations.append(("run", ready_file.exists()))
        raise RuntimeError("test worker stop")

    monkeypatch.setattr(worker, "init_scheduler", init_scheduler)
    monkeypatch.setattr(worker, "run_scheduler", stop_after_ready)

    with pytest.raises(RuntimeError, match="test worker stop"):
        worker.main()

    assert observations == [("init", False), ("run", True)]
