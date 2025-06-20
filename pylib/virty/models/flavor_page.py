from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.flavor import Flavor


T = TypeVar("T", bound="FlavorPage")


@_attrs_define
class FlavorPage:
    """
    Attributes:
        count (int):
        data (List['Flavor']):
    """

    count: int
    data: List["Flavor"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        count = self.count

        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "count": count,
                "data": data,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.flavor import Flavor

        d = src_dict.copy()
        count = d.pop("count")

        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = Flavor.from_dict(data_item_data)

            data.append(data_item)

        flavor_page = cls(
            count=count,
            data=data,
        )

        flavor_page.additional_properties = d
        return flavor_page

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
