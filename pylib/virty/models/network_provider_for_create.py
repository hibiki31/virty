from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="NetworkProviderForCreate")


@_attrs_define
class NetworkProviderForCreate:
    """
    Attributes:
        name (Union[None, Unset, str]):
        dns_domain (Union[None, Unset, str]):
        network_address (Union[None, Unset, str]):
        network_prefix (Union[None, Unset, str]):
        gateway_address (Union[None, Unset, str]):
        dhcp_start (Union[None, Unset, str]):
        dhcp_end (Union[None, Unset, str]):
        network_node (Union[None, Unset, str]):
    """

    name: Union[None, Unset, str] = UNSET
    dns_domain: Union[None, Unset, str] = UNSET
    network_address: Union[None, Unset, str] = UNSET
    network_prefix: Union[None, Unset, str] = UNSET
    gateway_address: Union[None, Unset, str] = UNSET
    dhcp_start: Union[None, Unset, str] = UNSET
    dhcp_end: Union[None, Unset, str] = UNSET
    network_node: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name: Union[None, Unset, str]
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        dns_domain: Union[None, Unset, str]
        if isinstance(self.dns_domain, Unset):
            dns_domain = UNSET
        else:
            dns_domain = self.dns_domain

        network_address: Union[None, Unset, str]
        if isinstance(self.network_address, Unset):
            network_address = UNSET
        else:
            network_address = self.network_address

        network_prefix: Union[None, Unset, str]
        if isinstance(self.network_prefix, Unset):
            network_prefix = UNSET
        else:
            network_prefix = self.network_prefix

        gateway_address: Union[None, Unset, str]
        if isinstance(self.gateway_address, Unset):
            gateway_address = UNSET
        else:
            gateway_address = self.gateway_address

        dhcp_start: Union[None, Unset, str]
        if isinstance(self.dhcp_start, Unset):
            dhcp_start = UNSET
        else:
            dhcp_start = self.dhcp_start

        dhcp_end: Union[None, Unset, str]
        if isinstance(self.dhcp_end, Unset):
            dhcp_end = UNSET
        else:
            dhcp_end = self.dhcp_end

        network_node: Union[None, Unset, str]
        if isinstance(self.network_node, Unset):
            network_node = UNSET
        else:
            network_node = self.network_node

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if dns_domain is not UNSET:
            field_dict["dnsDomain"] = dns_domain
        if network_address is not UNSET:
            field_dict["networkAddress"] = network_address
        if network_prefix is not UNSET:
            field_dict["networkPrefix"] = network_prefix
        if gateway_address is not UNSET:
            field_dict["gatewayAddress"] = gateway_address
        if dhcp_start is not UNSET:
            field_dict["dhcpStart"] = dhcp_start
        if dhcp_end is not UNSET:
            field_dict["dhcpEnd"] = dhcp_end
        if network_node is not UNSET:
            field_dict["networkNode"] = network_node

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def _parse_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_dns_domain(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        dns_domain = _parse_dns_domain(d.pop("dnsDomain", UNSET))

        def _parse_network_address(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        network_address = _parse_network_address(d.pop("networkAddress", UNSET))

        def _parse_network_prefix(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        network_prefix = _parse_network_prefix(d.pop("networkPrefix", UNSET))

        def _parse_gateway_address(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        gateway_address = _parse_gateway_address(d.pop("gatewayAddress", UNSET))

        def _parse_dhcp_start(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        dhcp_start = _parse_dhcp_start(d.pop("dhcpStart", UNSET))

        def _parse_dhcp_end(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        dhcp_end = _parse_dhcp_end(d.pop("dhcpEnd", UNSET))

        def _parse_network_node(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        network_node = _parse_network_node(d.pop("networkNode", UNSET))

        network_provider_for_create = cls(
            name=name,
            dns_domain=dns_domain,
            network_address=network_address,
            network_prefix=network_prefix,
            gateway_address=gateway_address,
            dhcp_start=dhcp_start,
            dhcp_end=dhcp_end,
            network_node=network_node,
        )

        network_provider_for_create.additional_properties = d
        return network_provider_for_create

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
