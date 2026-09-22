"""VM owner Project変更とresource変更の直列化service。"""

from collections.abc import Callable, Iterable

from sqlalchemy.orm import Session

from project.models import ProjectModel
from resource_authorization import domain_project_resource_conflicts

from .models import DomainModel


class DomainProjectMoveError(ValueError):
    """VM Project移動でclientへ安全に返せる検証エラー。"""


class DomainProjectMoveNotFoundError(DomainProjectMoveError):
    pass


class DomainProjectMoveConflictError(DomainProjectMoveError):
    def __init__(self, conflicts: list[str]) -> None:
        super().__init__("移動先ProjectへgrantされていないVM resourceがあります")
        self.conflicts = conflicts


def lock_domain_owner_context(
    db: Session,
    domain_uuid: str,
    *,
    additional_project_ids: Iterable[str] = (),
) -> DomainModel:
    """Domain、owner/追加Projectの順で固定し、最新inventoryを返す。

    Domainを先頭にし、ProjectはID順に固定する。この順序をVM移動、CD-ROM、
    network変更、resource削除で共有し、source/destinationの並びに依存する
    deadlockと、Project lock待ち中にownerが変わった後の古い認可を防ぐ。
    """

    domain = (
        db.query(DomainModel)
        .filter(DomainModel.uuid == domain_uuid)
        .populate_existing()
        .with_for_update()
        .one_or_none()
    )
    if domain is None:
        raise DomainProjectMoveNotFoundError("VMが見つかりません")

    required_project_ids = set(additional_project_ids)
    project_ids = set(required_project_ids)
    if domain.owner_project_id is not None:
        project_ids.add(domain.owner_project_id)

    locked_project_ids = {
        str(project_id)
        for (project_id,) in (
            db.query(ProjectModel.id)
            .filter(ProjectModel.id.in_(sorted(project_ids)))
            .order_by(ProjectModel.id)
            .with_for_update()
            .all()
        )
    } if project_ids else set()
    if not required_project_ids.issubset(locked_project_ids):
        raise DomainProjectMoveNotFoundError("移動先Projectが見つかりません")
    if (
        domain.owner_project_id is not None
        and domain.owner_project_id not in locked_project_ids
    ):
        raise DomainProjectMoveConflictError([
            f"project:{domain.owner_project_id}",
        ])

    # Project lock待ち中に別transactionが確定したinventoryも再取得する。
    db.refresh(domain)
    db.expire(domain, ["drives", "interfaces"])
    list(domain.drives)
    list(domain.interfaces)
    return domain


def move_domain_to_project(
    db: Session,
    *,
    domain_uuid: str,
    destination_project_id: str,
    authorize_locked: Callable[[DomainModel, ProjectModel], bool] | None = None,
) -> DomainModel:
    """lock後のownerとgrantを再検証してVMをProjectへ同期移動する。"""

    domain = lock_domain_owner_context(
        db,
        domain_uuid,
        additional_project_ids=[destination_project_id],
    )
    destination = db.get(ProjectModel, destination_project_id)
    if destination is None:  # pragma: no cover - Project row lock後の防御
        raise DomainProjectMoveNotFoundError("移動先Projectが見つかりません")
    if authorize_locked is not None and not authorize_locked(domain, destination):
        raise DomainProjectMoveNotFoundError("VMまたは移動先Projectが見つかりません")

    conflicts = domain_project_resource_conflicts(
        db,
        domain,
        destination_project_id,
    )
    if conflicts:
        raise DomainProjectMoveConflictError(conflicts)

    domain.owner_project_id = destination_project_id
    domain.owner_user_id = None
    db.flush()
    return domain
