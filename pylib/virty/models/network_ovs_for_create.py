from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="NetworkOVSForCreate")


@_attrs_define
class NetworkOVSForCreate:
    """
    Attributes:
        default (bool):
        name (str):
        vlan_id (Union[None, Unset, int]):
    """

    default: bool
    name: str
    vlan_id: Union[None, Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        default = self.default

        name = self.name

        vlan_id: Union[None, Unset, int]
        if isinstance(self.vlan_id, Unset):
            vlan_id = UNSET
        else:
            vlan_id = self.vlan_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "default": default,
                "name": name,
            }
        )
        if vlan_id is not UNSET:
            field_dict["vlanId"] = vlan_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        default = d.pop("default")

        name = d.pop("name")

        def _parse_vlan_id(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        vlan_id = _parse_vlan_id(d.pop("vlanId", UNSET))

        network_ovs_for_create = cls(
            default=default,
            name=name,
            vlan_id=vlan_id,
        )

        network_ovs_for_create.additional_properties = d
        return network_ovs_for_create

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
