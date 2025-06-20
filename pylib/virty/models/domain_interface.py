from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DomainInterface")


@_attrs_define
class DomainInterface:
    """
    Attributes:
        type (Union[None, Unset, str]):
        mac (Union[None, Unset, str]):
        target (Union[None, Unset, str]):
        bridge (Union[None, Unset, str]):
        network (Union[None, Unset, str]):
        port (Union[None, Unset, str]):
    """

    type: Union[None, Unset, str] = UNSET
    mac: Union[None, Unset, str] = UNSET
    target: Union[None, Unset, str] = UNSET
    bridge: Union[None, Unset, str] = UNSET
    network: Union[None, Unset, str] = UNSET
    port: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        type: Union[None, Unset, str]
        if isinstance(self.type, Unset):
            type = UNSET
        else:
            type = self.type

        mac: Union[None, Unset, str]
        if isinstance(self.mac, Unset):
            mac = UNSET
        else:
            mac = self.mac

        target: Union[None, Unset, str]
        if isinstance(self.target, Unset):
            target = UNSET
        else:
            target = self.target

        bridge: Union[None, Unset, str]
        if isinstance(self.bridge, Unset):
            bridge = UNSET
        else:
            bridge = self.bridge

        network: Union[None, Unset, str]
        if isinstance(self.network, Unset):
            network = UNSET
        else:
            network = self.network

        port: Union[None, Unset, str]
        if isinstance(self.port, Unset):
            port = UNSET
        else:
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

        def _parse_type(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        type = _parse_type(d.pop("type", UNSET))

        def _parse_mac(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        mac = _parse_mac(d.pop("mac", UNSET))

        def _parse_target(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        target = _parse_target(d.pop("target", UNSET))

        def _parse_bridge(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        bridge = _parse_bridge(d.pop("bridge", UNSET))

        def _parse_network(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        network = _parse_network(d.pop("network", UNSET))

        def _parse_port(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        port = _parse_port(d.pop("port", UNSET))

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
