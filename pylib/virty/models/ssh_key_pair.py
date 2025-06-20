from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="SSHKeyPair")


@_attrs_define
class SSHKeyPair:
    """
    Attributes:
        private_key (str):
        public_key (str):
    """

    private_key: str
    public_key: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        private_key = self.private_key

        public_key = self.public_key

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "privateKey": private_key,
                "publicKey": public_key,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        private_key = d.pop("privateKey")

        public_key = d.pop("publicKey")

        ssh_key_pair = cls(
            private_key=private_key,
            public_key=public_key,
        )

        ssh_key_pair.additional_properties = d
        return ssh_key_pair

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
