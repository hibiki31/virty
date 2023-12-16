from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.node_page import NodePage
    from ..models.storage_metadata import StorageMetadata


T = TypeVar("T", bound="StoragePage")


@_attrs_define
class StoragePage:
    """
    Attributes:
        name (str):
        uuid (str):
        status (int):
        active (bool):
        node_name (str):
        node (NodePage):
        auto_start (bool):
        available (Union[Unset, int]):
        capacity (Union[Unset, int]):
        path (Union[Unset, str]):
        meta_data (Union[Unset, StorageMetadata]):
        update_token (Union[Unset, str]):
        allocation_commit (Union[Unset, int]):
        capacity_commit (Union[Unset, int]):
    """

    name: str
    uuid: str
    status: int
    active: bool
    node_name: str
    node: "NodePage"
    auto_start: bool
    available: Union[Unset, int] = UNSET
    capacity: Union[Unset, int] = UNSET
    path: Union[Unset, str] = UNSET
    meta_data: Union[Unset, "StorageMetadata"] = UNSET
    update_token: Union[Unset, str] = UNSET
    allocation_commit: Union[Unset, int] = UNSET
    capacity_commit: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        uuid = self.uuid
        status = self.status
        active = self.active
        node_name = self.node_name
        node = self.node.to_dict()

        auto_start = self.auto_start
        available = self.available
        capacity = self.capacity
        path = self.path
        meta_data: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.meta_data, Unset):
            meta_data = self.meta_data.to_dict()

        update_token = self.update_token
        allocation_commit = self.allocation_commit
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
        from ..models.node_page import NodePage
        from ..models.storage_metadata import StorageMetadata

        d = src_dict.copy()
        name = d.pop("name")

        uuid = d.pop("uuid")

        status = d.pop("status")

        active = d.pop("active")

        node_name = d.pop("nodeName")

        node = NodePage.from_dict(d.pop("node"))

        auto_start = d.pop("autoStart")

        available = d.pop("available", UNSET)

        capacity = d.pop("capacity", UNSET)

        path = d.pop("path", UNSET)

        _meta_data = d.pop("metaData", UNSET)
        meta_data: Union[Unset, StorageMetadata]
        if isinstance(_meta_data, Unset):
            meta_data = UNSET
        else:
            meta_data = StorageMetadata.from_dict(_meta_data)

        update_token = d.pop("updateToken", UNSET)

        allocation_commit = d.pop("allocationCommit", UNSET)

        capacity_commit = d.pop("capacityCommit", UNSET)

        storage_page = cls(
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

        storage_page.additional_properties = d
        return storage_page

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
