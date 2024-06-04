from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="NetworkPoolForUpdate")


@_attrs_define
class NetworkPoolForUpdate:
    """
    Attributes:
        pool_id (int):
        network_uuid (str):
        port_name (Union[None, Unset, str]):
    """

    pool_id: int
    network_uuid: str
    port_name: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pool_id = self.pool_id

        network_uuid = self.network_uuid

        port_name: Union[None, Unset, str]
        if isinstance(self.port_name, Unset):
            port_name = UNSET
        else:
            port_name = self.port_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "poolId": pool_id,
                "networkUuid": network_uuid,
            }
        )
        if port_name is not UNSET:
            field_dict["portName"] = port_name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        pool_id = d.pop("poolId")

        network_uuid = d.pop("networkUuid")

        def _parse_port_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        port_name = _parse_port_name(d.pop("portName", UNSET))

        network_pool_for_update = cls(
            pool_id=pool_id,
            network_uuid=network_uuid,
            port_name=port_name,
        )

        network_pool_for_update.additional_properties = d
        return network_pool_for_update

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
