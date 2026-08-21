from collections.abc import Callable
from typing import Any, Self, cast

import pytest

from images import function as images_function
from module import backends
from module.ansiblelib import AnsibleManager
from module.backends import (
    AnsibleBackend,
    DownloadMetadataBackend,
    FakeAnsibleBackend,
    FakeDownloadMetadataBackend,
    FakeLibvirtBackend,
    FakeSSHBackend,
    HttpDownloadMetadataBackend,
    LibvirtBackend,
    SSHBackend,
)
from module.paramikolib import ParamikoManager
from module.virtlib import VirtManager
from node.models import NodeModel


pytestmark = [pytest.mark.unit, pytest.mark.timeout(10)]


class RecordingDownloadMetadataBackend:
    def __init__(self, size: int | None) -> None:
        self.size = size
        self.calls: list[tuple[str, bool]] = []

    def body_size(self, url: str, force_range: bool = False) -> int | None:
        self.calls.append((url, force_range))
        return self.size


class HeaderOnlyResponse:
    def __init__(self, headers: dict[str, str]) -> None:
        self.headers = headers

    def raise_for_status(self) -> None:
        return None


class HeaderOnlyClient:
    def __init__(self, *args: object, **kwargs: object) -> None:
        pass

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def head(self, url: str) -> HeaderOnlyResponse:
        return HeaderOnlyResponse({})

    def get(self, url: str, headers: dict[str, str]) -> HeaderOnlyResponse:
        return HeaderOnlyResponse({})


class NeverFinishesChannel:
    def __init__(self) -> None:
        self.closed = False

    def recv_ready(self) -> bool:
        return False

    def recv_stderr_ready(self) -> bool:
        return False

    def exit_status_ready(self) -> bool:
        return False

    def close(self) -> None:
        self.closed = True


class ChannelOutput:
    def __init__(self, channel: NeverFinishesChannel) -> None:
        self.channel = channel


class NeverFinishesSSHClient:
    def __init__(self, channel: NeverFinishesChannel) -> None:
        self.channel = channel

    def exec_command(self, *args: object, **kwargs: object) -> tuple[object, ChannelOutput, object]:
        return object(), ChannelOutput(self.channel), object()

    def close(self) -> None:
        return None


def test_download_fake_satisfies_protocol() -> None:
    backend = RecordingDownloadMetadataBackend(size=1024)

    assert isinstance(backend, DownloadMetadataBackend)
    assert backend.body_size("https://invalid.example/image", force_range=True) == 1024
    assert backend.calls == [("https://invalid.example/image", True)]


def test_production_backends_satisfy_protocols() -> None:
    assert issubclass(AnsibleManager, AnsibleBackend)
    assert issubclass(ParamikoManager, SSHBackend)
    assert issubclass(VirtManager, LibvirtBackend)


def test_fake_mode_returns_deterministic_protocol_implementations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("VIRTY_BACKEND_MODE", "fake")
    monkeypatch.setenv("VIRTY_TESTING", "1")

    ansible = backends.create_ansible_backend("ignored", "no-network.invalid")
    ssh = backends.create_ssh_backend("ignored", "no-network.invalid", 22)
    libvirt = backends.create_libvirt_backend(cast(NodeModel, object()))
    download = backends.create_download_metadata_backend()

    assert isinstance(ansible, FakeAnsibleBackend)
    assert isinstance(ansible, AnsibleBackend)
    assert ansible.node_infomation() == {"virty_backend": "fake"}
    result = ansible.run(
        "commom/download_file_in_node",
        extravars={"url": "https://example.invalid/signed?token=secret"},
        sensitive_keys={"url"},
    )
    assert result.status == "successful"
    assert isinstance(ssh, FakeSSHBackend)
    assert isinstance(ssh, SSHBackend)
    assert ssh.get_node_cpu_core() == "4"
    assert isinstance(libvirt, FakeLibvirtBackend)
    assert isinstance(libvirt, LibvirtBackend)
    assert libvirt.domain_data() == []
    assert isinstance(download, FakeDownloadMetadataBackend)
    assert isinstance(download, DownloadMetadataBackend)
    assert download.body_size("https://no-network.invalid/image") == 0


def test_backend_mode_defaults_to_production_and_rejects_unknown(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("VIRTY_BACKEND_MODE", raising=False)
    assert isinstance(backends.create_download_metadata_backend(), HttpDownloadMetadataBackend)

    monkeypatch.setenv("VIRTY_BACKEND_MODE", "typo")
    with pytest.raises(RuntimeError, match="未対応のVIRTY_BACKEND_MODE"):
        backends.create_download_metadata_backend()


def test_fake_mode_requires_explicit_testing_guard(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("VIRTY_BACKEND_MODE", "fake")
    monkeypatch.delenv("VIRTY_TESTING", raising=False)

    with pytest.raises(RuntimeError, match="VIRTY_TESTING=1"):
        backends.create_download_metadata_backend()


def test_http_download_backend_delegates_without_network(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, bool]] = []

    def fake_body_size(url: str, foce_range: bool = False) -> int:
        calls.append((url, foce_range))
        return 2048

    replacement: Callable[[str, bool], int] = fake_body_size
    monkeypatch.setattr(backends, "url_body_size", replacement)

    backend = HttpDownloadMetadataBackend()
    assert backend.body_size("https://invalid.example/image", force_range=True) == 2048
    assert calls == [("https://invalid.example/image", True)]


def test_url_body_size_returns_none_without_size_headers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        images_function.httpx,
        "head",
        lambda *args, **kwargs: HeaderOnlyResponse({}),
    )
    monkeypatch.setattr(images_function.httpx, "Client", HeaderOnlyClient)

    assert images_function.url_body_size("https://invalid.example/no-size") is None


def test_paramiko_command_timeout_closes_channel() -> None:
    channel = NeverFinishesChannel()
    manager = cast(ParamikoManager, object.__new__(ParamikoManager))
    manager.user = "test"
    manager.domain = "no-network.invalid"
    manager.operation_timeout = 0.01
    manager.client = cast(Any, NeverFinishesSSHClient(channel))

    with pytest.raises(TimeoutError, match="SSH command timed out"):
        manager.run_cmd("never-finishes")

    assert channel.closed is True
