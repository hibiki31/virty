from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="NetworkPortgroup")


@_attrs_define
class NetworkPortgroup:
    """
    Attributes:
        name (str):
        is_default (bool):
        vlan_id (Union[None, Unset, str]):
    """

    name: str
    is_default: bool
    vlan_id: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        is_default = self.is_default

        vlan_id: Union[None, Unset, str]
        if isinstance(self.vlan_id, Unset):
            vlan_id = UNSET
        else:
            vlan_id = self.vlan_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "isDefault": is_default,
            }
        )
        if vlan_id is not UNSET:
            field_dict["vlanId"] = vlan_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        is_default = d.pop("isDefault")

        def _parse_vlan_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        vlan_id = _parse_vlan_id(d.pop("vlanId", UNSET))

        network_portgroup = cls(
            name=name,
            is_default=is_default,
            vlan_id=vlan_id,
        )

        network_portgroup.additional_properties = d
        return network_portgroup

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
