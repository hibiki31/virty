from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.flavor import Flavor
    from ..models.image_domain import ImageDomain
    from ..models.storage import Storage


T = TypeVar("T", bound="Image")


@_attrs_define
class Image:
    """
    Attributes:
        name (str):
        capacity (int):
        storage (Storage):
        allocation (int):
        path (str):
        storage_uuid (Union[None, Unset, str]):
        flavor (Union['Flavor', None, Unset]):
        update_token (Union[None, Unset, str]):
        domain (Union['ImageDomain', None, Unset]):
    """

    name: str
    capacity: int
    storage: "Storage"
    allocation: int
    path: str
    storage_uuid: Union[None, Unset, str] = UNSET
    flavor: Union["Flavor", None, Unset] = UNSET
    update_token: Union[None, Unset, str] = UNSET
    domain: Union["ImageDomain", None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.flavor import Flavor
        from ..models.image_domain import ImageDomain

        name = self.name

        capacity = self.capacity

        storage = self.storage.to_dict()

        allocation = self.allocation

        path = self.path

        storage_uuid: Union[None, Unset, str]
        if isinstance(self.storage_uuid, Unset):
            storage_uuid = UNSET
        else:
            storage_uuid = self.storage_uuid

        flavor: Union[Dict[str, Any], None, Unset]
        if isinstance(self.flavor, Unset):
            flavor = UNSET
        elif isinstance(self.flavor, Flavor):
            flavor = self.flavor.to_dict()
        else:
            flavor = self.flavor

        update_token: Union[None, Unset, str]
        if isinstance(self.update_token, Unset):
            update_token = UNSET
        else:
            update_token = self.update_token

        domain: Union[Dict[str, Any], None, Unset]
        if isinstance(self.domain, Unset):
            domain = UNSET
        elif isinstance(self.domain, ImageDomain):
            domain = self.domain.to_dict()
        else:
            domain = self.domain

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
        from ..models.storage import Storage

        d = src_dict.copy()
        name = d.pop("name")

        capacity = d.pop("capacity")

        storage = Storage.from_dict(d.pop("storage"))

        allocation = d.pop("allocation")

        path = d.pop("path")

        def _parse_storage_uuid(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        storage_uuid = _parse_storage_uuid(d.pop("storageUuid", UNSET))

        def _parse_flavor(data: object) -> Union["Flavor", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                flavor_type_0 = Flavor.from_dict(data)

                return flavor_type_0
            except:  # noqa: E722
                pass
            return cast(Union["Flavor", None, Unset], data)

        flavor = _parse_flavor(d.pop("flavor", UNSET))

        def _parse_update_token(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        update_token = _parse_update_token(d.pop("updateToken", UNSET))

        def _parse_domain(data: object) -> Union["ImageDomain", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                domain_type_0 = ImageDomain.from_dict(data)

                return domain_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ImageDomain", None, Unset], data)

        domain = _parse_domain(d.pop("domain", UNSET))

        image = cls(
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

        image.additional_properties = d
        return image

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
