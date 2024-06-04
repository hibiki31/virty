from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DomainDrive")


@_attrs_define
class DomainDrive:
    """
    Attributes:
        device (Union[Unset, str]):
        type (Union[Unset, str]):
        source (Union[Unset, str]):
        target (Union[Unset, str]):
    """

    device: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    source: Union[Unset, str] = UNSET
    target: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        device = self.device
        type = self.type
        source = self.source
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
        device = d.pop("device", UNSET)

        type = d.pop("type", UNSET)

        source = d.pop("source", UNSET)

        target = d.pop("target", UNSET)

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
