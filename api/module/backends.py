"""外部systemへ接続するproduction backendの生成境界。"""

import os
from collections.abc import Mapping
from typing import Any, Literal, Protocol, runtime_checkable

from images.function import url_body_size
from module.ansiblelib import AnsibleManager, AnsibleRunResult
from module.paramikolib import ParamikoManager, RemoteCommandResult
from module.virtlib import VirtManager
from node.models import NodeModel


@runtime_checkable
class AnsibleBackend(Protocol):
    """Ansibleを使う処理が必要とする最小interface。"""

    def run(
        self,
        playbook_name: str,
        extravars: Mapping[str, Any] | None = None,
        timeout: int = 900,
        *,
        sensitive_keys: set[str] | None = None,
    ) -> AnsibleRunResult: ...

    def node_infomation(self) -> Mapping[str, Any]: ...


@runtime_checkable
class SSHBackend(Protocol):
    """SSH越しの情報取得に必要なinterface。"""

    def run_cmd(self, command: str) -> RemoteCommandResult: ...

    def get_node_mem(self) -> float: ...

    def get_node_cpu_core(self) -> str: ...

    def get_node_libvirt_version(self) -> str: ...

    def get_node_qemu_version(self) -> str: ...

    def get_node_cpu_name(self) -> str: ...

    def get_node_os_release(self) -> Mapping[str, str]: ...


@runtime_checkable
class LibvirtBackend(Protocol):
    """libvirt操作の差し替え点。引数と返却値は既存adapterを透過する。"""

    def domain_data(self) -> list[dict[str, Any]]: ...

    def storages_data(self, token: str, uuids: list[str] = ...) -> list[Any]: ...

    def image_delete(self, storage_uuid: str, image_name: str, secure: bool = False) -> None: ...

    def network_data(self) -> list[Any]: ...

    def domain_define(self, xml_str: str) -> None: ...

    def domain_undefine(self, uuid: str) -> None: ...

    def domain_destroy(self, uuid: str) -> None: ...

    def domain_poweron(self, uuid: str) -> None: ...

    def domain_cdrom(self, uuid: str, target: str | None = None, path: str = "") -> None: ...

    def domain_network(
        self,
        uuid: str,
        network: str,
        port: str | None,
        mac: str,
    ) -> None: ...

    def storage_define(self, xml_str: str) -> None: ...

    def storage_undefine(self, uuid: str) -> None: ...

    def network_define(self, xml_str: str) -> None: ...

    def network_undefine(self, uuid: str) -> None: ...

    def network_ovs_add(self, uuid: str, name: str, vlan: int) -> None: ...

    def network_ovs_delete(self, uuid: str, name: str) -> None: ...


@runtime_checkable
class DownloadMetadataBackend(Protocol):
    """download前のmetadata取得interface。"""

    def body_size(self, url: str, force_range: bool = False) -> int | None: ...


class HttpDownloadMetadataBackend:
    """httpxを使うproduction実装。"""

    def body_size(self, url: str, force_range: bool = False) -> int | None:
        return url_body_size(url=url, foce_range=force_range)


class _FaultInjectableFake:
    """標準testが外部接続なしで失敗経路を選択するための共通基盤。"""

    def __init__(self, failures: Mapping[str, Exception] | None = None) -> None:
        self._failures = dict(failures or {})

    def _raise_failure(self, operation: str) -> None:
        failure = self._failures.get(operation)
        if failure is not None:
            raise failure


class FakeAnsibleBackend(_FaultInjectableFake):
    """外部processを起動せず固定値を返すverify専用実装。"""

    def run(
        self,
        playbook_name: str,
        extravars: Mapping[str, Any] | None = None,
        timeout: int = 900,
        *,
        sensitive_keys: set[str] | None = None,
    ) -> AnsibleRunResult:
        self._raise_failure("run")
        return AnsibleRunResult(
            status="successful",
            rc=0,
            events_ok=[],
            events_failed=[],
            playbook_on_stats={},
        )

    def node_infomation(self) -> Mapping[str, Any]:
        self._raise_failure("node_infomation")
        return {"virty_backend": "fake"}


class FakeSSHBackend(_FaultInjectableFake):
    """SSH接続を行わないverify専用実装。"""

    def run_cmd(self, command: str) -> RemoteCommandResult:
        self._raise_failure("run_cmd")
        return RemoteCommandResult(stdout="", stderr="", rc=0)

    def get_node_mem(self) -> float:
        self._raise_failure("get_node_mem")
        return 8.0

    def get_node_cpu_core(self) -> str:
        self._raise_failure("get_node_cpu_core")
        return "4"

    def get_node_libvirt_version(self) -> str:
        self._raise_failure("get_node_libvirt_version")
        return "fake-libvirt-1.0"

    def get_node_qemu_version(self) -> str:
        self._raise_failure("get_node_qemu_version")
        return "fake-qemu-1.0"

    def get_node_cpu_name(self) -> str:
        self._raise_failure("get_node_cpu_name")
        return "Virty Fake CPU"

    def get_node_os_release(self) -> Mapping[str, str]:
        self._raise_failure("get_node_os_release")
        return {
            "ID_LIKE": "debian",
            "PRETTY_NAME": "Virty Fake Linux",
            "VERSION_ID": "1",
        }


class FakeLibvirtBackend(_FaultInjectableFake):
    """libvirt資源を変更せず空のinventoryを返すverify専用実装。"""

    def domain_data(self) -> list[dict[str, Any]]:
        self._raise_failure("domain_data")
        return []

    def storages_data(self, token: str, uuids: list[str] | None = None) -> list[Any]:
        self._raise_failure("storages_data")
        return []

    def image_delete(self, storage_uuid: str, image_name: str, secure: bool = False) -> None:
        self._raise_failure("image_delete")
        return None

    def network_data(self) -> list[Any]:
        self._raise_failure("network_data")
        return []

    def domain_define(self, xml_str: str) -> None:
        self._raise_failure("domain_define")
        return None

    def domain_undefine(self, uuid: str) -> None:
        self._raise_failure("domain_undefine")
        return None

    def domain_destroy(self, uuid: str) -> None:
        self._raise_failure("domain_destroy")
        return None

    def domain_poweron(self, uuid: str) -> None:
        self._raise_failure("domain_poweron")
        return None

    def domain_cdrom(self, uuid: str, target: str | None = None, path: str = "") -> None:
        self._raise_failure("domain_cdrom")
        return None

    def domain_network(
        self,
        uuid: str,
        network: str,
        port: str | None,
        mac: str,
    ) -> None:
        self._raise_failure("domain_network")
        return None

    def storage_define(self, xml_str: str) -> None:
        self._raise_failure("storage_define")
        return None

    def storage_undefine(self, uuid: str) -> None:
        self._raise_failure("storage_undefine")
        return None

    def network_define(self, xml_str: str) -> None:
        self._raise_failure("network_define")
        return None

    def network_undefine(self, uuid: str) -> None:
        self._raise_failure("network_undefine")
        return None

    def network_ovs_add(self, uuid: str, name: str, vlan: int) -> None:
        self._raise_failure("network_ovs_add")
        return None

    def network_ovs_delete(self, uuid: str, name: str) -> None:
        self._raise_failure("network_ovs_delete")
        return None


class FakeDownloadMetadataBackend(_FaultInjectableFake):
    """HTTP requestを行わないverify専用実装。"""

    def body_size(self, url: str, force_range: bool = False) -> int | None:
        self._raise_failure("body_size")
        return 0


BackendMode = Literal["production", "fake"]


def _backend_mode() -> BackendMode:
    mode = os.getenv("VIRTY_BACKEND_MODE", "production")
    if mode == "production":
        return "production"
    if mode == "fake":
        if os.getenv("VIRTY_TESTING") != "1":
            raise RuntimeError("fake backendにはVIRTY_TESTING=1が必要です")
        return "fake"
    raise RuntimeError(f"未対応のVIRTY_BACKEND_MODEです: {mode}")


def create_ansible_backend(user: str, domain: str) -> AnsibleBackend:
    """選択されたAnsible backendを生成する。"""

    if _backend_mode() == "fake":
        return FakeAnsibleBackend()
    return AnsibleManager(user=user, domain=domain)


def create_ssh_backend(user: str, domain: str, port: int) -> SSHBackend:
    """選択されたSSH backendを生成する。"""

    if _backend_mode() == "fake":
        return FakeSSHBackend()
    return ParamikoManager(user=user, domain=domain, port=port)


def create_libvirt_backend(node_model: NodeModel) -> LibvirtBackend:
    """選択されたlibvirt backendを生成する。"""

    if _backend_mode() == "fake":
        return FakeLibvirtBackend()
    return VirtManager(node_model=node_model)


def create_download_metadata_backend() -> DownloadMetadataBackend:
    """選択されたdownload metadata backendを生成する。"""

    if _backend_mode() == "fake":
        return FakeDownloadMetadataBackend()
    return HttpDownloadMetadataBackend()
