from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DomainInterface")


@_attrs_define
class DomainInterface:
    """
    Attributes:
        type (Union[Unset, str]):
        mac (Union[Unset, str]):
        target (Union[Unset, str]):
        bridge (Union[Unset, str]):
        network (Union[Unset, str]):
        port (Union[Unset, str]):
    """

    type: Union[Unset, str] = UNSET
    mac: Union[Unset, str] = UNSET
    target: Union[Unset, str] = UNSET
    bridge: Union[Unset, str] = UNSET
    network: Union[Unset, str] = UNSET
    port: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        type = self.type
        mac = self.mac
        target = self.target
        bridge = self.bridge
        network = self.network
        port = self.port

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if type is not UNSET:
            field_dict["type"] = type
        if mac is not UNSET:
            field_dict["mac"] = mac
        if target is not UNSET:
            field_dict["target"] = target
        if bridge is not UNSET:
            field_dict["bridge"] = bridge
        if network is not UNSET:
            field_dict["network"] = network
        if port is not UNSET:
            field_dict["port"] = port

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        type = d.pop("type", UNSET)

        mac = d.pop("mac", UNSET)

        target = d.pop("target", UNSET)

        bridge = d.pop("bridge", UNSET)

        network = d.pop("network", UNSET)

        port = d.pop("port", UNSET)

        domain_interface = cls(
            type=type,
            mac=mac,
            target=target,
            bridge=bridge,
            network=network,
            port=port,
        )

        domain_interface.additional_properties = d
        return domain_interface

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
