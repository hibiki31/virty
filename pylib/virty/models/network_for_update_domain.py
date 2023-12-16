from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="NetworkForUpdateDomain")


@_attrs_define
class NetworkForUpdateDomain:
    """
    Attributes:
        mac (str):
        network_uuid (str):
        port (Union[Unset, str]):
    """

    mac: str
    network_uuid: str
    port: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        mac = self.mac
        network_uuid = self.network_uuid
        port = self.port

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "mac": mac,
                "networkUuid": network_uuid,
            }
        )
        if port is not UNSET:
            field_dict["port"] = port

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        mac = d.pop("mac")

        network_uuid = d.pop("networkUuid")

        port = d.pop("port", UNSET)

        network_for_update_domain = cls(
            mac=mac,
            network_uuid=network_uuid,
            port=port,
        )

        network_for_update_domain.additional_properties = d
        return network_for_update_domain

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
