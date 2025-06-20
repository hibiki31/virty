from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ImageDownloadForCreate")


@_attrs_define
class ImageDownloadForCreate:
    """
    Attributes:
        storage_uuid (str):
        image_url (str):
    """

    storage_uuid: str
    image_url: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        storage_uuid = self.storage_uuid

        image_url = self.image_url

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "storageUuid": storage_uuid,
                "imageUrl": image_url,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        storage_uuid = d.pop("storageUuid")

        image_url = d.pop("imageUrl")

        image_download_for_create = cls(
            storage_uuid=storage_uuid,
            image_url=image_url,
        )

        image_download_for_create.additional_properties = d
        return image_download_for_create

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
