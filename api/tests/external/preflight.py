"""専用labのconfig phaseとread-only readiness phase。"""

from __future__ import annotations

import argparse
import logging
import os
import re
import shlex
from contextlib import contextmanager
from ipaddress import IPv4Network, ip_network
from pathlib import Path, PurePosixPath
from typing import Iterator
from uuid import UUID
from xml.etree import ElementTree

from cryptography.hazmat.primitives import serialization
import httpx

from tests.external.conftest import _remote_paths
from tests.external.support.config import (
    EnvConfig,
    InfraConfigError,
    apply_run_prefix,
    derive_resource_name,
    load_infra_config_file,
    validate_run_id,
)
from tests.external.support.remote_inventory import (
    RemoteCommandManager,
    logical_libvirt_name,
)


class PreflightError(RuntimeError):
    """config由来の値を含まないpreflight error。"""


VM_DISK_BYTES = 64 * 1024**3
CAPACITY_MARGIN_BYTES = 1024**3
CONTENT_RANGE_PATTERN = re.compile(r"bytes\s+\d+-\d+/(\d+)")


@contextmanager
def _muted_external_loggers() -> Iterator[None]:
    logger_names = ("module.paramikolib", "module.ansiblelib")
    previous = {name: logging.getLogger(name).disabled for name in logger_names}
    for name in logger_names:
        logging.getLogger(name).disabled = True
    try:
        yield
    finally:
        for name, disabled in previous.items():
            logging.getLogger(name).disabled = disabled


def _load_base_config() -> tuple[EnvConfig, str]:
    config_path = os.getenv("VIRTY_INFRA_CONFIG", "")
    run_id = os.getenv("VIRTY_TEST_RUN_ID", "")
    if not config_path:
        raise PreflightError("config phase failed: path is missing")
    try:
        validate_run_id(run_id)
        config = load_infra_config_file(config_path)
        apply_run_prefix(config, run_id)
    except InfraConfigError as exc:
        raise PreflightError(str(exc)) from None
    return config, run_id


def _install_ssh_key(config: EnvConfig) -> None:
    """readiness containerのproject-scoped SSH volumeだけへkey pairを配置する。"""

    try:
        parsed = serialization.load_ssh_private_key(config.key.encode(), password=None)
    except (TypeError, ValueError):
        raise PreflightError("readiness failed: SSH key parse") from None
    key_type = type(parsed).__name__
    if "RSA" in key_type:
        key_name = "id_rsa"
    elif "Ed25519" in key_type:
        key_name = "id_ed25519"
    else:
        raise PreflightError("readiness failed: SSH key type")

    try:
        ssh_directory = Path.home() / ".ssh"
        ssh_directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        ssh_directory.chmod(0o700)
        for candidate in ("id_rsa", "id_rsa.pub", "id_ed25519", "id_ed25519.pub"):
            (ssh_directory / candidate).unlink(missing_ok=True)
        private_path = ssh_directory / key_name
        public_path = ssh_directory / f"{key_name}.pub"
        private_path.write_text(config.key.rstrip("\r\n") + "\n", encoding="utf-8")
        public_path.write_text(config.pub.rstrip("\r\n") + "\n", encoding="utf-8")
        private_path.chmod(0o600)
        public_path.chmod(0o600)
    except OSError:
        raise PreflightError("readiness failed: SSH key install") from None


def _download_sizes(config: EnvConfig) -> tuple[int, int]:
    sizes: list[int] = []
    try:
        with httpx.Client(follow_redirects=True, timeout=10) as client:
            for url in (config.image_url, config.iso_url):
                head = client.head(url)
                head.raise_for_status()
                head_size_raw = head.headers.get("Content-Length", "")
                with client.stream(
                    "GET",
                    url,
                    headers={"Range": "bytes=0-0"},
                ) as ranged:
                    ranged.raise_for_status()
                    match = CONTENT_RANGE_PATTERN.fullmatch(
                        ranged.headers.get("Content-Range", "")
                    )
                    if (
                        not head_size_raw.isdigit()
                        or int(head_size_raw) <= 0
                        or ranged.status_code != 206
                        or match is None
                        or int(match.group(1)) != int(head_size_raw)
                    ):
                        raise PreflightError("readiness failed: download metadata")
                sizes.append(int(head_size_raw))
    except PreflightError:
        raise
    except Exception:
        raise PreflightError("readiness failed: download metadata") from None
    return sizes[0], sizes[1]


def _required_capacity_bytes(
    storage_name: str,
    *,
    vm_count: int,
    download_sizes: tuple[int, int],
) -> int:
    if storage_name.endswith("test-cloud"):
        return download_sizes[0]
    if storage_name.endswith("test-iso"):
        return download_sizes[1]
    if storage_name.endswith("test-img"):
        return VM_DISK_BYTES * vm_count
    return 0


def _network_from_attributes(attributes: dict[str, str]) -> IPv4Network | None:
    address = attributes.get("address")
    prefix = attributes.get("prefix") or attributes.get("netmask")
    if not address or not prefix:
        return None
    try:
        parsed = ip_network(f"{address}/{prefix}", strict=False)
    except ValueError:
        raise PreflightError("readiness failed: subnet inventory") from None
    return parsed if isinstance(parsed, IPv4Network) else None


def _libvirt_ipv4_networks(raw_xml: str) -> set[IPv4Network]:
    try:
        root = ElementTree.fromstring(raw_xml)
    except ElementTree.ParseError:
        raise PreflightError("readiness failed: subnet inventory") from None
    networks: set[IPv4Network] = set()
    for element in [*root.findall(".//ip"), *root.findall(".//route")]:
        network = _network_from_attributes(element.attrib)
        if network is not None:
            networks.add(network)
    return networks


def _route_ipv4_networks(raw_routes: str) -> set[IPv4Network]:
    networks: set[IPv4Network] = set()
    for line in raw_routes.splitlines():
        for token in line.split():
            if token == "default":
                break
            try:
                parsed = ip_network(token, strict=False)
            except ValueError:
                continue
            if isinstance(parsed, IPv4Network):
                networks.add(parsed)
                break
    return networks


def _check_subnet_collisions(
    manager: RemoteCommandManager,
    env: EnvConfig,
    server_index: int,
) -> None:
    desired = {
        IPv4Network(f"10.144.{int(network.octet)}.0/24")
        for network in env.networks
    }
    existing = _route_ipv4_networks(
        manager.run_cmd("ip -4 route show").stdout
    )
    raw_uuids = manager.run_cmd("virsh net-list --all --uuid").stdout.splitlines()
    for raw_uuid in raw_uuids:
        if not raw_uuid.strip():
            continue
        try:
            resource_uuid = str(UUID(raw_uuid.strip()))
        except ValueError:
            raise PreflightError(
                f"readiness failed: server_index={server_index} "
                "check=subnet-inventory"
            ) from None
        raw_xml = manager.run_cmd(
            f"virsh net-dumpxml {shlex.quote(resource_uuid)}"
        ).stdout
        existing.update(_libvirt_ipv4_networks(raw_xml))
    overlaps = sum(
        desired_network.overlaps(existing_network)
        for desired_network in desired
        for existing_network in existing
    )
    if overlaps:
        raise PreflightError(
            f"readiness collision: server_index={server_index} count={overlaps}"
        )


def _check_server_readiness(
    env: EnvConfig,
    run_id: str,
    server_index: int,
    download_sizes: tuple[int, int],
) -> int:
    from module.ansiblelib import AnsibleManager
    from module.paramikolib import ParamikoManager

    server = env.servers[server_index]
    current_check = "ssh"
    manager = None
    check_count = 0
    try:
        with _muted_external_loggers():
            manager = ParamikoManager(
                user=server.username,
                domain=server.domain,
                port=22,
                connect_timeout=10,
                operation_timeout=60,
            )
            check_count += 1

            current_check = "sftp"
            sftp = manager.client.open_sftp()
            try:
                sftp.stat(".")
            finally:
                sftp.close()
            check_count += 1

            for current_check, command in (
                ("sudo", "sudo -n true"),
                ("libvirt-version", "virsh version --daemon"),
                ("qemu-version", "qemu-img --version"),
            ):
                manager.run_cmd(command)
                check_count += 1

            current_check = "inventory"
            inventories = {
                "storage": (
                    {storage.name for storage in env.storages},
                    manager.run_cmd("virsh pool-list --all --name").stdout,
                ),
                "network": (
                    {network.name for network in env.networks},
                    manager.run_cmd("virsh net-list --all --name").stdout,
                ),
                "vm": (
                    {
                        derive_resource_name(run_id, vm.name, server.name)
                        for vm in env.vms
                    },
                    manager.run_cmd("virsh list --all --name").stdout,
                ),
            }
            for kind, (expected, raw_names) in inventories.items():
                actual = {
                    logical_libvirt_name(kind, raw_name)
                    for raw_name in raw_names.splitlines()
                }
                if expected.intersection(actual):
                    raise PreflightError(
                        f"readiness collision: server_index={server_index} count=1"
                    )
                check_count += 1

            current_check = "subnet-inventory"
            _check_subnet_collisions(manager, env, server_index)
            check_count += 1

            current_check = "remote-path"
            for remote_path in _remote_paths(env, run_id):
                result = manager.run_cmd(
                    "if test -e "
                    f"{shlex.quote(remote_path)}; then printf present; fi"
                )
                if result.stdout == "present":
                    raise PreflightError(
                        f"readiness collision: server_index={server_index} count=1"
                    )
                check_count += 1

            current_check = "storage-parent"
            capacity_by_filesystem: dict[str, tuple[int, int]] = {}
            for storage in env.storages:
                parent = str(PurePosixPath(storage.path).parent)
                quoted_parent = shlex.quote(parent)
                manager.run_cmd(
                    f"test -d {quoted_parent} "
                    f"&& test ! -L {quoted_parent} "
                    f"&& test \"$(readlink -f -- {quoted_parent})\" = {quoted_parent} "
                    f"&& sudo -n test -w {quoted_parent}"
                )
                disk_free = manager.run_cmd(
                    f"df -PB1 -- {quoted_parent} | tail -n 1 | "
                    "awk '{print $1, $4}'"
                ).stdout.split()
                if len(disk_free) != 2 or not disk_free[1].isdigit():
                    raise PreflightError(
                        f"readiness capacity: server_index={server_index} count=1"
                    )
                required = _required_capacity_bytes(
                    storage.name,
                    vm_count=len(env.vms),
                    download_sizes=download_sizes,
                )
                previous_required, available = capacity_by_filesystem.get(
                    disk_free[0],
                    (0, int(disk_free[1])),
                )
                capacity_by_filesystem[disk_free[0]] = (
                    previous_required + required,
                    min(available, int(disk_free[1])),
                )
                check_count += 1

            for required, available in capacity_by_filesystem.values():
                if available < required + CAPACITY_MARGIN_BYTES:
                    raise PreflightError(
                        f"readiness capacity: server_index={server_index} count=1"
                    )
                check_count += 1

            current_check = "ansible-facts"
            facts = AnsibleManager(
                user=server.username,
                domain=server.domain,
            ).node_infomation()
            if not facts:
                raise PreflightError(
                    f"readiness facts: server_index={server_index} count=0"
                )
            check_count += 1
    except PreflightError:
        raise
    except Exception:
        raise PreflightError(
            f"readiness failed: server_index={server_index} check={current_check}"
        ) from None
    finally:
        if manager is not None:
            try:
                with _muted_external_loggers():
                    manager.close()
            except Exception:
                pass
    return check_count


def run_config_phase() -> None:
    config, _run_id = _load_base_config()
    print(config.lab_id)


def run_readiness_phase() -> None:
    config, run_id = _load_base_config()
    env = apply_run_prefix(config, run_id)
    download_sizes = _download_sizes(config)
    _install_ssh_key(config)
    checks = sum(
        _check_server_readiness(
            env,
            run_id,
            server_index,
            download_sizes,
        )
        for server_index in range(len(env.servers))
    )
    print(f"readiness ok servers={len(env.servers)} checks={checks}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("config", "readiness"))
    args = parser.parse_args()
    try:
        if args.phase == "config":
            run_config_phase()
        else:
            run_readiness_phase()
    except PreflightError as exc:
        raise SystemExit(str(exc)) from None


if __name__ == "__main__":
    main()
