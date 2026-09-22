"""Agent mutationへ現在のProject membership境界を適用する。"""

from typing import Any, Iterable

from sqlalchemy.orm import Session

from .exceptions import AuthorizationError


# Project membershipをprimary targetへ適用するmutationだけを明示する。
# node/pool/resource lifecycle、identity、inventory refresh等のglobal操作は
# この集合へ含めず、それぞれのadmin/scope検査を正本とする。
PROJECT_MEMBERSHIP_MUTATIONS = frozenset({
    "vm.create",
    "vm.delete",
    "vm.power.update",
    "vm.cdrom.update",
    "vm.network.update",
    "vm.project.update",
    "storage.metadata.update",
    "image.download",
    "image.flavor.update",
    "project.update",
    "project.member.add",
    "project.member.remove",
})


def validate_mutation_lease_constraints(
    *,
    action_id: str,
    mutation: bool,
    project_ids: Iterable[str],
    node_ids: Iterable[str],
) -> None:
    """global mutationはProject/Node制約を持たないleaseだけに許可する。"""

    if not mutation or action_id in PROJECT_MEMBERSHIP_MUTATIONS:
        return
    if list(project_ids) or list(node_ids):
        raise AuthorizationError(
            "global_mutation_requires_unscoped_lease",
            "global mutationにはProject/Node制約なしの能力leaseが必要です",
        )


def _authorization_targets(
    targets: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        target
        for target in targets
        if str(target.get("authorizationTarget", "true")).lower() != "false"
    ]


def _current_project_ids(db: Session, principal_id: str) -> set[str]:
    from user.models import association_users_to_projects

    return {
        str(project_id)
        for (project_id,) in db.query(
            association_users_to_projects.c.project_id,
        ).filter(
            association_users_to_projects.c.user_id == principal_id,
        ).all()
    }


def require_current_project_membership(
    db: Session,
    *,
    principal_id: str,
    project_id: str | None,
) -> str:
    """leaseがunscopedでもDB上の最新membershipを必須にする。"""

    if project_id is None or project_id not in _current_project_ids(
        db,
        principal_id,
    ):
        raise AuthorizationError(
            "project_membership_denied",
            "対象Projectはprincipalの現在の所属範囲外です",
        )
    return project_id


def require_vm_source_access(
    db: Session,
    *,
    principal_id: str,
    vm_uuid: str,
    bound_project_id: str | None,
) -> None:
    """Project VMはmembership、legacy personal VMは個人ownerで検査する。"""

    from domain.models import DomainModel

    vm = db.get(DomainModel, vm_uuid)
    if vm is None:
        raise AuthorizationError(
            "vm_source_denied",
            "変更元VMへaccessできません",
        )
    if vm.owner_project_id is not None:
        project_id = require_current_project_membership(
            db,
            principal_id=principal_id,
            project_id=str(vm.owner_project_id),
        )
        if bound_project_id != project_id:
            raise AuthorizationError(
                "vm_project_binding_changed",
                "変更元VMのProject bindingが一致しません",
            )
        return
    if vm.owner_user_id != principal_id or bound_project_id is not None:
        raise AuthorizationError(
            "vm_owner_denied",
            "legacy personal VMは個人ownerだけが変更できます",
        )


def require_storage_project_access(
    db: Session,
    *,
    principal_id: str,
    storage_uuid: str,
    project_id: str | None,
) -> str:
    """storage metadata等を所属Projectからgrantされたstorageへ限定する。"""

    selected_id = require_current_project_membership(
        db,
        principal_id=principal_id,
        project_id=project_id,
    )
    from project.models import association_projects_to_storages_pools
    from storage.models import AssociationStoragePoolModel

    granted_pool_ids = {
        int(pool_id)
        for (pool_id,) in db.query(
            association_projects_to_storages_pools.c.storages_pools_id,
        ).filter(
            association_projects_to_storages_pools.c.projects_id == selected_id,
        ).all()
    }
    is_granted = db.query(AssociationStoragePoolModel.storage_uuid).filter(
        AssociationStoragePoolModel.pool_id.in_(granted_pool_ids or {-1}),
        AssociationStoragePoolModel.storage_uuid == storage_uuid,
    ).first() is not None
    if not is_granted:
        raise AuthorizationError(
            "storage_project_denied",
            "対象storageはprincipal所属Projectのgrant範囲外です",
        )
    return selected_id


def validate_project_mutation_targets(
    db: Session,
    *,
    principal_id: str,
    action_id: str,
    targets: Iterable[dict[str, Any]],
) -> None:
    """server解決済みprimary/related targetを現在のDB状態で再認可する。"""

    if action_id not in PROJECT_MEMBERSHIP_MUTATIONS:
        return
    values = _authorization_targets(targets)
    if not values:
        raise AuthorizationError(
            "mutation_target_missing",
            "Project境界を検査するprimary targetがありません",
        )
    current_project_ids = _current_project_ids(db, principal_id)
    for value in values:
        value_project_id = value.get("projectId") or value.get("project_id")
        if (
            value_project_id is not None
            and str(value_project_id) not in current_project_ids
        ):
            raise AuthorizationError(
                "project_membership_denied",
                "resolved targetのProjectはprincipalの現在の所属範囲外です",
            )
    primary = values[0]
    project_id_value = primary.get("projectId") or primary.get("project_id")
    project_id = None if project_id_value is None else str(project_id_value)
    resource_id = str(
        primary.get("resourceId")
        or primary.get("resource_id")
        or "",
    )

    if action_id in {
        "vm.delete",
        "vm.power.update",
        "vm.cdrom.update",
        "vm.network.update",
        "vm.project.update",
    }:
        require_vm_source_access(
            db,
            principal_id=principal_id,
            vm_uuid=resource_id,
            bound_project_id=project_id,
        )
        return

    if action_id == "storage.metadata.update":
        require_storage_project_access(
            db,
            principal_id=principal_id,
            storage_uuid=resource_id,
            project_id=project_id,
        )
        return

    if action_id == "image.download":
        require_current_project_membership(
            db,
            principal_id=principal_id,
            project_id=project_id,
        )
        storage_target = next(
            (
                target
                for target in values[1:]
                if target.get("resourceType") == "storage"
            ),
            None,
        )
        if storage_target is None:
            raise AuthorizationError(
                "image_storage_target_missing",
                "image download先storageの解決結果がありません",
            )
        require_storage_project_access(
            db,
            principal_id=principal_id,
            storage_uuid=str(storage_target.get("resourceId") or ""),
            project_id=project_id,
        )
        return

    # VM作成、image flavor更新、Project名称/member更新はprimaryのProjectを
    # 正本にする。関連grantはaction固有検査で別途検証される。
    require_current_project_membership(
        db,
        principal_id=principal_id,
        project_id=project_id,
    )
