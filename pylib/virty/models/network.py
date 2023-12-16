from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.network_portgroup import NetworkPortgroup


T = TypeVar("T", bound="Network")


@_attrs_define
class Network:
    """
    Attributes:
        name (str):
        uuid (str):
        type (str):
        portgroups (List['NetworkPortgroup']):
        node_name (str):
        dhcp (Union[Unset, bool]):
        description (Union[Unset, str]):
        active (Union[Unset, bool]):
        bridge (Union[Unset, str]):
        auto_start (Union[Unset, bool]):
        update_token (Union[Unset, str]):
    """

    name: str
    uuid: str
    type: str
    portgroups: List["NetworkPortgroup"]
    node_name: str
    dhcp: Union[Unset, bool] = UNSET
    description: Union[Unset, str] = UNSET
    active: Union[Unset, bool] = UNSET
    bridge: Union[Unset, str] = UNSET
    auto_start: Union[Unset, bool] = UNSET
    update_token: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        uuid = self.uuid
        type = self.type
        portgroups = []
        for portgroups_item_data in self.portgroups:
            portgroups_item = portgroups_item_data.to_dict()

            portgroups.append(portgroups_item)

        node_name = self.node_name
        dhcp = self.dhcp
        description = self.description
        active = self.active
        bridge = self.bridge
        auto_start = self.auto_start
        update_token = self.update_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "uuid": uuid,
                "type": type,
                "portgroups": portgroups,
                "nodeName": node_name,
            }
        )
        if dhcp is not UNSET:
            field_dict["dhcp"] = dhcp
        if description is not UNSET:
            field_dict["description"] = description
        if active is not UNSET:
            field_dict["active"] = active
        if bridge is not UNSET:
            field_dict["bridge"] = bridge
        if auto_start is not UNSET:
            field_dict["autoStart"] = auto_start
        if update_token is not UNSET:
            field_dict["updateToken"] = update_token

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.network_portgroup import NetworkPortgroup

        d = src_dict.copy()
        name = d.pop("name")

        uuid = d.pop("uuid")

        type = d.pop("type")

        portgroups = []
        _portgroups = d.pop("portgroups")
        for portgroups_item_data in _portgroups:
            portgroups_item = NetworkPortgroup.from_dict(portgroups_item_data)

            portgroups.append(portgroups_item)

        node_name = d.pop("nodeName")

        dhcp = d.pop("dhcp", UNSET)

        description = d.pop("description", UNSET)

        active = d.pop("active", UNSET)

        bridge = d.pop("bridge", UNSET)

        auto_start = d.pop("autoStart", UNSET)

        update_token = d.pop("updateToken", UNSET)

        network = cls(
            name=name,
            uuid=uuid,
            type=type,
            portgroups=portgroups,
            node_name=node_name,
            dhcp=dhcp,
            description=description,
            active=active,
            bridge=bridge,
            auto_start=auto_start,
            update_token=update_token,
        )

        network.additional_properties = d
        return network

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
