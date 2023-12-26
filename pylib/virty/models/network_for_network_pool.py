from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="NetworkForNetworkPool")


@_attrs_define
class NetworkForNetworkPool:
    """
    Attributes:
        name (str):
        uuid (str):
        node_name (str):
        bridge (str):
        type (str):
    """

    name: str
    uuid: str
    node_name: str
    bridge: str
    type: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        uuid = self.uuid
        node_name = self.node_name
        bridge = self.bridge
        type = self.type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "uuid": uuid,
                "nodeName": node_name,
                "bridge": bridge,
                "type": type,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        uuid = d.pop("uuid")

        node_name = d.pop("nodeName")

        bridge = d.pop("bridge")

        type = d.pop("type")

        network_for_network_pool = cls(
            name=name,
            uuid=uuid,
            node_name=node_name,
            bridge=bridge,
            type=type,
        )

        network_for_network_pool.additional_properties = d
        return network_for_network_pool

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
