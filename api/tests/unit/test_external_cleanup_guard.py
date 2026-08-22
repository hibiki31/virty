from pathlib import Path
from types import SimpleNamespace
from typing import cast

import pytest

import tests.external.cleanup as external_cleanup
from tests.external.conftest import _write_cleanup_marker
from tests.external.support.config import EnvConfig


pytestmark = [pytest.mark.unit, pytest.mark.timeout(10)]
RUN_ID = "run-123456"


class _Response:
    def raise_for_status(self) -> None:
        return None


class _Client:
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls

    def post(self, _path: str, *, json: dict[str, str]) -> _Response:
        assert set(json) == {"privateKey", "publicKey"}
        self.calls.append("key")
        return _Response()


def _env() -> EnvConfig:
    return cast(
        EnvConfig,
        SimpleNamespace(
            lab_id="dedicated-lab",
            key="private-placeholder",
            pub="public-placeholder",
        ),
    )


def test_cleanup_marker_is_atomic_and_private(tmp_path: Path) -> None:
    marker = tmp_path / "infra-cleanup-armed"

    _write_cleanup_marker(marker, RUN_ID)

    assert marker.read_text(encoding="utf-8").strip() == RUN_ID
    assert marker.stat().st_mode & 0o777 == 0o600


def test_manual_cleanup_validates_manifest_before_api_mutation(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    marker = tmp_path / "infra-cleanup-armed"
    manifest = tmp_path / "manifest.json"
    _write_cleanup_marker(marker, RUN_ID)
    calls: list[str] = []
    env = _env()

    monkeypatch.setenv("VIRTY_TEST_RUN_ID", RUN_ID)
    monkeypatch.setattr(external_cleanup, "_cleanup_marker", lambda: marker)
    monkeypatch.setattr(external_cleanup, "manifest_path", lambda: manifest)
    monkeypatch.setattr(external_cleanup, "infra_project_id", lambda: "project-id")
    monkeypatch.setattr(external_cleanup, "_load_infra_config", lambda: env)

    def load_manifest(*_args, **_kwargs) -> object:
        calls.append("manifest")
        return object()

    def create_client(_env: EnvConfig) -> _Client:
        calls.append("client")
        return _Client(calls)

    monkeypatch.setattr(external_cleanup, "load_manifest", load_manifest)
    monkeypatch.setattr(
        external_cleanup,
        "create_authenticated_client",
        create_client,
    )
    monkeypatch.setattr(
        external_cleanup,
        "cleanup_resources",
        lambda *_args: calls.append("cleanup"),
    )

    external_cleanup.main()

    assert calls == ["manifest", "client", "key", "cleanup"]


def test_guard_cli_is_read_only_and_silent(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    marker = tmp_path / "infra-cleanup-armed"
    manifest = tmp_path / "manifest.json"
    _write_cleanup_marker(marker, RUN_ID)
    calls: list[str] = []
    env = _env()

    monkeypatch.setenv("VIRTY_TEST_RUN_ID", RUN_ID)
    monkeypatch.setattr(external_cleanup, "_cleanup_marker", lambda: marker)
    monkeypatch.setattr(external_cleanup, "manifest_path", lambda: manifest)
    monkeypatch.setattr(external_cleanup, "infra_project_id", lambda: "project-id")
    monkeypatch.setattr(external_cleanup, "_load_infra_config", lambda: env)
    monkeypatch.setattr(
        external_cleanup,
        "load_manifest",
        lambda *_args, **_kwargs: calls.append("manifest"),
    )
    monkeypatch.setattr(
        external_cleanup,
        "create_authenticated_client",
        lambda _env: pytest.fail("guard CLIがAPI mutationへ進みました"),
    )

    external_cleanup.cli(["guard"])

    assert calls == ["manifest"]
    assert capsys.readouterr() == ("", "")


def test_guard_cli_failure_hides_marker_and_argument_content(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    marker = tmp_path / "infra-cleanup-armed"
    sentinel = "secret-marker-content"
    marker.write_text(sentinel, encoding="utf-8")
    marker.chmod(0o600)

    monkeypatch.setenv("VIRTY_TEST_RUN_ID", RUN_ID)
    monkeypatch.setattr(external_cleanup, "_cleanup_marker", lambda: marker)
    monkeypatch.setattr(external_cleanup, "_load_infra_config", _env)

    with pytest.raises(SystemExit) as guard_error:
        external_cleanup.cli(["guard"])
    assert str(guard_error.value) == (
        "external cleanup guard failed: kind=validation count=1"
    )
    assert sentinel not in str(guard_error.value)

    with pytest.raises(SystemExit) as usage_error:
        external_cleanup.cli([sentinel])
    assert str(usage_error.value) == "external cleanup failed: kind=usage count=1"
    assert sentinel not in str(usage_error.value)


def test_invalid_cleanup_marker_blocks_mutation_without_exposing_content(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    marker = tmp_path / "infra-cleanup-armed"
    sentinel = "secret-marker-content"
    marker.write_text(sentinel, encoding="utf-8")
    marker.chmod(0o600)
    env = _env()

    monkeypatch.setenv("VIRTY_TEST_RUN_ID", RUN_ID)
    monkeypatch.setattr(external_cleanup, "_cleanup_marker", lambda: marker)
    monkeypatch.setattr(external_cleanup, "_load_infra_config", lambda: env)
    monkeypatch.setattr(
        external_cleanup,
        "create_authenticated_client",
        lambda _env: pytest.fail("guard失敗後にAPI mutationへ進みました"),
    )

    with pytest.raises(SystemExit) as caught:
        external_cleanup.main()

    assert sentinel not in str(caught.value)
    assert str(caught.value) == "external cleanup failed: kind=setup count=1"
