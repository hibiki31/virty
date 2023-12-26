from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.domain_drive import DomainDrive
    from ..models.domain_interface import DomainInterface
    from ..models.domain_project import DomainProject
    from ..models.node import Node


T = TypeVar("T", bound="DomainDetail")


@_attrs_define
class DomainDetail:
    """
    Attributes:
        uuid (str):
        name (str):
        core (int):
        memory (int):
        status (int):
        node_name (str):
        node (Node):
        description (Union[Unset, str]):
        owner_user_id (Union[Unset, str]):
        owner_project_id (Union[Unset, str]):
        owner_project (Union[Unset, DomainProject]):
        vnc_port (Union[Unset, int]):
        vnc_password (Union[Unset, str]):
        drives (Union[Unset, List['DomainDrive']]):
        interfaces (Union[Unset, List['DomainInterface']]):
    """

    uuid: str
    name: str
    core: int
    memory: int
    status: int
    node_name: str
    node: "Node"
    description: Union[Unset, str] = UNSET
    owner_user_id: Union[Unset, str] = UNSET
    owner_project_id: Union[Unset, str] = UNSET
    owner_project: Union[Unset, "DomainProject"] = UNSET
    vnc_port: Union[Unset, int] = UNSET
    vnc_password: Union[Unset, str] = UNSET
    drives: Union[Unset, List["DomainDrive"]] = UNSET
    interfaces: Union[Unset, List["DomainInterface"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        uuid = self.uuid
        name = self.name
        core = self.core
        memory = self.memory
        status = self.status
        node_name = self.node_name
        node = self.node.to_dict()

        description = self.description
        owner_user_id = self.owner_user_id
        owner_project_id = self.owner_project_id
        owner_project: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.owner_project, Unset):
            owner_project = self.owner_project.to_dict()

        vnc_port = self.vnc_port
        vnc_password = self.vnc_password
        drives: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.drives, Unset):
            drives = []
            for drives_item_data in self.drives:
                drives_item = drives_item_data.to_dict()

                drives.append(drives_item)

        interfaces: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.interfaces, Unset):
            interfaces = []
            for interfaces_item_data in self.interfaces:
                interfaces_item = interfaces_item_data.to_dict()

                interfaces.append(interfaces_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "uuid": uuid,
                "name": name,
                "core": core,
                "memory": memory,
                "status": status,
                "nodeName": node_name,
                "node": node,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if owner_user_id is not UNSET:
            field_dict["ownerUserId"] = owner_user_id
        if owner_project_id is not UNSET:
            field_dict["ownerProjectId"] = owner_project_id
        if owner_project is not UNSET:
            field_dict["ownerProject"] = owner_project
        if vnc_port is not UNSET:
            field_dict["vncPort"] = vnc_port
        if vnc_password is not UNSET:
            field_dict["vncPassword"] = vnc_password
        if drives is not UNSET:
            field_dict["drives"] = drives
        if interfaces is not UNSET:
            field_dict["interfaces"] = interfaces

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.domain_drive import DomainDrive
        from ..models.domain_interface import DomainInterface
        from ..models.domain_project import DomainProject
        from ..models.node import Node

        d = src_dict.copy()
        uuid = d.pop("uuid")

        name = d.pop("name")

        core = d.pop("core")

        memory = d.pop("memory")

        status = d.pop("status")

        node_name = d.pop("nodeName")

        node = Node.from_dict(d.pop("node"))

        description = d.pop("description", UNSET)

        owner_user_id = d.pop("ownerUserId", UNSET)

        owner_project_id = d.pop("ownerProjectId", UNSET)

        _owner_project = d.pop("ownerProject", UNSET)
        owner_project: Union[Unset, DomainProject]
        if isinstance(_owner_project, Unset):
            owner_project = UNSET
        else:
            owner_project = DomainProject.from_dict(_owner_project)

        vnc_port = d.pop("vncPort", UNSET)

        vnc_password = d.pop("vncPassword", UNSET)

        drives = []
        _drives = d.pop("drives", UNSET)
        for drives_item_data in _drives or []:
            drives_item = DomainDrive.from_dict(drives_item_data)

            drives.append(drives_item)

        interfaces = []
        _interfaces = d.pop("interfaces", UNSET)
        for interfaces_item_data in _interfaces or []:
            interfaces_item = DomainInterface.from_dict(interfaces_item_data)

            interfaces.append(interfaces_item)

        domain_detail = cls(
            uuid=uuid,
            name=name,
            core=core,
            memory=memory,
            status=status,
            node_name=node_name,
            node=node,
            description=description,
            owner_user_id=owner_user_id,
            owner_project_id=owner_project_id,
            owner_project=owner_project,
            vnc_port=vnc_port,
            vnc_password=vnc_password,
            drives=drives,
            interfaces=interfaces,
        )

        domain_detail.additional_properties = d
        return domain_detail

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
