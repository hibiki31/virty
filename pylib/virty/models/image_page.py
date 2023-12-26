from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.flavor import Flavor
    from ..models.image_domain import ImageDomain
    from ..models.storage_page import StoragePage


T = TypeVar("T", bound="ImagePage")


@_attrs_define
class ImagePage:
    """
    Attributes:
        name (str):
        capacity (int):
        storage (StoragePage):
        allocation (int):
        path (str):
        storage_uuid (Union[Unset, str]):
        flavor (Union[Unset, Flavor]):
        update_token (Union[Unset, str]):
        domain (Union[Unset, ImageDomain]):
    """

    name: str
    capacity: int
    storage: "StoragePage"
    allocation: int
    path: str
    storage_uuid: Union[Unset, str] = UNSET
    flavor: Union[Unset, "Flavor"] = UNSET
    update_token: Union[Unset, str] = UNSET
    domain: Union[Unset, "ImageDomain"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        capacity = self.capacity
        storage = self.storage.to_dict()

        allocation = self.allocation
        path = self.path
        storage_uuid = self.storage_uuid
        flavor: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.flavor, Unset):
            flavor = self.flavor.to_dict()

        update_token = self.update_token
        domain: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.domain, Unset):
            domain = self.domain.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "capacity": capacity,
                "storage": storage,
                "allocation": allocation,
                "path": path,
            }
        )
        if storage_uuid is not UNSET:
            field_dict["storageUuid"] = storage_uuid
        if flavor is not UNSET:
            field_dict["flavor"] = flavor
        if update_token is not UNSET:
            field_dict["updateToken"] = update_token
        if domain is not UNSET:
            field_dict["domain"] = domain

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.flavor import Flavor
        from ..models.image_domain import ImageDomain
        from ..models.storage_page import StoragePage

        d = src_dict.copy()
        name = d.pop("name")

        capacity = d.pop("capacity")

        storage = StoragePage.from_dict(d.pop("storage"))

        allocation = d.pop("allocation")

        path = d.pop("path")

        storage_uuid = d.pop("storageUuid", UNSET)

        _flavor = d.pop("flavor", UNSET)
        flavor: Union[Unset, Flavor]
        if isinstance(_flavor, Unset):
            flavor = UNSET
        else:
            flavor = Flavor.from_dict(_flavor)

        update_token = d.pop("updateToken", UNSET)

        _domain = d.pop("domain", UNSET)
        domain: Union[Unset, ImageDomain]
        if isinstance(_domain, Unset):
            domain = UNSET
        else:
            domain = ImageDomain.from_dict(_domain)

        image_page = cls(
            name=name,
            capacity=capacity,
            storage=storage,
            allocation=allocation,
            path=path,
            storage_uuid=storage_uuid,
            flavor=flavor,
            update_token=update_token,
            domain=domain,
        )

        image_page.additional_properties = d
        return image_page

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
