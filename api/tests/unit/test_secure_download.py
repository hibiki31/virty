import importlib.util
import io
import socket
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest


_MODULE_PATH = Path(__file__).parents[2] / "ansible/secure_download.py"
_SPEC = importlib.util.spec_from_file_location("virty_secure_download", _MODULE_PATH)
assert _SPEC is not None and _SPEC.loader is not None
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
_install_no_clobber = _MODULE._install_no_clobber
_resolved_global_addresses = _MODULE._resolved_global_addresses
_stream_hardened = _MODULE._stream_hardened


def test_secure_download_never_overwrites_existing_file(tmp_path: Path) -> None:
    destination = tmp_path / "image.qcow2"
    destination.write_bytes(b"existing-image")

    with pytest.raises(FileExistsError):
        _install_no_clobber(destination, lambda output: output.write(b"replacement"))

    assert destination.read_bytes() == b"existing-image"
    assert list(tmp_path.glob(".virty-download-*")) == []


def test_secure_download_installs_complete_file_atomically(tmp_path: Path) -> None:
    destination = tmp_path / "image.qcow2"

    _install_no_clobber(destination, lambda output: output.write(b"complete-image"))

    assert destination.read_bytes() == b"complete-image"
    assert destination.stat().st_mode & 0o777 == 0o644
    assert list(tmp_path.glob(".virty-download-*")) == []


def test_secure_download_rejects_if_any_resolved_address_is_not_global(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        _MODULE.socket,
        "getaddrinfo",
        lambda *_args, **_kwargs: [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("169.254.169.254", 443)),
        ],
    )

    with pytest.raises(ValueError, match="global address以外"):
        _resolved_global_addresses("images.example.invalid", 443)


def test_secure_download_pins_validated_ip_and_rejects_redirect(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    connected: list[tuple[str, int]] = []

    class FakeResponse:
        status = 302

        @staticmethod
        def read(_: int) -> bytes:
            return b""

    class FakeConnection:
        def __init__(self, hostname: str, port: int, **_: object) -> None:
            assert hostname == "images.example.invalid"
            assert port == 443

        def request(self, *_: object, **__: object) -> None:
            self._create_connection(("ignored", 443))

        @staticmethod
        def getresponse() -> FakeResponse:
            return FakeResponse()

        @staticmethod
        def close() -> None:
            return None

    monkeypatch.setattr(
        _MODULE,
        "_resolved_global_addresses",
        lambda *_: ["93.184.216.34"],
    )
    monkeypatch.setattr(_MODULE.http.client, "HTTPSConnection", FakeConnection)
    monkeypatch.setattr(
        _MODULE.socket,
        "create_connection",
        lambda address, **_: connected.append(address) or object(),
    )

    with pytest.raises(ValueError, match="redirect"):
        _stream_hardened(
            "https://images.example.invalid/base.qcow2",
            io.BytesIO(),
            ["images.example.invalid"],
        )
    assert connected == [("93.184.216.34", 443)]


def test_concurrent_secure_download_has_exactly_one_no_clobber_winner(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "image.qcow2"
    barrier = threading.Barrier(2)

    def install(payload: bytes) -> str:
        def download(output: object) -> None:
            barrier.wait(timeout=5)
            output.write(payload)

        try:
            _install_no_clobber(destination, download)
            return "installed"
        except FileExistsError:
            return "exists"

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(install, (b"first", b"second")))

    assert sorted(results) == ["exists", "installed"]
    assert destination.read_bytes() in {b"first", b"second"}
    assert list(tmp_path.glob(".virty-download-*")) == []
