from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.network_for_create_type import NetworkForCreateType
from ..types import UNSET, Unset

T = TypeVar("T", bound="NetworkForCreate")


@_attrs_define
class NetworkForCreate:
    """
    Attributes:
        name (str):
        node_name (str):
        type (NetworkForCreateType): brdige or ovs
        bridge_device (Union[Unset, str]):
    """

    name: str
    node_name: str
    type: NetworkForCreateType
    bridge_device: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        node_name = self.node_name
        type = self.type.value

        bridge_device = self.bridge_device

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "nodeName": node_name,
                "type": type,
            }
        )
        if bridge_device is not UNSET:
            field_dict["bridgeDevice"] = bridge_device

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        node_name = d.pop("nodeName")

        type = NetworkForCreateType(d.pop("type"))

        bridge_device = d.pop("bridgeDevice", UNSET)

        network_for_create = cls(
            name=name,
            node_name=node_name,
            type=type,
            bridge_device=bridge_device,
        )

        network_for_create.additional_properties = d
        return network_for_create

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
