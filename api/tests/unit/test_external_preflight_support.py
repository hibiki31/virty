import traceback
from ipaddress import IPv4Network

import pytest

import tests.external.preflight as preflight
from tests.external.support.config import EnvConfig


pytestmark = [pytest.mark.unit, pytest.mark.timeout(10)]


class _FakeResponse:
    def __init__(
        self,
        *,
        status_code: int,
        headers: dict[str, str],
        error: Exception | None = None,
    ) -> None:
        self.status_code = status_code
        self.headers = headers
        self.error = error

    def raise_for_status(self) -> None:
        if self.error is not None:
            raise self.error

    def __enter__(self):
        return self

    def __exit__(self, *_args) -> None:
        return None


class _FakeHttpClient:
    head_sizes = {"https://lab.test/image": 4096, "https://lab.test/iso": 8192}
    range_total_override: int | None = None
    error: Exception | None = None

    def __init__(self, **_kwargs) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, *_args) -> None:
        return None

    def head(self, url: str) -> _FakeResponse:
        return _FakeResponse(
            status_code=200,
            headers={"Content-Length": str(self.head_sizes[url])},
            error=self.error,
        )

    def stream(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str],
    ) -> _FakeResponse:
        assert method == "GET"
        assert headers == {"Range": "bytes=0-0"}
        total = self.range_total_override or self.head_sizes[url]
        return _FakeResponse(
            status_code=206,
            headers={"Content-Range": f"bytes 0-0/{total}"},
            error=self.error,
        )


def _download_config() -> EnvConfig:
    return EnvConfig.model_construct(
        image_url="https://lab.test/image",
        iso_url="https://lab.test/iso",
    )


def test_download_preflight_requires_consistent_head_and_range(monkeypatch) -> None:
    _FakeHttpClient.range_total_override = None
    _FakeHttpClient.error = None
    monkeypatch.setattr(preflight.httpx, "Client", _FakeHttpClient)

    assert preflight._download_sizes(_download_config()) == (4096, 8192)

    _FakeHttpClient.range_total_override = 16384
    with pytest.raises(preflight.PreflightError, match="download metadata"):
        preflight._download_sizes(_download_config())


def test_download_preflight_wraps_http_error_without_leak(monkeypatch) -> None:
    secret_seed = "credential-bearing-http-diagnostic"
    _FakeHttpClient.range_total_override = None
    _FakeHttpClient.error = RuntimeError(secret_seed)
    monkeypatch.setattr(preflight.httpx, "Client", _FakeHttpClient)

    with pytest.raises(preflight.PreflightError) as caught:
        preflight._download_sizes(_download_config())

    rendered = "".join(traceback.format_exception(caught.value))
    assert secret_seed not in rendered
    assert caught.value.__cause__ is None


def test_required_capacity_covers_downloads_and_every_vm_disk() -> None:
    sizes = (4096, 8192)

    assert preflight._required_capacity_bytes(
        "run-123456-test-cloud", vm_count=2, download_sizes=sizes
    ) == 4096
    assert preflight._required_capacity_bytes(
        "run-123456-test-iso", vm_count=2, download_sizes=sizes
    ) == 8192
    assert preflight._required_capacity_bytes(
        "run-123456-test-img", vm_count=2, download_sizes=sizes
    ) == 2 * preflight.VM_DISK_BYTES


def test_subnet_inventory_parses_libvirt_xml_and_host_routes() -> None:
    xml = """
    <network>
      <ip address="10.144.240.254" netmask="255.255.255.0" />
      <route address="10.145.0.0" prefix="16" gateway="10.0.0.1" />
    </network>
    """

    assert preflight._libvirt_ipv4_networks(xml) == {
        IPv4Network("10.144.240.0/24"),
        IPv4Network("10.145.0.0/16"),
    }
    assert preflight._route_ipv4_networks(
        "default via 192.0.2.1 dev eth0\n10.146.0.0/16 dev virbr0\n"
    ) == {IPv4Network("10.146.0.0/16")}


def test_malformed_libvirt_subnet_inventory_fails_closed() -> None:
    with pytest.raises(preflight.PreflightError, match="subnet inventory"):
        preflight._libvirt_ipv4_networks(
            '<network><ip address="10.144.240.1" netmask="invalid" /></network>'
        )
