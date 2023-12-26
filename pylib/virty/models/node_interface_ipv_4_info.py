from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="NodeInterfaceIpv4Info")


@_attrs_define
class NodeInterfaceIpv4Info:
    """
    Attributes:
        address (str):
        prefixlen (int):
        label (str):
    """

    address: str
    prefixlen: int
    label: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        address = self.address
        prefixlen = self.prefixlen
        label = self.label

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "address": address,
                "prefixlen": prefixlen,
                "label": label,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        address = d.pop("address")

        prefixlen = d.pop("prefixlen")

        label = d.pop("label")

        node_interface_ipv_4_info = cls(
            address=address,
            prefixlen=prefixlen,
            label=label,
        )

        node_interface_ipv_4_info.additional_properties = d
        return node_interface_ipv_4_info

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
