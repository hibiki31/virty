from sqlalchemy.orm import Session

from auth.router import CurrentUser
from mixin.exception import ApiError, ApiErrorCode

from .models import DomainModel


def can_access_domain(current_user: CurrentUser, domain: DomainModel) -> bool:
    """利用者本人、所属project、または管理者だけにVMを公開する。"""
    return (
        current_user.verify_scope(["admin"], return_bool=True)
        or domain.owner_user_id == current_user.id
        or (
            domain.owner_project_id is not None
            and domain.owner_project_id in current_user.projects
        )
    )


def get_authorized_domain(
    db: Session,
    uuid: str,
    current_user: CurrentUser,
) -> DomainModel:
    domain = db.query(DomainModel).filter(DomainModel.uuid == uuid).one_or_none()
    if domain is None:
        raise ApiError(404, ApiErrorCode.VM_NOT_FOUND, "The VM was not found.")
    if not can_access_domain(current_user, domain):
        # resourceの存在自体を権限外のprincipalへ知らせない。
        raise ApiError(404, ApiErrorCode.VM_NOT_FOUND, "The VM was not found.")
    return domain
