from typing import Any

from pydantic import model_validator
from sqlalchemy.orm import Session

from auth.router import CurrentUser
from mixin.exception import ApiError, ApiErrorCode
from mixin.schemas import BaseSchema
from resource_authorization import is_global_inventory
from user.models import association_users_to_projects

from .models import DomainModel


DOMAIN_TASK_OWNER_BINDING_KEY = "ownerBinding"


class DomainTaskOwnerBinding(BaseSchema):
    """REST task受付時のprincipalとVM ownerを固定する内部契約。"""

    model_config = BaseSchema.model_config | {"extra": "forbid"}

    principal_id: str
    owner_user_id: str | None = None
    owner_project_id: str | None = None

    @model_validator(mode="after")
    def validate_single_owner(self) -> "DomainTaskOwnerBinding":
        if (self.owner_user_id is None) == (self.owner_project_id is None):
            raise ValueError("VM task ownerはuserまたはProjectの一方だけが必要です")
        return self


class DomainTaskAuthorizationError(ValueError):
    """queue待機中にVM ownerまたはmembershipが変化した場合の拒否。"""


def domain_task_path_param(
    domain: DomainModel,
    principal_id: str,
) -> dict[str, Any]:
    """REST taskへ受付時のVM owner bindingを保存する。"""

    binding = DomainTaskOwnerBinding(
        principal_id=principal_id,
        owner_user_id=domain.owner_user_id,
        owner_project_id=domain.owner_project_id,
    )
    return {
        "uuid": domain.uuid,
        DOMAIN_TASK_OWNER_BINDING_KEY: binding.model_dump(
            mode="json",
            by_alias=True,
        ),
    }


def validate_locked_domain_task_authorization(
    db: Session,
    domain: DomainModel,
    *,
    task_user_id: str | None,
    path_param: Any,
) -> DomainTaskOwnerBinding:
    """Domain→Project lock取得後のownerとDB membershipを再認可する。"""

    if not isinstance(path_param, dict):
        raise DomainTaskAuthorizationError("VM task path parameterが不正です")
    try:
        binding = DomainTaskOwnerBinding.model_validate(
            path_param.get(DOMAIN_TASK_OWNER_BINDING_KEY),
        )
    except (TypeError, ValueError) as error:
        raise DomainTaskAuthorizationError(
            "VM task owner bindingがありません",
        ) from error

    if task_user_id is None or binding.principal_id != task_user_id:
        raise DomainTaskAuthorizationError(
            "VM task principalが受付時と一致しません",
        )
    if (
        domain.owner_user_id != binding.owner_user_id
        or domain.owner_project_id != binding.owner_project_id
    ):
        raise DomainTaskAuthorizationError(
            "VM ownerがtask受付時から変更されています",
        )

    if binding.owner_user_id is not None:
        if binding.owner_user_id != binding.principal_id:
            raise DomainTaskAuthorizationError(
                "個人VMのownerとtask principalが一致しません",
            )
        return binding

    membership = db.query(
        association_users_to_projects.c.user_id,
    ).filter(
        association_users_to_projects.c.user_id == binding.principal_id,
        association_users_to_projects.c.project_id == binding.owner_project_id,
    ).first()
    if membership is None:
        raise DomainTaskAuthorizationError(
            "VM owner Projectのmembershipが失効しています",
        )
    return binding


def can_access_domain(current_user: CurrentUser, domain: DomainModel) -> bool:
    """利用者本人またはJWTに残る所属ProjectだけにVMを公開する。"""
    return (
        domain.owner_user_id == current_user.id
        or (
            domain.owner_project_id is not None
            and domain.owner_project_id in current_user.projects
        )
    )


def get_authorized_domain(
    db: Session,
    uuid: str,
    current_user: CurrentUser,
    *,
    admin: bool = False,
) -> DomainModel:
    global_inventory = is_global_inventory(current_user, admin=admin)
    domain = db.query(DomainModel).filter(DomainModel.uuid == uuid).one_or_none()
    if domain is None:
        raise ApiError(404, ApiErrorCode.VM_NOT_FOUND, "The VM was not found.")
    if not global_inventory and not can_access_domain(current_user, domain):
        # resourceの存在自体を権限外のprincipalへ知らせない。
        raise ApiError(404, ApiErrorCode.VM_NOT_FOUND, "The VM was not found.")
    return domain
