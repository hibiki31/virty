from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DomainDrive")


@_attrs_define
class DomainDrive:
    """
    Attributes:
        device (Union[None, Unset, str]):
        type (Union[None, Unset, str]):
        source (Union[None, Unset, str]):
        target (Union[None, Unset, str]):
    """

    device: Union[None, Unset, str] = UNSET
    type: Union[None, Unset, str] = UNSET
    source: Union[None, Unset, str] = UNSET
    target: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        device: Union[None, Unset, str]
        if isinstance(self.device, Unset):
            device = UNSET
        else:
            device = self.device

        type: Union[None, Unset, str]
        if isinstance(self.type, Unset):
            type = UNSET
        else:
            type = self.type

        source: Union[None, Unset, str]
        if isinstance(self.source, Unset):
            source = UNSET
        else:
            source = self.source

        target: Union[None, Unset, str]
        if isinstance(self.target, Unset):
            target = UNSET
        else:
            target = self.target

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if device is not UNSET:
            field_dict["device"] = device
        if type is not UNSET:
            field_dict["type"] = type
        if source is not UNSET:
            field_dict["source"] = source
        if target is not UNSET:
            field_dict["target"] = target

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def _parse_device(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        device = _parse_device(d.pop("device", UNSET))

        def _parse_type(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        type = _parse_type(d.pop("type", UNSET))

        def _parse_source(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        source = _parse_source(d.pop("source", UNSET))

        def _parse_target(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        target = _parse_target(d.pop("target", UNSET))

        domain_drive = cls(
            device=device,
            type=type,
            source=source,
            target=target,
        )

        domain_drive.additional_properties = d
        return domain_drive

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
