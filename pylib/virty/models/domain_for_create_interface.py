from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DomainForCreateInterface")


@_attrs_define
class DomainForCreateInterface:
    """
    Attributes:
        type (str):
        network_uuid (str):
        mac (Union[Unset, str]):
        port (Union[Unset, str]):
    """

    type: str
    network_uuid: str
    mac: Union[Unset, str] = UNSET
    port: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        type = self.type
        network_uuid = self.network_uuid
        mac = self.mac
        port = self.port

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type,
                "networkUuid": network_uuid,
            }
        )
        if mac is not UNSET:
            field_dict["mac"] = mac
        if port is not UNSET:
            field_dict["port"] = port

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        type = d.pop("type")

        network_uuid = d.pop("networkUuid")

        mac = d.pop("mac", UNSET)

        port = d.pop("port", UNSET)

        domain_for_create_interface = cls(
            type=type,
            network_uuid=network_uuid,
            mac=mac,
            port=port,
        )

        domain_for_create_interface.additional_properties = d
        return domain_for_create_interface

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