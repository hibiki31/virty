from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

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
        id (Union[None, Unset, int]):
        name (Union[None, Unset, str]):
        networks (Union[List['NetworkForNetworkPool'], None, Unset]):
        ports (Union[List['NetworkPoolPort'], None, Unset]):
    """

    id: Union[None, Unset, int] = UNSET
    name: Union[None, Unset, str] = UNSET
    networks: Union[List["NetworkForNetworkPool"], None, Unset] = UNSET
    ports: Union[List["NetworkPoolPort"], None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id: Union[None, Unset, int]
        if isinstance(self.id, Unset):
            id = UNSET
        else:
            id = self.id

        name: Union[None, Unset, str]
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        networks: Union[List[Dict[str, Any]], None, Unset]
        if isinstance(self.networks, Unset):
            networks = UNSET
        elif isinstance(self.networks, list):
            networks = []
            for networks_type_0_item_data in self.networks:
                networks_type_0_item = networks_type_0_item_data.to_dict()
                networks.append(networks_type_0_item)

        else:
            networks = self.networks

        ports: Union[List[Dict[str, Any]], None, Unset]
        if isinstance(self.ports, Unset):
            ports = UNSET
        elif isinstance(self.ports, list):
            ports = []
            for ports_type_0_item_data in self.ports:
                ports_type_0_item = ports_type_0_item_data.to_dict()
                ports.append(ports_type_0_item)

        else:
            ports = self.ports

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

        def _parse_id(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        id = _parse_id(d.pop("id", UNSET))

        def _parse_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_networks(data: object) -> Union[List["NetworkForNetworkPool"], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                networks_type_0 = []
                _networks_type_0 = data
                for networks_type_0_item_data in _networks_type_0:
                    networks_type_0_item = NetworkForNetworkPool.from_dict(networks_type_0_item_data)

                    networks_type_0.append(networks_type_0_item)

                return networks_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List["NetworkForNetworkPool"], None, Unset], data)

        networks = _parse_networks(d.pop("networks", UNSET))

        def _parse_ports(data: object) -> Union[List["NetworkPoolPort"], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                ports_type_0 = []
                _ports_type_0 = data
                for ports_type_0_item_data in _ports_type_0:
                    ports_type_0_item = NetworkPoolPort.from_dict(ports_type_0_item_data)

                    ports_type_0.append(ports_type_0_item)

                return ports_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List["NetworkPoolPort"], None, Unset], data)

        ports = _parse_ports(d.pop("ports", UNSET))

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
