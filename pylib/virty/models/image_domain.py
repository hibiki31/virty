from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ImageDomain")


@_attrs_define
class ImageDomain:
    """
    Attributes:
        name (str):
        uuid (str):
        owner_user_id (Union[Unset, str]):
        issuance_id (Union[Unset, int]):
    """

    name: str
    uuid: str
    owner_user_id: Union[Unset, str] = UNSET
    issuance_id: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        uuid = self.uuid
        owner_user_id = self.owner_user_id
        issuance_id = self.issuance_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "uuid": uuid,
            }
        )
        if owner_user_id is not UNSET:
            field_dict["ownerUserId"] = owner_user_id
        if issuance_id is not UNSET:
            field_dict["issuanceId"] = issuance_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        uuid = d.pop("uuid")

        owner_user_id = d.pop("ownerUserId", UNSET)

        issuance_id = d.pop("issuanceId", UNSET)

        image_domain = cls(
            name=name,
            uuid=uuid,
            owner_user_id=owner_user_id,
            issuance_id=issuance_id,
        )

        image_domain.additional_properties = d
        return image_domain

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