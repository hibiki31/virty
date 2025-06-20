from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.storage_for_storage_container import StorageForStorageContainer


T = TypeVar("T", bound="StorageContainerForStoragePool")


@_attrs_define
class StorageContainerForStoragePool:
    """
    Attributes:
        storage (StorageForStorageContainer):
    """

    storage: "StorageForStorageContainer"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        storage = self.storage.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "storage": storage,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.storage_for_storage_container import StorageForStorageContainer

        d = src_dict.copy()
        storage = StorageForStorageContainer.from_dict(d.pop("storage"))

        storage_container_for_storage_pool = cls(
            storage=storage,
        )

        storage_container_for_storage_pool.additional_properties = d
        return storage_container_for_storage_pool

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
