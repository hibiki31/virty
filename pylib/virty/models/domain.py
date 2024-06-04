from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.domain_drive import DomainDrive
    from ..models.domain_interface import DomainInterface
    from ..models.domain_project import DomainProject


T = TypeVar("T", bound="Domain")


@_attrs_define
class Domain:
    """
    Attributes:
        uuid (str):
        name (str):
        core (int):
        memory (int):
        status (int):
        node_name (str):
        description (Union[None, Unset, str]):
        owner_user_id (Union[None, Unset, str]):
        owner_project_id (Union[None, Unset, str]):
        owner_project (Union['DomainProject', None, Unset]):
        vnc_port (Union[None, Unset, int]):
        vnc_password (Union[None, Unset, str]):
        drives (Union[List['DomainDrive'], None, Unset]):
        interfaces (Union[List['DomainInterface'], None, Unset]):
    """

    uuid: str
    name: str
    core: int
    memory: int
    status: int
    node_name: str
    description: Union[None, Unset, str] = UNSET
    owner_user_id: Union[None, Unset, str] = UNSET
    owner_project_id: Union[None, Unset, str] = UNSET
    owner_project: Union["DomainProject", None, Unset] = UNSET
    vnc_port: Union[None, Unset, int] = UNSET
    vnc_password: Union[None, Unset, str] = UNSET
    drives: Union[List["DomainDrive"], None, Unset] = UNSET
    interfaces: Union[List["DomainInterface"], None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.domain_project import DomainProject

        uuid = self.uuid

        name = self.name

        core = self.core

        memory = self.memory

        status = self.status

        node_name = self.node_name

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        owner_user_id: Union[None, Unset, str]
        if isinstance(self.owner_user_id, Unset):
            owner_user_id = UNSET
        else:
            owner_user_id = self.owner_user_id

        owner_project_id: Union[None, Unset, str]
        if isinstance(self.owner_project_id, Unset):
            owner_project_id = UNSET
        else:
            owner_project_id = self.owner_project_id

        owner_project: Union[Dict[str, Any], None, Unset]
        if isinstance(self.owner_project, Unset):
            owner_project = UNSET
        elif isinstance(self.owner_project, DomainProject):
            owner_project = self.owner_project.to_dict()
        else:
            owner_project = self.owner_project

        vnc_port: Union[None, Unset, int]
        if isinstance(self.vnc_port, Unset):
            vnc_port = UNSET
        else:
            vnc_port = self.vnc_port

        vnc_password: Union[None, Unset, str]
        if isinstance(self.vnc_password, Unset):
            vnc_password = UNSET
        else:
            vnc_password = self.vnc_password

        drives: Union[List[Dict[str, Any]], None, Unset]
        if isinstance(self.drives, Unset):
            drives = UNSET
        elif isinstance(self.drives, list):
            drives = []
            for drives_type_0_item_data in self.drives:
                drives_type_0_item = drives_type_0_item_data.to_dict()
                drives.append(drives_type_0_item)

        else:
            drives = self.drives

        interfaces: Union[List[Dict[str, Any]], None, Unset]
        if isinstance(self.interfaces, Unset):
            interfaces = UNSET
        elif isinstance(self.interfaces, list):
            interfaces = []
            for interfaces_type_0_item_data in self.interfaces:
                interfaces_type_0_item = interfaces_type_0_item_data.to_dict()
                interfaces.append(interfaces_type_0_item)

        else:
            interfaces = self.interfaces

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

        d = src_dict.copy()
        uuid = d.pop("uuid")

        name = d.pop("name")

        core = d.pop("core")

        memory = d.pop("memory")

        status = d.pop("status")

        node_name = d.pop("nodeName")

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_owner_user_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        owner_user_id = _parse_owner_user_id(d.pop("ownerUserId", UNSET))

        def _parse_owner_project_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        owner_project_id = _parse_owner_project_id(d.pop("ownerProjectId", UNSET))

        def _parse_owner_project(data: object) -> Union["DomainProject", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                owner_project_type_0 = DomainProject.from_dict(data)

                return owner_project_type_0
            except:  # noqa: E722
                pass
            return cast(Union["DomainProject", None, Unset], data)

        owner_project = _parse_owner_project(d.pop("ownerProject", UNSET))

        def _parse_vnc_port(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        vnc_port = _parse_vnc_port(d.pop("vncPort", UNSET))

        def _parse_vnc_password(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        vnc_password = _parse_vnc_password(d.pop("vncPassword", UNSET))

        def _parse_drives(data: object) -> Union[List["DomainDrive"], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                drives_type_0 = []
                _drives_type_0 = data
                for drives_type_0_item_data in _drives_type_0:
                    drives_type_0_item = DomainDrive.from_dict(drives_type_0_item_data)

                    drives_type_0.append(drives_type_0_item)

                return drives_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List["DomainDrive"], None, Unset], data)

        drives = _parse_drives(d.pop("drives", UNSET))

        def _parse_interfaces(data: object) -> Union[List["DomainInterface"], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                interfaces_type_0 = []
                _interfaces_type_0 = data
                for interfaces_type_0_item_data in _interfaces_type_0:
                    interfaces_type_0_item = DomainInterface.from_dict(interfaces_type_0_item_data)

                    interfaces_type_0.append(interfaces_type_0_item)

                return interfaces_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List["DomainInterface"], None, Unset], data)

        interfaces = _parse_interfaces(d.pop("interfaces", UNSET))

        domain = cls(
            uuid=uuid,
            name=name,
            core=core,
            memory=memory,
            status=status,
            node_name=node_name,
            description=description,
            owner_user_id=owner_user_id,
            owner_project_id=owner_project_id,
            owner_project=owner_project,
            vnc_port=vnc_port,
            vnc_password=vnc_password,
            drives=drives,
            interfaces=interfaces,
        )

        domain.additional_properties = d
        return domain

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
