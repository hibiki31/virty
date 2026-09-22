"""workerが扱う外部資源のpostconditionを共有状態へ再現する。"""

from collections.abc import Mapping
from pathlib import PurePosixPath
from typing import Any
from xml.etree import ElementTree

from module.ansiblelib import AnsibleRunResult
from module.backends import FakeLibvirtBackend
from network.schemas import PaseNetwork
from storage.schemas import ImageForLibvirt, StorageForLibvirt
from tests.e2e.state import fail_once, locked_state, require_e2e_environment


def inventory_domain_xml(xml_str: str) -> str:
    """libvirt XMLDescが返すmemory単位の正規化を再現する。"""

    tree = ElementTree.fromstring(xml_str)
    for name in ("memory", "currentMemory"):
        memory = tree.find(name)
        if memory is None:
            continue
        unit = memory.get("unit", "KiB")
        if unit in {"Mib", "MiB"}:
            memory.text = str(int(memory.text or "0") * 1024)
            memory.set("unit", "KiB")
        elif unit != "KiB":
            raise NotImplementedError(f"E2Eで未対応のmemory単位です: {unit}")
    return ElementTree.tostring(tree, encoding="unicode")


class E2EAnsibleBackend:
    def __init__(self, domain: str) -> None:
        require_e2e_environment()
        self.domain = domain

    def node_infomation(self) -> Mapping[str, Any]:
        raise NotImplementedError("E2Eではnode情報収集を実装していません")

    def run(
        self,
        playbook_name: str,
        extravars: Mapping[str, Any] | None = None,
        timeout: int = 900,
        *,
        sensitive_keys: set[str] | None = None,
    ) -> AnsibleRunResult:
        variables = dict(extravars or {})
        supported = {"vms/qemu_image_create", "vms/qemu_image_resize", "commom/copy_node_internal"}
        if playbook_name not in supported:
            raise NotImplementedError(f"E2Eで未対応のplaybookです: {playbook_name}")
        with locked_state() as state:
            fail_once(state, "ansible.run")
            path = str(variables["dst"] if playbook_name == "commom/copy_node_internal" else variables["path"])
            storages = [item for item in state["storages"].values() if item["domain"] == self.domain]
            storage = next((item for item in storages if PurePosixPath(path).parent == PurePosixPath(item["path"])), None)
            if storage is None:
                raise ValueError("E2Eの保存先storageがありません")
            existing = next((image for image in storage["images"] if image["path"] == path), None)
            if playbook_name == "vms/qemu_image_resize":
                if existing is None:
                    raise ValueError("E2Eのresize対象imageがありません")
                existing["capacity"] = int(str(variables["size"]).removesuffix("G"))
            else:
                if existing is not None:
                    raise ValueError("E2Eの保存先imageは既にあります")
                capacity = 0
                if playbook_name == "commom/copy_node_internal":
                    source = next((image for item in storages for image in item["images"] if image["path"] == variables["src"]), None)
                    if source is None:
                        raise ValueError("E2Eのcopy元imageがありません")
                    capacity = source["capacity"]
                else:
                    capacity = int(str(variables["size"]).removesuffix("G"))
                storage["images"].append({"name": PurePosixPath(path).name, "path": path, "capacity": capacity, "allocation": 0})
        return AnsibleRunResult(status="successful", rc=0, events_ok=[], events_failed=[], playbook_on_stats={})


class E2ELibvirtBackend(FakeLibvirtBackend):
    """未対応操作を拒否し、実装した操作だけがinventoryを変更する。"""

    def __init__(self, node_name: str) -> None:
        super().__init__()
        require_e2e_environment()
        self.node_name = node_name

    def _raise_failure(self, operation: str) -> None:
        # 継承した未実装のFake操作を万能な成功として扱わない。
        raise NotImplementedError(f"E2Eで未対応のlibvirt操作です: {operation}")

    def domain_data(self) -> list[dict[str, Any]]:
        with locked_state() as state:
            fail_once(state, "domain_data")
            return [dict(item) for item in state["domains"].values() if item["node_name"] == self.node_name]

    def domain_define(self, xml_str: str) -> None:
        tree = ElementTree.fromstring(xml_str)
        uuid = tree.findtext("uuid")
        if not uuid or not tree.findtext("name"):
            raise ValueError("E2E domain XMLにuuidとnameが必要です")
        with locked_state() as state:
            fail_once(state, "domain_define")
            images = {image["path"] for pool in state["storages"].values() if pool["node_name"] == self.node_name for image in pool["images"]}
            for source in tree.findall("./devices/disk[@device='disk']/source"):
                if source.get("file") not in images:
                    raise ValueError("E2E domain XMLが存在しないdiskを参照しています")
            networks = {network["name"] for network in state["networks"].values() if network["node_name"] == self.node_name}
            for source in tree.findall("./devices/interface[@type='network']/source"):
                if source.get("network") not in networks:
                    raise ValueError("E2E domain XMLが存在しないnetworkを参照しています")
            state["domains"][uuid] = {"node_name": self.node_name, "xml": inventory_domain_xml(xml_str), "status": 5, "auto": False}

    def domain_undefine(self, uuid: str) -> None:
        with locked_state() as state:
            domain = state["domains"][uuid]
            if domain["node_name"] != self.node_name:
                raise ValueError("E2E domainが別nodeに属しています")
            del state["domains"][uuid]

    def _power(self, uuid: str, status: int) -> None:
        with locked_state() as state:
            fail_once(state, "domain_power")
            domain = state["domains"][uuid]
            if domain["node_name"] != self.node_name:
                raise ValueError("E2E domainが別nodeに属しています")
            domain["status"] = status

    def domain_destroy(self, uuid: str) -> None:
        self._power(uuid, 5)

    def domain_poweron(self, uuid: str) -> None:
        self._power(uuid, 1)

    def storages_data(self, token: str, uuids: list[str] | None = None) -> list[StorageForLibvirt]:
        with locked_state() as state:
            fail_once(state, "storages_data")
            return [StorageForLibvirt(
                **{key: value for key, value in pool.items() if key not in {"domain", "images"}},
                update_token=token,
                images=[ImageForLibvirt(**image, update_token=token, storage_uuid=pool["uuid"]) for image in pool["images"]],
            ) for pool in state["storages"].values() if pool["node_name"] == self.node_name and (not uuids or pool["uuid"] in uuids)]

    def network_data(self) -> list[PaseNetwork]:
        with locked_state() as state:
            return [PaseNetwork.model_validate(item) for item in state["networks"].values() if item["node_name"] == self.node_name]
