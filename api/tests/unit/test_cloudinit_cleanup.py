from pathlib import Path

import pytest

from module import cloudinitlib


def test_cloud_init_secret_files_are_private_and_removed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cloudinitlib, "DATA_ROOT", str(tmp_path))
    manager = cloudinitlib.CloudInitManager(
        "12345678-1234-1234-1234-123456789abc",
        "agent-vm",
    )
    manager.custom_user_data("password: prompt-injection-secret\n")

    user_data = manager.root / "user-data"
    assert user_data.read_text(encoding="utf-8") == (
        "password: prompt-injection-secret\n"
    )
    assert user_data.stat().st_mode & 0o777 == 0o600

    manager.cleanup()

    assert not manager.root.exists()


def test_cloud_init_iso_command_does_not_use_shell(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cloudinitlib, "DATA_ROOT", str(tmp_path))
    manager = cloudinitlib.CloudInitManager(
        "12345678-1234-1234-1234-123456789abc",
        "agent-vm",
    )
    calls: list[tuple[list[str], dict[str, object]]] = []

    def fake_run(command: list[str], **kwargs: object) -> None:
        calls.append((command, kwargs))
        Path(command[2]).touch(mode=0o600)

    monkeypatch.setattr(cloudinitlib.subprocess, "run", fake_run)
    iso_path = Path(manager.make_iso())

    assert calls[0][0][0] == "genisoimage"
    assert "shell" not in calls[0][1]
    assert calls[0][1]["check"] is True
    assert iso_path.stat().st_mode & 0o777 == 0o600
    manager.cleanup()
