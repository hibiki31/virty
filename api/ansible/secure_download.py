#!/usr/bin/python
"""既存fileを上書きせず、Agent経路ではHTTPS接続先IPを固定して取得する。"""

import http.client
import ipaddress
import os
import socket
import ssl
import tempfile
import urllib.request
from pathlib import Path
from typing import BinaryIO, Callable, List, Optional, Protocol, Tuple, cast
from urllib.parse import urlsplit, urlunsplit

from ansible.module_utils.basic import AnsibleModule


class _PinnableHTTPSConnection(Protocol):
    _create_connection: Callable[
        [Tuple[str, int], Optional[float], Optional[Tuple[str, int]]],
        socket.socket,
    ]


def _resolved_global_addresses(hostname: str, port: int) -> List[str]:
    addresses: set[str] = set()
    for result in socket.getaddrinfo(
        hostname,
        port,
        type=socket.SOCK_STREAM,
    ):
        address = result[4][0]
        if not isinstance(address, str):
            raise ValueError("download hostがIP address以外を返しました")
        addresses.add(address)
    if not addresses:
        raise ValueError("download hostを名前解決できません")
    if any(not ipaddress.ip_address(value).is_global for value in addresses):
        raise ValueError("download hostがglobal address以外を返しました")
    return sorted(addresses)


def _stream_hardened(url: str, output: BinaryIO, allowed_hosts: List[str]) -> None:
    parsed = urlsplit(url)
    hostname = (parsed.hostname or "").rstrip(".").lower()
    allowed = {item.rstrip(".").lower() for item in allowed_hosts}
    if (
        parsed.scheme != "https"
        or not hostname
        or parsed.username is not None
        or parsed.password is not None
        or hostname not in allowed
    ):
        raise ValueError("download URLはallowlist内のHTTPS URLに限定されます")
    port = parsed.port or 443
    address = _resolved_global_addresses(hostname, port)[0]
    connection = http.client.HTTPSConnection(
        hostname,
        port,
        context=ssl.create_default_context(),
        timeout=30,
    )

    def pinned_connection(
        _target: Tuple[str, int],
        timeout: Optional[float] = 30,
        source_address: Optional[Tuple[str, int]] = None,
    ) -> socket.socket:
        return socket.create_connection(
            (address, port),
            timeout=timeout,
            source_address=source_address,
        )

    cast(_PinnableHTTPSConnection, connection)._create_connection = pinned_connection
    request_target = urlunsplit(("", "", parsed.path or "/", parsed.query, ""))
    try:
        connection.request("GET", request_target, headers={"Accept-Encoding": "identity"})
        response = connection.getresponse()
        if 300 <= response.status < 400:
            raise ValueError("download redirectは禁止されています")
        if response.status != 200:
            raise ValueError(f"download serverがHTTP {response.status}を返しました")
        while chunk := response.read(1024 * 1024):
            output.write(chunk)
    finally:
        connection.close()


def _stream_interactive(url: str, output: BinaryIO) -> None:
    with urllib.request.urlopen(url, timeout=30) as response:
        while chunk := response.read(1024 * 1024):
            output.write(chunk)


def _install_no_clobber(
    destination: Path,
    download: Callable[[BinaryIO], None],
) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        dir=destination.parent,
        prefix=".virty-download-",
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as output:
            download(output)
            output.flush()
            os.fsync(output.fileno())
        os.chmod(temporary, 0o644)
        # hard linkの作成はdestinationが既に存在すればatomicに失敗し、上書きしない。
        os.link(temporary, destination)
        directory_descriptor = os.open(destination.parent, os.O_RDONLY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    finally:
        temporary.unlink(missing_ok=True)


def run_module() -> None:
    module = AnsibleModule(
        argument_spec={
            "url": {"type": "str", "required": True, "no_log": True},
            "dest": {"type": "path", "required": True},
            "agent_hardened": {"type": "bool", "default": False},
            "allowed_hosts": {"type": "list", "elements": "str", "default": []},
        },
        supports_check_mode=False,
    )
    destination = Path(module.params["dest"])
    if not destination.is_absolute() or not destination.parent.is_dir():
        module.fail_json(msg="download先directoryがありません", error_code="INVALID_DESTINATION")
    if destination.exists() or destination.is_symlink():
        module.fail_json(msg="download先fileは既に存在します", error_code="DESTINATION_EXISTS")

    try:
        def download(output: BinaryIO) -> None:
            if module.params["agent_hardened"]:
                _stream_hardened(
                    module.params["url"],
                    output,
                    module.params["allowed_hosts"],
                )
            else:
                _stream_interactive(module.params["url"], output)

        _install_no_clobber(destination, download)
    except FileExistsError:
        module.fail_json(msg="download先fileは既に存在します", error_code="DESTINATION_EXISTS")
    except Exception as exc:
        module.fail_json(
            msg="image downloadに失敗しました",
            error_code=type(exc).__name__,
        )
    module.exit_json(changed=True, destination=str(destination))


def main() -> None:
    run_module()


if __name__ == "__main__":
    main()
