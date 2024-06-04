from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.network_for_network_pool import NetworkForNetworkPool


T = TypeVar("T", bound="NetworkPoolPort")


@_attrs_define
class NetworkPoolPort:
    """
    Attributes:
        network (NetworkForNetworkPool):
        name (Union[Unset, str]):
        vlan_id (Union[None, Unset, int]):
    """

    network: "NetworkForNetworkPool"
    name: Union[Unset, str] = UNSET
    vlan_id: Union[None, Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        network = self.network.to_dict()

        name = self.name

        vlan_id: Union[None, Unset, int]
        if isinstance(self.vlan_id, Unset):
            vlan_id = UNSET
        else:
            vlan_id = self.vlan_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "network": network,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if vlan_id is not UNSET:
            field_dict["vlanId"] = vlan_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.network_for_network_pool import NetworkForNetworkPool

        d = src_dict.copy()
        network = NetworkForNetworkPool.from_dict(d.pop("network"))

        name = d.pop("name", UNSET)

        def _parse_vlan_id(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        vlan_id = _parse_vlan_id(d.pop("vlanId", UNSET))

        network_pool_port = cls(
            network=network,
            name=name,
            vlan_id=vlan_id,
        )

        network_pool_port.additional_properties = d
        return network_pool_port

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
