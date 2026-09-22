import pytest
from pydantic import ValidationError

from domain.authorization import DomainTaskOwnerBinding


@pytest.mark.parametrize("admin", [False, True])
@pytest.mark.parametrize(
    ("owner_user_id", "owner_project_id"),
    [(None, None), ("owner", None), (None, "abc123"), ("owner", "abc123")],
)
def test_task_owner_binding_only_allows_ownerless_admin(
    admin: bool,
    owner_user_id: str | None,
    owner_project_id: str | None,
) -> None:
    values = {
        "principalId": "actor",
        "ownerUserId": owner_user_id,
        "ownerProjectId": owner_project_id,
        "admin": admin,
    }
    dual_owner = owner_user_id is not None and owner_project_id is not None
    missing_owner = owner_user_id is None and owner_project_id is None
    if dual_owner or (missing_owner and not admin):
        with pytest.raises(ValidationError):
            DomainTaskOwnerBinding.model_validate(values)
    else:
        binding = DomainTaskOwnerBinding.model_validate(values)
        assert binding.model_dump(mode="json", by_alias=True) == values
