from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.network_for_network_pool import NetworkForNetworkPool
    from ..models.network_pool_port import NetworkPoolPort


T = TypeVar("T", bound="NetworkPool")


@_attrs_define
class NetworkPool:
    """
    Attributes:
        id (Union[Unset, int]):
        name (Union[Unset, str]):
        networks (Union[Unset, List['NetworkForNetworkPool']]):
        ports (Union[Unset, List['NetworkPoolPort']]):
    """

    id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    networks: Union[Unset, List["NetworkForNetworkPool"]] = UNSET
    ports: Union[Unset, List["NetworkPoolPort"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        name = self.name
        networks: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.networks, Unset):
            networks = []
            for networks_item_data in self.networks:
                networks_item = networks_item_data.to_dict()

                networks.append(networks_item)

        ports: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.ports, Unset):
            ports = []
            for ports_item_data in self.ports:
                ports_item = ports_item_data.to_dict()

                ports.append(ports_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if networks is not UNSET:
            field_dict["networks"] = networks
        if ports is not UNSET:
            field_dict["ports"] = ports

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.network_for_network_pool import NetworkForNetworkPool
        from ..models.network_pool_port import NetworkPoolPort

        d = src_dict.copy()
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        networks = []
        _networks = d.pop("networks", UNSET)
        for networks_item_data in _networks or []:
            networks_item = NetworkForNetworkPool.from_dict(networks_item_data)

            networks.append(networks_item)

        ports = []
        _ports = d.pop("ports", UNSET)
        for ports_item_data in _ports or []:
            ports_item = NetworkPoolPort.from_dict(ports_item_data)

            ports.append(ports_item)

        network_pool = cls(
            id=id,
            name=name,
            networks=networks,
            ports=ports,
        )

        network_pool.additional_properties = d
        return network_pool

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
