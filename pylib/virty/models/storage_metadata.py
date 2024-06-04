from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="StorageMetadata")


@_attrs_define
class StorageMetadata:
    """
    Attributes:
        rool (Union[None, Unset, str]):
        protocol (Union[None, Unset, str]):
        device_type (Union[None, Unset, str]):
    """

    rool: Union[None, Unset, str] = UNSET
    protocol: Union[None, Unset, str] = UNSET
    device_type: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        rool: Union[None, Unset, str]
        if isinstance(self.rool, Unset):
            rool = UNSET
        else:
            rool = self.rool

        protocol: Union[None, Unset, str]
        if isinstance(self.protocol, Unset):
            protocol = UNSET
        else:
            protocol = self.protocol

        device_type: Union[None, Unset, str]
        if isinstance(self.device_type, Unset):
            device_type = UNSET
        else:
            device_type = self.device_type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if rool is not UNSET:
            field_dict["rool"] = rool
        if protocol is not UNSET:
            field_dict["protocol"] = protocol
        if device_type is not UNSET:
            field_dict["deviceType"] = device_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def _parse_rool(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        rool = _parse_rool(d.pop("rool", UNSET))

        def _parse_protocol(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        protocol = _parse_protocol(d.pop("protocol", UNSET))

        def _parse_device_type(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        device_type = _parse_device_type(d.pop("deviceType", UNSET))

        storage_metadata = cls(
            rool=rool,
            protocol=protocol,
            device_type=device_type,
        )

        storage_metadata.additional_properties = d
        return storage_metadata

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
