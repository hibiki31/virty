from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.storage_container_for_storage_pool import StorageContainerForStoragePool


T = TypeVar("T", bound="StoragePool")


@_attrs_define
class StoragePool:
    """
    Attributes:
        id (int):
        name (str):
        storages (List['StorageContainerForStoragePool']):
    """

    id: int
    name: str
    storages: List["StorageContainerForStoragePool"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        name = self.name

        storages = []
        for storages_item_data in self.storages:
            storages_item = storages_item_data.to_dict()
            storages.append(storages_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "storages": storages,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.storage_container_for_storage_pool import StorageContainerForStoragePool

        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        storages = []
        _storages = d.pop("storages")
        for storages_item_data in _storages:
            storages_item = StorageContainerForStoragePool.from_dict(storages_item_data)

            storages.append(storages_item)

        storage_pool = cls(
            id=id,
            name=name,
            storages=storages,
        )

        storage_pool.additional_properties = d
        return storage_pool

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
