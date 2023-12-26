from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.domain_for_create_type import DomainForCreateType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cloud_init_insert import CloudInitInsert
    from ..models.domain_for_create_disk import DomainForCreateDisk
    from ..models.domain_for_create_interface import DomainForCreateInterface


T = TypeVar("T", bound="DomainForCreate")


@_attrs_define
class DomainForCreate:
    """
    Attributes:
        type (DomainForCreateType):
        name (str):
        node_name (str):
        memory_mega_byte (int):
        cpu (int):
        disks (List['DomainForCreateDisk']):
        interface (List['DomainForCreateInterface']):
        cloud_init (Union[Unset, CloudInitInsert]):
    """

    type: DomainForCreateType
    name: str
    node_name: str
    memory_mega_byte: int
    cpu: int
    disks: List["DomainForCreateDisk"]
    interface: List["DomainForCreateInterface"]
    cloud_init: Union[Unset, "CloudInitInsert"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        type = self.type.value

        name = self.name
        node_name = self.node_name
        memory_mega_byte = self.memory_mega_byte
        cpu = self.cpu
        disks = []
        for disks_item_data in self.disks:
            disks_item = disks_item_data.to_dict()

            disks.append(disks_item)

        interface = []
        for interface_item_data in self.interface:
            interface_item = interface_item_data.to_dict()

            interface.append(interface_item)

        cloud_init: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.cloud_init, Unset):
            cloud_init = self.cloud_init.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type,
                "name": name,
                "nodeName": node_name,
                "memoryMegaByte": memory_mega_byte,
                "cpu": cpu,
                "disks": disks,
                "interface": interface,
            }
        )
        if cloud_init is not UNSET:
            field_dict["cloudInit"] = cloud_init

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.cloud_init_insert import CloudInitInsert
        from ..models.domain_for_create_disk import DomainForCreateDisk
        from ..models.domain_for_create_interface import DomainForCreateInterface

        d = src_dict.copy()
        type = DomainForCreateType(d.pop("type"))

        name = d.pop("name")

        node_name = d.pop("nodeName")

        memory_mega_byte = d.pop("memoryMegaByte")

        cpu = d.pop("cpu")

        disks = []
        _disks = d.pop("disks")
        for disks_item_data in _disks:
            disks_item = DomainForCreateDisk.from_dict(disks_item_data)

            disks.append(disks_item)

        interface = []
        _interface = d.pop("interface")
        for interface_item_data in _interface:
            interface_item = DomainForCreateInterface.from_dict(interface_item_data)

            interface.append(interface_item)

        _cloud_init = d.pop("cloudInit", UNSET)
        cloud_init: Union[Unset, CloudInitInsert]
        if isinstance(_cloud_init, Unset):
            cloud_init = UNSET
        else:
            cloud_init = CloudInitInsert.from_dict(_cloud_init)

        domain_for_create = cls(
            type=type,
            name=name,
            node_name=node_name,
            memory_mega_byte=memory_mega_byte,
            cpu=cpu,
            disks=disks,
            interface=interface,
            cloud_init=cloud_init,
        )

        domain_for_create.additional_properties = d
        return domain_for_create

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
