from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.node_role_extrajson import NodeRoleExtrajson


T = TypeVar("T", bound="NodeRole")


@_attrs_define
class NodeRole:
    """
    Attributes:
        role_name (str):
        extra_json (Union[Unset, NodeRoleExtrajson]):
    """

    role_name: str
    extra_json: Union[Unset, "NodeRoleExtrajson"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        role_name = self.role_name
        extra_json: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.extra_json, Unset):
            extra_json = self.extra_json.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "roleName": role_name,
            }
        )
        if extra_json is not UNSET:
            field_dict["extraJson"] = extra_json

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.node_role_extrajson import NodeRoleExtrajson

        d = src_dict.copy()
        role_name = d.pop("roleName")

        _extra_json = d.pop("extraJson", UNSET)
        extra_json: Union[Unset, NodeRoleExtrajson]
        if isinstance(_extra_json, Unset):
            extra_json = UNSET
        else:
            extra_json = NodeRoleExtrajson.from_dict(_extra_json)

        node_role = cls(
            role_name=role_name,
            extra_json=extra_json,
        )

        node_role.additional_properties = d
        return node_role

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
