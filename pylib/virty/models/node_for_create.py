from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="NodeForCreate")


@_attrs_define
class NodeForCreate:
    """
    Attributes:
        name (str):
        description (str):
        domain (str):
        user_name (str):
        port (int):
        libvirt_role (bool):
    """

    name: str
    description: str
    domain: str
    user_name: str
    port: int
    libvirt_role: bool
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        description = self.description

        domain = self.domain

        user_name = self.user_name

        port = self.port

        libvirt_role = self.libvirt_role

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "domain": domain,
                "userName": user_name,
                "port": port,
                "libvirtRole": libvirt_role,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        description = d.pop("description")

        domain = d.pop("domain")

        user_name = d.pop("userName")

        port = d.pop("port")

        libvirt_role = d.pop("libvirtRole")

        node_for_create = cls(
            name=name,
            description=description,
            domain=domain,
            user_name=user_name,
            port=port,
            libvirt_role=libvirt_role,
        )

        node_for_create.additional_properties = d
        return node_for_create

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
