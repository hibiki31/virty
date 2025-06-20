from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DomainForCreateDisk")


@_attrs_define
class DomainForCreateDisk:
    """
    Attributes:
        type (str):
        save_pool_uuid (str):
        original_pool_uuid (Union[None, Unset, str]):
        original_name (Union[None, Unset, str]):
        size_giga_byte (Union[None, Unset, int]):
        template_name (Union[None, Unset, str]):
    """

    type: str
    save_pool_uuid: str
    original_pool_uuid: Union[None, Unset, str] = UNSET
    original_name: Union[None, Unset, str] = UNSET
    size_giga_byte: Union[None, Unset, int] = UNSET
    template_name: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        type = self.type

        save_pool_uuid = self.save_pool_uuid

        original_pool_uuid: Union[None, Unset, str]
        if isinstance(self.original_pool_uuid, Unset):
            original_pool_uuid = UNSET
        else:
            original_pool_uuid = self.original_pool_uuid

        original_name: Union[None, Unset, str]
        if isinstance(self.original_name, Unset):
            original_name = UNSET
        else:
            original_name = self.original_name

        size_giga_byte: Union[None, Unset, int]
        if isinstance(self.size_giga_byte, Unset):
            size_giga_byte = UNSET
        else:
            size_giga_byte = self.size_giga_byte

        template_name: Union[None, Unset, str]
        if isinstance(self.template_name, Unset):
            template_name = UNSET
        else:
            template_name = self.template_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type,
                "savePoolUuid": save_pool_uuid,
            }
        )
        if original_pool_uuid is not UNSET:
            field_dict["originalPoolUuid"] = original_pool_uuid
        if original_name is not UNSET:
            field_dict["originalName"] = original_name
        if size_giga_byte is not UNSET:
            field_dict["sizeGigaByte"] = size_giga_byte
        if template_name is not UNSET:
            field_dict["templateName"] = template_name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        type = d.pop("type")

        save_pool_uuid = d.pop("savePoolUuid")

        def _parse_original_pool_uuid(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        original_pool_uuid = _parse_original_pool_uuid(d.pop("originalPoolUuid", UNSET))

        def _parse_original_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        original_name = _parse_original_name(d.pop("originalName", UNSET))

        def _parse_size_giga_byte(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        size_giga_byte = _parse_size_giga_byte(d.pop("sizeGigaByte", UNSET))

        def _parse_template_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        template_name = _parse_template_name(d.pop("templateName", UNSET))

        domain_for_create_disk = cls(
            type=type,
            save_pool_uuid=save_pool_uuid,
            original_pool_uuid=original_pool_uuid,
            original_name=original_name,
            size_giga_byte=size_giga_byte,
            template_name=template_name,
        )

        domain_for_create_disk.additional_properties = d
        return domain_for_create_disk

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
