from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.network import Network


T = TypeVar("T", bound="NetworkPage")


@_attrs_define
class NetworkPage:
    """
    Attributes:
        count (int):
        data (List['Network']):
    """

    count: int
    data: List["Network"]
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
        from ..models.network import Network

        d = src_dict.copy()
        count = d.pop("count")

        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = Network.from_dict(data_item_data)

            data.append(data_item)

        network_page = cls(
            count=count,
            data=data,
        )

        network_page.additional_properties = d
        return network_page

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
