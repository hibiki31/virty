from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ImageForUpdateImageFlavor")


@_attrs_define
class ImageForUpdateImageFlavor:
    """
    Attributes:
        storage_uuid (str):
        path (str):
        node_name (str):
        flavor_id (int):
    """

    storage_uuid: str
    path: str
    node_name: str
    flavor_id: int
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        storage_uuid = self.storage_uuid
        path = self.path
        node_name = self.node_name
        flavor_id = self.flavor_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "storageUuid": storage_uuid,
                "path": path,
                "nodeName": node_name,
                "flavorId": flavor_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        storage_uuid = d.pop("storageUuid")

        path = d.pop("path")

        node_name = d.pop("nodeName")

        flavor_id = d.pop("flavorId")

        image_for_update_image_flavor = cls(
            storage_uuid=storage_uuid,
            path=path,
            node_name=node_name,
            flavor_id=flavor_id,
        )

        image_for_update_image_flavor.additional_properties = d
        return image_for_update_image_flavor

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
