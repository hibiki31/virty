from typing import Any, Dict, List, Type, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="TaskIncomplete")


@_attrs_define
class TaskIncomplete:
    """
    Attributes:
        hash_ (str):
        count (int):
        uuids (List[str]):
    """

    hash_: str
    count: int
    uuids: List[str]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        hash_ = self.hash_
        count = self.count
        uuids = self.uuids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "hash": hash_,
                "count": count,
                "uuids": uuids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        hash_ = d.pop("hash")

        count = d.pop("count")

        uuids = cast(List[str], d.pop("uuids"))

        task_incomplete = cls(
            hash_=hash_,
            count=count,
            uuids=uuids,
        )

        task_incomplete.additional_properties = d
        return task_incomplete

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
