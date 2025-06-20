from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.node_role_for_update_extra_json_type_0 import NodeRoleForUpdateExtraJsonType0


T = TypeVar("T", bound="NodeRoleForUpdate")


@_attrs_define
class NodeRoleForUpdate:
    """
    Attributes:
        node_name (str):
        role_name (str):
        extra_json (Union['NodeRoleForUpdateExtraJsonType0', None, Unset]):
    """

    node_name: str
    role_name: str
    extra_json: Union["NodeRoleForUpdateExtraJsonType0", None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.node_role_for_update_extra_json_type_0 import NodeRoleForUpdateExtraJsonType0

        node_name = self.node_name

        role_name = self.role_name

        extra_json: Union[Dict[str, Any], None, Unset]
        if isinstance(self.extra_json, Unset):
            extra_json = UNSET
        elif isinstance(self.extra_json, NodeRoleForUpdateExtraJsonType0):
            extra_json = self.extra_json.to_dict()
        else:
            extra_json = self.extra_json

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "nodeName": node_name,
                "roleName": role_name,
            }
        )
        if extra_json is not UNSET:
            field_dict["extraJson"] = extra_json

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.node_role_for_update_extra_json_type_0 import NodeRoleForUpdateExtraJsonType0

        d = src_dict.copy()
        node_name = d.pop("nodeName")

        role_name = d.pop("roleName")

        def _parse_extra_json(data: object) -> Union["NodeRoleForUpdateExtraJsonType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                extra_json_type_0 = NodeRoleForUpdateExtraJsonType0.from_dict(data)

                return extra_json_type_0
            except:  # noqa: E722
                pass
            return cast(Union["NodeRoleForUpdateExtraJsonType0", None, Unset], data)

        extra_json = _parse_extra_json(d.pop("extraJson", UNSET))

        node_role_for_update = cls(
            node_name=node_name,
            role_name=role_name,
            extra_json=extra_json,
        )

        node_role_for_update.additional_properties = d
        return node_role_for_update

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
