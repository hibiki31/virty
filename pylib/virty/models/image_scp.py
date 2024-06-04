from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ImageSCP")


@_attrs_define
class ImageSCP:
    """
    Attributes:
        from_node_name (str):
        to_node_name (str):
        from_file_path (str):
        to_file_path (str):
    """

    from_node_name: str
    to_node_name: str
    from_file_path: str
    to_file_path: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from_node_name = self.from_node_name

        to_node_name = self.to_node_name

        from_file_path = self.from_file_path

        to_file_path = self.to_file_path

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fromNodeName": from_node_name,
                "toNodeName": to_node_name,
                "fromFilePath": from_file_path,
                "toFilePath": to_file_path,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        from_node_name = d.pop("fromNodeName")

        to_node_name = d.pop("toNodeName")

        from_file_path = d.pop("fromFilePath")

        to_file_path = d.pop("toFilePath")

        image_scp = cls(
            from_node_name=from_node_name,
            to_node_name=to_node_name,
            from_file_path=from_file_path,
            to_file_path=to_file_path,
        )

        image_scp.additional_properties = d
        return image_scp

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
