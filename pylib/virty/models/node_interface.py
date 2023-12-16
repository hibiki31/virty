from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.node_interface_ipv_4_info import NodeInterfaceIpv4Info
    from ..models.node_interface_ipv_6_info import NodeInterfaceIpv6Info


T = TypeVar("T", bound="NodeInterface")


@_attrs_define
class NodeInterface:
    """
    Attributes:
        ifname (str):
        operstate (str):
        mtu (int):
        link_type (str):
        ipv_4_info (List['NodeInterfaceIpv4Info']):
        ipv_6_info (List['NodeInterfaceIpv6Info']):
        master (Union[Unset, str]):
        mac_address (Union[Unset, str]):
    """

    ifname: str
    operstate: str
    mtu: int
    link_type: str
    ipv_4_info: List["NodeInterfaceIpv4Info"]
    ipv_6_info: List["NodeInterfaceIpv6Info"]
    master: Union[Unset, str] = UNSET
    mac_address: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ifname = self.ifname
        operstate = self.operstate
        mtu = self.mtu
        link_type = self.link_type
        ipv_4_info = []
        for ipv_4_info_item_data in self.ipv_4_info:
            ipv_4_info_item = ipv_4_info_item_data.to_dict()

            ipv_4_info.append(ipv_4_info_item)

        ipv_6_info = []
        for ipv_6_info_item_data in self.ipv_6_info:
            ipv_6_info_item = ipv_6_info_item_data.to_dict()

            ipv_6_info.append(ipv_6_info_item)

        master = self.master
        mac_address = self.mac_address

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ifname": ifname,
                "operstate": operstate,
                "mtu": mtu,
                "linkType": link_type,
                "ipv4Info": ipv_4_info,
                "ipv6Info": ipv_6_info,
            }
        )
        if master is not UNSET:
            field_dict["master"] = master
        if mac_address is not UNSET:
            field_dict["macAddress"] = mac_address

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.node_interface_ipv_4_info import NodeInterfaceIpv4Info
        from ..models.node_interface_ipv_6_info import NodeInterfaceIpv6Info

        d = src_dict.copy()
        ifname = d.pop("ifname")

        operstate = d.pop("operstate")

        mtu = d.pop("mtu")

        link_type = d.pop("linkType")

        ipv_4_info = []
        _ipv_4_info = d.pop("ipv4Info")
        for ipv_4_info_item_data in _ipv_4_info:
            ipv_4_info_item = NodeInterfaceIpv4Info.from_dict(ipv_4_info_item_data)

            ipv_4_info.append(ipv_4_info_item)

        ipv_6_info = []
        _ipv_6_info = d.pop("ipv6Info")
        for ipv_6_info_item_data in _ipv_6_info:
            ipv_6_info_item = NodeInterfaceIpv6Info.from_dict(ipv_6_info_item_data)

            ipv_6_info.append(ipv_6_info_item)

        master = d.pop("master", UNSET)

        mac_address = d.pop("macAddress", UNSET)

        node_interface = cls(
            ifname=ifname,
            operstate=operstate,
            mtu=mtu,
            link_type=link_type,
            ipv_4_info=ipv_4_info,
            ipv_6_info=ipv_6_info,
            master=master,
            mac_address=mac_address,
        )

        node_interface.additional_properties = d
        return node_interface

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
