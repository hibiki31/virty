from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.user_project import UserProject
    from ..models.user_scope import UserScope


T = TypeVar("T", bound="User")


@_attrs_define
class User:
    """
    Attributes:
        username (str):
        scopes (List['UserScope']):
        projects (List['UserProject']):
    """

    username: str
    scopes: List["UserScope"]
    projects: List["UserProject"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        username = self.username

        scopes = []
        for scopes_item_data in self.scopes:
            scopes_item = scopes_item_data.to_dict()
            scopes.append(scopes_item)

        projects = []
        for projects_item_data in self.projects:
            projects_item = projects_item_data.to_dict()
            projects.append(projects_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "username": username,
                "scopes": scopes,
                "projects": projects,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.user_project import UserProject
        from ..models.user_scope import UserScope

        d = src_dict.copy()
        username = d.pop("username")

        scopes = []
        _scopes = d.pop("scopes")
        for scopes_item_data in _scopes:
            scopes_item = UserScope.from_dict(scopes_item_data)

            scopes.append(scopes_item)

        projects = []
        _projects = d.pop("projects")
        for projects_item_data in _projects:
            projects_item = UserProject.from_dict(projects_item_data)

            projects.append(projects_item)

        user = cls(
            username=username,
            scopes=scopes,
            projects=projects,
        )

        user.additional_properties = d
        return user

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
