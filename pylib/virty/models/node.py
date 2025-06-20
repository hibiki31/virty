from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.node_role import NodeRole


T = TypeVar("T", bound="Node")


@_attrs_define
class Node:
    """
    Attributes:
        name (str):
        description (str):
        domain (str):
        user_name (str):
        port (int):
        core (int):
        memory (int):
        cpu_gen (str):
        os_like (str):
        os_name (str):
        os_version (str):
        status (int):
        roles (List['NodeRole']):
        qemu_version (Union[None, Unset, str]):
        libvirt_version (Union[None, Unset, str]):
    """

    name: str
    description: str
    domain: str
    user_name: str
    port: int
    core: int
    memory: int
    cpu_gen: str
    os_like: str
    os_name: str
    os_version: str
    status: int
    roles: List["NodeRole"]
    qemu_version: Union[None, Unset, str] = UNSET
    libvirt_version: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        description = self.description

        domain = self.domain

        user_name = self.user_name

        port = self.port

        core = self.core

        memory = self.memory

        cpu_gen = self.cpu_gen

        os_like = self.os_like

        os_name = self.os_name

        os_version = self.os_version

        status = self.status

        roles = []
        for roles_item_data in self.roles:
            roles_item = roles_item_data.to_dict()
            roles.append(roles_item)

        qemu_version: Union[None, Unset, str]
        if isinstance(self.qemu_version, Unset):
            qemu_version = UNSET
        else:
            qemu_version = self.qemu_version

        libvirt_version: Union[None, Unset, str]
        if isinstance(self.libvirt_version, Unset):
            libvirt_version = UNSET
        else:
            libvirt_version = self.libvirt_version

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "domain": domain,
                "userName": user_name,
                "port": port,
                "core": core,
                "memory": memory,
                "cpuGen": cpu_gen,
                "osLike": os_like,
                "osName": os_name,
                "osVersion": os_version,
                "status": status,
                "roles": roles,
            }
        )
        if qemu_version is not UNSET:
            field_dict["qemuVersion"] = qemu_version
        if libvirt_version is not UNSET:
            field_dict["libvirtVersion"] = libvirt_version

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.node_role import NodeRole

        d = src_dict.copy()
        name = d.pop("name")

        description = d.pop("description")

        domain = d.pop("domain")

        user_name = d.pop("userName")

        port = d.pop("port")

        core = d.pop("core")

        memory = d.pop("memory")

        cpu_gen = d.pop("cpuGen")

        os_like = d.pop("osLike")

        os_name = d.pop("osName")

        os_version = d.pop("osVersion")

        status = d.pop("status")

        roles = []
        _roles = d.pop("roles")
        for roles_item_data in _roles:
            roles_item = NodeRole.from_dict(roles_item_data)

            roles.append(roles_item)

        def _parse_qemu_version(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        qemu_version = _parse_qemu_version(d.pop("qemuVersion", UNSET))

        def _parse_libvirt_version(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        libvirt_version = _parse_libvirt_version(d.pop("libvirtVersion", UNSET))

        node = cls(
            name=name,
            description=description,
            domain=domain,
            user_name=user_name,
            port=port,
            core=core,
            memory=memory,
            cpu_gen=cpu_gen,
            os_like=os_like,
            os_name=os_name,
            os_version=os_version,
            status=status,
            roles=roles,
            qemu_version=qemu_version,
            libvirt_version=libvirt_version,
        )

        node.additional_properties = d
        return node

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
