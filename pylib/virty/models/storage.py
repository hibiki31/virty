from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.node import Node
    from ..models.storage_metadata import StorageMetadata


T = TypeVar("T", bound="Storage")


@_attrs_define
class Storage:
    """
    Attributes:
        name (str):
        uuid (str):
        status (int):
        active (bool):
        node_name (str):
        node (Node):
        auto_start (bool):
        available (Union[None, Unset, int]):
        capacity (Union[None, Unset, int]):
        path (Union[None, Unset, str]):
        meta_data (Union['StorageMetadata', None, Unset]):
        update_token (Union[None, Unset, str]):
        allocation_commit (Union[None, Unset, int]):
        capacity_commit (Union[None, Unset, int]):
    """

    name: str
    uuid: str
    status: int
    active: bool
    node_name: str
    node: "Node"
    auto_start: bool
    available: Union[None, Unset, int] = UNSET
    capacity: Union[None, Unset, int] = UNSET
    path: Union[None, Unset, str] = UNSET
    meta_data: Union["StorageMetadata", None, Unset] = UNSET
    update_token: Union[None, Unset, str] = UNSET
    allocation_commit: Union[None, Unset, int] = UNSET
    capacity_commit: Union[None, Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.storage_metadata import StorageMetadata

        name = self.name

        uuid = self.uuid

        status = self.status

        active = self.active

        node_name = self.node_name

        node = self.node.to_dict()

        auto_start = self.auto_start

        available: Union[None, Unset, int]
        if isinstance(self.available, Unset):
            available = UNSET
        else:
            available = self.available

        capacity: Union[None, Unset, int]
        if isinstance(self.capacity, Unset):
            capacity = UNSET
        else:
            capacity = self.capacity

        path: Union[None, Unset, str]
        if isinstance(self.path, Unset):
            path = UNSET
        else:
            path = self.path

        meta_data: Union[Dict[str, Any], None, Unset]
        if isinstance(self.meta_data, Unset):
            meta_data = UNSET
        elif isinstance(self.meta_data, StorageMetadata):
            meta_data = self.meta_data.to_dict()
        else:
            meta_data = self.meta_data

        update_token: Union[None, Unset, str]
        if isinstance(self.update_token, Unset):
            update_token = UNSET
        else:
            update_token = self.update_token

        allocation_commit: Union[None, Unset, int]
        if isinstance(self.allocation_commit, Unset):
            allocation_commit = UNSET
        else:
            allocation_commit = self.allocation_commit

        capacity_commit: Union[None, Unset, int]
        if isinstance(self.capacity_commit, Unset):
            capacity_commit = UNSET
        else:
            capacity_commit = self.capacity_commit

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "uuid": uuid,
                "status": status,
                "active": active,
                "nodeName": node_name,
                "node": node,
                "autoStart": auto_start,
            }
        )
        if available is not UNSET:
            field_dict["available"] = available
        if capacity is not UNSET:
            field_dict["capacity"] = capacity
        if path is not UNSET:
            field_dict["path"] = path
        if meta_data is not UNSET:
            field_dict["metaData"] = meta_data
        if update_token is not UNSET:
            field_dict["updateToken"] = update_token
        if allocation_commit is not UNSET:
            field_dict["allocationCommit"] = allocation_commit
        if capacity_commit is not UNSET:
            field_dict["capacityCommit"] = capacity_commit

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.node import Node
        from ..models.storage_metadata import StorageMetadata

        d = src_dict.copy()
        name = d.pop("name")

        uuid = d.pop("uuid")

        status = d.pop("status")

        active = d.pop("active")

        node_name = d.pop("nodeName")

        node = Node.from_dict(d.pop("node"))

        auto_start = d.pop("autoStart")

        def _parse_available(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        available = _parse_available(d.pop("available", UNSET))

        def _parse_capacity(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        capacity = _parse_capacity(d.pop("capacity", UNSET))

        def _parse_path(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        path = _parse_path(d.pop("path", UNSET))

        def _parse_meta_data(data: object) -> Union["StorageMetadata", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                meta_data_type_0 = StorageMetadata.from_dict(data)

                return meta_data_type_0
            except:  # noqa: E722
                pass
            return cast(Union["StorageMetadata", None, Unset], data)

        meta_data = _parse_meta_data(d.pop("metaData", UNSET))

        def _parse_update_token(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        update_token = _parse_update_token(d.pop("updateToken", UNSET))

        def _parse_allocation_commit(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        allocation_commit = _parse_allocation_commit(d.pop("allocationCommit", UNSET))

        def _parse_capacity_commit(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        capacity_commit = _parse_capacity_commit(d.pop("capacityCommit", UNSET))

        storage = cls(
            name=name,
            uuid=uuid,
            status=status,
            active=active,
            node_name=node_name,
            node=node,
            auto_start=auto_start,
            available=available,
            capacity=capacity,
            path=path,
            meta_data=meta_data,
            update_token=update_token,
            allocation_commit=allocation_commit,
            capacity_commit=capacity_commit,
        )

        storage.additional_properties = d
        return storage

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
