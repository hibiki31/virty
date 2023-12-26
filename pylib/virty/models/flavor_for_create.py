from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="FlavorForCreate")


@_attrs_define
class FlavorForCreate:
    """
    Attributes:
        name (str):
        os (str):
        manual_url (str):
        icon (str):
        cloud_init_ready (bool):
        description (str):
    """

    name: str
    os: str
    manual_url: str
    icon: str
    cloud_init_ready: bool
    description: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        os = self.os
        manual_url = self.manual_url
        icon = self.icon
        cloud_init_ready = self.cloud_init_ready
        description = self.description

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "os": os,
                "manualUrl": manual_url,
                "icon": icon,
                "cloudInitReady": cloud_init_ready,
                "description": description,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        os = d.pop("os")

        manual_url = d.pop("manualUrl")

        icon = d.pop("icon")

        cloud_init_ready = d.pop("cloudInitReady")

        description = d.pop("description")

        flavor_for_create = cls(
            name=name,
            os=os,
            manual_url=manual_url,
            icon=icon,
            cloud_init_ready=cloud_init_ready,
            description=description,
        )

        flavor_for_create.additional_properties = d
        return flavor_for_create

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
