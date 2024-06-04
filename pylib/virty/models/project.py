from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.project_user import ProjectUser


T = TypeVar("T", bound="Project")


@_attrs_define
class Project:
    """
    Attributes:
        id (str):
        name (str):
        memory_g (int):
        core (int):
        storage_capacity_g (int):
        users (List['ProjectUser']):
        used_memory_g (int):
        used_core (int):
        network_pools (Any):
        storage_pools (Any):
    """

    id: str
    name: str
    memory_g: int
    core: int
    storage_capacity_g: int
    users: List["ProjectUser"]
    used_memory_g: int
    used_core: int
    network_pools: Any
    storage_pools: Any
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        name = self.name

        memory_g = self.memory_g

        core = self.core

        storage_capacity_g = self.storage_capacity_g

        users = []
        for users_item_data in self.users:
            users_item = users_item_data.to_dict()
            users.append(users_item)

        used_memory_g = self.used_memory_g

        used_core = self.used_core

        network_pools = self.network_pools

        storage_pools = self.storage_pools

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "memoryG": memory_g,
                "core": core,
                "storageCapacityG": storage_capacity_g,
                "users": users,
                "usedMemoryG": used_memory_g,
                "usedCore": used_core,
                "networkPools": network_pools,
                "storagePools": storage_pools,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.project_user import ProjectUser

        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        memory_g = d.pop("memoryG")

        core = d.pop("core")

        storage_capacity_g = d.pop("storageCapacityG")

        users = []
        _users = d.pop("users")
        for users_item_data in _users:
            users_item = ProjectUser.from_dict(users_item_data)

            users.append(users_item)

        used_memory_g = d.pop("usedMemoryG")

        used_core = d.pop("usedCore")

        network_pools = d.pop("networkPools")

        storage_pools = d.pop("storagePools")

        project = cls(
            id=id,
            name=name,
            memory_g=memory_g,
            core=core,
            storage_capacity_g=storage_capacity_g,
            users=users,
            used_memory_g=used_memory_g,
            used_core=used_core,
            network_pools=network_pools,
            storage_pools=storage_pools,
        )

        project.additional_properties = d
        return project

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
