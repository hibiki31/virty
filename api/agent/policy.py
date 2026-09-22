"""能力lease policyとworker dispatch直前の再検査。"""

import secrets
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from .audit import append_audit_event
from .catalog import ACTIONS, DEPENDENT_TASK_SELECTORS, ActionDefinition
from .crypto import (
    as_utc,
    decode_capability_token,
    request_hash,
    sha256_hex,
    utc_now,
    verify_dpop_proof,
)
from .exceptions import AuthenticationError, AuthorizationError, ConflictError
from .models import (
    AgentCapabilityLeaseModel,
    AgentControlModel,
    AgentDeviceModel,
    AuditEventModel,
)
from .project_boundary import (
    validate_mutation_lease_constraints,
    validate_project_mutation_targets,
)

BREAKER_WINDOW_MINUTES = 30
BREAKER_FAILURE_LIMIT = 3
MAX_CONCURRENT_MUTATIONS = 3
MAX_CONCURRENT_R3 = 1


@dataclass(frozen=True)
class LeaseContext:
    lease: AgentCapabilityLeaseModel
    device: AgentDeviceModel
    claims: dict[str, Any]
    token: str

    @property
    def principal_id(self) -> str:
        return self.lease.principal_id


def scope_allows(granted: str, requested: str) -> bool:
    """scopeは完全一致か明示的な`.*`だけを許可する。"""

    if granted == requested or granted == "*":
        return True
    if granted.endswith(".*"):
        prefix = granted[:-1]
        return requested.startswith(prefix) and len(requested) > len(prefix)
    return False


def require_scope(granted_scopes: list[str], requested: str) -> None:
    if not any(scope_allows(granted, requested) for granted in granted_scopes):
        raise AuthorizationError(
            "scope_denied",
            f"action scope `{requested}` は能力leaseに含まれていません",
        )


def authenticate_lease(
    db: Session,
    *,
    authorization: str,
    dpop_proof: str,
    method: str,
    url: str,
) -> LeaseContext:
    scheme, separator, token = authorization.partition(" ")
    if not separator or scheme.lower() != "dpop" or not token:
        raise AuthenticationError(
            "lease_required",
            "AuthorizationにはDPoP能力leaseが必要です",
        )
    claims = decode_capability_token(token)
    lease = db.query(AgentCapabilityLeaseModel).filter(
        AgentCapabilityLeaseModel.id == str(claims["lease_id"]),
    ).one_or_none()
    if lease is None:
        raise AuthenticationError("unknown_lease", "能力leaseが存在しません")
    now = utc_now()
    if lease.revoked_at is not None:
        raise AuthenticationError("lease_revoked", "能力leaseは失効済みです")
    if as_utc(lease.expires_at) <= now:
        raise AuthenticationError("lease_expired", "能力leaseの有効期限が切れています")
    if not secrets.compare_digest(lease.token_hash, sha256_hex(token)):
        raise AuthenticationError("lease_mismatch", "能力leaseがDB記録と一致しません")
    if (
        claims.get("jti") != lease.jti
        or claims.get("sub") != lease.principal_id
        or claims.get("device_id") != lease.device_id
    ):
        raise AuthenticationError("lease_mismatch", "能力lease claimが一致しません")

    device = db.query(AgentDeviceModel).filter(
        AgentDeviceModel.id == lease.device_id,
    ).one_or_none()
    if device is None or device.status != "active" or device.revoked_at is not None:
        raise AuthenticationError("device_revoked", "端末は無効化されています")
    if device.principal_id != lease.principal_id:
        raise AuthenticationError(
            "device_principal_mismatch",
            "能力lease principalと端末の現在の所有者が一致しません",
        )
    cnf = claims.get("cnf")
    if not isinstance(cnf, dict) or not secrets.compare_digest(
        str(cnf.get("jkt", "")),
        device.public_key_thumbprint,
    ):
        raise AuthenticationError(
            "device_key_mismatch",
            "能力leaseが登録端末鍵に束縛されていません",
        )
    verify_dpop_proof(
        db,
        proof=dpop_proof,
        device=device,
        method=method,
        url=url,
        access_token=token,
        now=now,
    )
    # replay消費後にrow lockを取得し、検証中の失効raceを再検査する。
    lease = db.query(AgentCapabilityLeaseModel).filter(
        AgentCapabilityLeaseModel.id == str(claims["lease_id"]),
    ).populate_existing().with_for_update().one_or_none()
    if (
        lease is None
        or lease.revoked_at is not None
        or as_utc(lease.expires_at) <= utc_now()
        or not secrets.compare_digest(lease.token_hash, sha256_hex(token))
    ):
        raise AuthenticationError(
            "lease_inactive_after_dpop",
            "DPoP検証中に能力leaseが無効になりました",
        )
    device = db.query(AgentDeviceModel).filter(
        AgentDeviceModel.id == lease.device_id,
    ).populate_existing().with_for_update().one_or_none()
    if device is None or device.status != "active" or device.revoked_at is not None:
        raise AuthenticationError(
            "device_inactive_after_dpop",
            "DPoP検証中に端末が無効になりました",
        )
    if device.principal_id != lease.principal_id:
        raise AuthenticationError(
            "device_principal_changed_after_dpop",
            "DPoP検証中に端末principalが変更されました",
        )
    from user.models import UserModel, UserScopeModel

    principal = db.get(UserModel, lease.principal_id)
    is_admin = db.query(UserScopeModel).filter(
        UserScopeModel.user_id == lease.principal_id,
        UserScopeModel.name == "admin",
    ).first()
    if principal is None or is_admin is None:
        raise AuthenticationError(
            "principal_authority_revoked",
            "能力lease principalの管理権限は失効しています",
        )
    current_project_ids = {project.id for project in principal.projects}
    if any(
        project_id not in current_project_ids
        for project_id in lease.project_ids
    ):
        raise AuthenticationError(
            "principal_project_revoked",
            "能力leaseのProject所属は失効しています",
        )
    lease.last_used_at = now
    return LeaseContext(lease=lease, device=device, claims=claims, token=token)


def get_control(db: Session, *, lock: bool = False) -> AgentControlModel:
    query = db.query(AgentControlModel).filter(AgentControlModel.id == 1)
    if lock:
        query = query.with_for_update()
    control = query.one_or_none()
    if control is None:
        raise AuthorizationError(
            "agent_control_missing",
            "Agent制御設定がないため変更操作を拒否しました",
        )
    return control


def authorize_action(
    db: Session,
    *,
    context: LeaseContext,
    definition: ActionDefinition,
    resource_type: str,
    project_id: str | None,
    node_id: str | None,
    expected_generation: str | None,
    collection: bool = False,
) -> None:
    require_scope(list(context.lease.scopes or []), definition.required_scope)
    validate_mutation_lease_constraints(
        action_id=definition.action_id,
        mutation=definition.mutation,
        project_ids=context.lease.project_ids,
        node_ids=context.lease.node_ids,
    )
    if resource_type != definition.resource_type:
        raise AuthorizationError(
            "resource_type_mismatch",
            "actionとtarget resource typeが一致しません",
        )
    if context.lease.project_ids and not collection:
        if project_id is None or project_id not in context.lease.project_ids:
            raise AuthorizationError(
                "project_denied",
                "target projectは能力leaseの制約外です",
            )
    if context.lease.node_ids and not collection:
        if node_id is None or node_id not in context.lease.node_ids:
            raise AuthorizationError(
                "node_denied",
                "target nodeは能力leaseの制約外です",
            )
    if definition.mutation and expected_generation is None:
        raise ConflictError(
            "expected_generation_required",
            "変更操作にはexpectedGenerationが必要です",
        )
    if (
        definition.mutation
        and not definition.requires_generation
        and expected_generation != "0"
    ):
        raise ConflictError(
            "generation_sentinel_required",
            "新規作成・refreshにはexpectedGeneration=`0`を指定してください",
        )
    if not definition.mutation:
        return

    control = get_control(db, lock=True)
    if control.shadow_mode or not control.mutations_enabled:
        raise AuthorizationError(
            "mutations_disabled",
            "Agent変更操作はshadow/read-only modeです",
        )
    if definition.risk not in list(control.enabled_risk_levels or []):
        raise AuthorizationError(
            "risk_disabled",
            f"risk {definition.risk} は有効化されていません",
        )
    if context.device.breaker_opened_at is not None:
        raise AuthorizationError(
            "device_breaker_open",
            "端末のmutation breakerが開いています",
        )
    if definition.destructive and not context.lease.allow_destructive:
        raise AuthorizationError(
            "destructive_action_denied",
            "能力leaseは破壊操作を許可していません",
        )
    if definition.destructive and "delete" in definition.action_id:
        if not (
            control.allow_delete_without_recovery
            and context.lease.allow_delete_without_recovery
        ):
            raise AuthorizationError(
                "recovery_required",
                "復旧手段なしの削除はglobal設定とleaseの両方で許可が必要です",
            )
    if definition.network_change and not (
        control.allow_network_change_without_oob
        and context.lease.allow_network_change_without_oob
    ):
        raise AuthorizationError(
            "oob_required",
            "帯域外復旧なしのnetwork変更はglobal設定とleaseの両方で許可が必要です",
        )
    if context.lease.mutations_used >= context.lease.max_mutations:
        raise AuthorizationError(
            "mutation_limit_exhausted",
            "能力leaseの変更回数上限に達しました",
        )
    _check_concurrency(db, definition.risk)


def consume_mutation(context: LeaseContext) -> None:
    context.lease.mutations_used += 1


def authorize_operation_access(
    db: Session,
    *,
    context: LeaseContext,
    definition: ActionDefinition,
    task: Any,
) -> None:
    """status/cancel/idempotency replayを現在の能力leaseで再認可する。"""

    if _task_action_id(db, task) != definition.action_id:
        raise AuthorizationError(
            "operation_action_mismatch",
            "operationと要求actionが一致しません",
        )
    owner = getattr(task, "principal_id", None) or getattr(task, "user_id", None)
    if owner != context.principal_id:
        raise AuthorizationError(
            "operation_owner_mismatch",
            "operation作成者と能力lease principalが一致しません",
        )
    require_scope(list(context.lease.scopes or []), definition.required_scope)
    validate_mutation_lease_constraints(
        action_id=definition.action_id,
        mutation=definition.mutation,
        project_ids=context.lease.project_ids,
        node_ids=context.lease.node_ids,
    )
    if definition.destructive and not context.lease.allow_destructive:
        raise AuthorizationError(
            "destructive_action_denied",
            "現在の能力leaseはこの破壊操作へのaccessを許可していません",
        )
    targets = getattr(task, "resolved_targets", None) or []
    if isinstance(targets, dict):
        targets = [targets]
    if not targets:
        raise AuthorizationError(
            "operation_target_missing",
            "operationのserver-side resolved targetがありません",
        )
    for target in targets:
        if not isinstance(target, dict):
            raise AuthorizationError(
                "operation_target_invalid",
                "operationのresolved target形式が不正です",
            )
        if str(target.get("authorizationTarget", "true")).lower() == "false":
            continue
        project_id = target.get("projectId") or target.get("project_id")
        node_id = target.get("nodeId") or target.get("node_id")
        if context.lease.project_ids and project_id not in context.lease.project_ids:
            raise AuthorizationError(
                "operation_project_denied",
                "operation targetは現在のproject制約外です",
            )
        if context.lease.node_ids and node_id not in context.lease.node_ids:
            raise AuthorizationError(
                "operation_node_denied",
                "operation targetは現在のnode制約外です",
            )
    validate_project_mutation_targets(
        db,
        principal_id=context.principal_id,
        action_id=definition.action_id,
        targets=targets,
    )


def _check_concurrency(
    db: Session,
    risk: str,
    *,
    exclude_operation_id: str | None = None,
) -> None:
    """全端末を通した未完了Agent operation数を上限と比較する。"""

    from task.models import TaskModel

    active = db.query(TaskModel).filter(
        TaskModel.lease_id.is_not(None),
        TaskModel.status.in_((
            "wait",
            "init",
            "start",
            "reconciling",
            "cancel_requested",
        )),
    )
    operation_key = func.coalesce(TaskModel.correlation_id, TaskModel.uuid)
    if exclude_operation_id is not None:
        active = active.filter(operation_key != exclude_operation_id)
    if active.with_entities(operation_key).distinct().count() >= MAX_CONCURRENT_MUTATIONS:
        raise ConflictError(
            "mutation_concurrency_limit",
            "Agent変更操作は全端末で同時3件までです",
        )
    if (
        risk == "R3"
        and active.filter(TaskModel.risk == "R3")
        .with_entities(operation_key)
        .distinct()
        .count()
        >= MAX_CONCURRENT_R3
    ):
        raise ConflictError(
            "r3_concurrency_limit",
            "R3操作は全端末で同時1件までです",
        )


def validate_worker_dispatch(db: Session, task: Any) -> None:
    """workerが外部副作用を開始する直前にAgent policyを再検査する。"""

    lease_id = getattr(task, "lease_id", None)
    if not lease_id:
        return
    lease = db.query(AgentCapabilityLeaseModel).filter(
        AgentCapabilityLeaseModel.id == lease_id,
    ).with_for_update().one_or_none()
    if lease is None or lease.revoked_at is not None or as_utc(lease.expires_at) <= utc_now():
        raise AuthorizationError(
            "lease_inactive_at_dispatch",
            "dispatch前に能力leaseが無効になりました",
        )
    device = db.query(AgentDeviceModel).filter(
        AgentDeviceModel.id == lease.device_id,
    ).with_for_update().one_or_none()
    if (
        device is None
        or device.status != "active"
        or device.breaker_opened_at is not None
        or device.principal_id != lease.principal_id
    ):
        raise AuthorizationError(
            "device_inactive_at_dispatch",
            "dispatch前に端末またはprincipal束縛が無効化されました",
        )
    control = get_control(db, lock=True)
    if control.shadow_mode or not control.mutations_enabled:
        raise AuthorizationError(
            "mutations_disabled_at_dispatch",
            "dispatch前にAgent変更操作が停止されました",
        )
    action_id = _task_action_id(db, task)
    definition = ACTIONS.get(action_id)
    if definition is None or definition.kind not in {"task", "direct"}:
        raise AuthorizationError(
            "catalog_action_missing_at_dispatch",
            "dispatch対象がAgent catalogに登録されていません",
        )
    _validate_dispatch_action_contract(
        db,
        task=task,
        lease=lease,
        control=control,
        definition=definition,
    )
    risk = getattr(task, "risk", None)
    if risk not in list(control.enabled_risk_levels or []):
        raise AuthorizationError(
            "risk_disabled_at_dispatch",
            "dispatch前にrisk levelが無効化されました",
        )
    from user.models import UserModel, UserScopeModel

    if db.get(UserModel, lease.principal_id) is None or db.query(
        UserScopeModel
    ).filter(
        UserScopeModel.user_id == lease.principal_id,
        UserScopeModel.name == "admin",
    ).first() is None:
        raise AuthorizationError(
            "principal_authority_revoked_at_dispatch",
            "dispatch前にprincipalの管理権限が失効しました",
        )
    _validate_task_constraints(db, task, lease)
    _check_concurrency(
        db,
        str(risk),
        exclude_operation_id=str(task.correlation_id or task.uuid),
    )
    _validate_task_generations(db, task)
    append_audit_event(
        db,
        event_type="worker.dispatch",
        actor_id=str(getattr(task, "principal_id", None) or task.user_id),
        device_id=device.id,
        lease_id=lease.id,
        action_id=_task_action_id(db, task),
        policy_decision="allowed",
        operation_id=str(task.uuid),
        correlation_id=getattr(task, "correlation_id", None),
        outcome="dispatching",
    )


def _validate_dispatch_action_contract(
    db: Session,
    *,
    task: Any,
    lease: AgentCapabilityLeaseModel,
    control: AgentControlModel,
    definition: ActionDefinition,
) -> None:
    """受付後に変更し得るpolicyをcatalog正本から再評価する。"""

    if getattr(task, "principal_id", None) != lease.principal_id:
        raise AuthorizationError(
            "task_principal_mismatch_at_dispatch",
            "task principalと能力lease principalが一致しません",
        )
    root = _task_operation_root(db, task)
    if definition.kind == "direct":
        valid_binding = (
            task.uuid == root.uuid
            and task.dependence_uuid is None
            and task.method == "agent"
            and task.resource == "direct"
            and task.object == definition.action_id
            and root.method == "agent"
            and root.resource == "direct"
            and root.object == definition.action_id
        )
    else:
        current_selector = (task.method, task.resource, task.object)
        allowed_selectors = {
            definition.task_selector,
            *DEPENDENT_TASK_SELECTORS.get(definition.action_id, ()),
        }
        valid_binding = (
            definition.task_selector is not None
            and (root.method, root.resource, root.object)
            == definition.task_selector
            and current_selector in allowed_selectors
        )
    if not valid_binding:
        raise AuthorizationError(
            "catalog_selector_mismatch_at_dispatch",
            "task selectorとAgent catalog actionが一致しません",
        )
    require_scope(list(lease.scopes or []), definition.required_scope)
    _validate_dispatch_identity_scope(db, task, lease, definition)
    if getattr(task, "risk", None) != definition.risk:
        raise AuthorizationError(
            "catalog_risk_mismatch_at_dispatch",
            "task riskとAgent catalog riskが一致しません",
        )
    if definition.destructive and not lease.allow_destructive:
        raise AuthorizationError(
            "destructive_action_denied_at_dispatch",
            "dispatch前に破壊操作の能力が失効しました",
        )
    if definition.destructive and "delete" in definition.action_id and not (
        control.allow_delete_without_recovery
        and lease.allow_delete_without_recovery
    ):
        raise AuthorizationError(
            "recovery_required_at_dispatch",
            "dispatch前に復旧手段なし削除の許可が失効しました",
        )
    if definition.network_change and not (
        control.allow_network_change_without_oob
        and lease.allow_network_change_without_oob
    ):
        raise AuthorizationError(
            "oob_required_at_dispatch",
            "dispatch前に帯域外復旧なしnetwork変更の許可が失効しました",
        )


def _validate_dispatch_identity_scope(
    db: Session,
    task: Any,
    lease: AgentCapabilityLeaseModel,
    definition: ActionDefinition,
) -> None:
    """queue滞留中にadmin化されたuserへの変更を再認可する。"""

    if definition.action_id not in {"user.update", "user.delete"}:
        return
    from user.models import UserModel

    targets = getattr(task, "resolved_targets", None) or []
    if isinstance(targets, dict):
        targets = [targets]
    username = next(
        (
            str(item.get("resourceId"))
            for item in targets
            if isinstance(item, dict)
            and item.get("resourceType") == "user"
            and str(item.get("authorizationTarget", "true")).lower() != "false"
            and item.get("resourceId")
        ),
        None,
    )
    if username is None:
        raise AuthorizationError(
            "identity_target_missing_at_dispatch",
            "user変更のresolved targetがありません",
        )
    user = db.get(UserModel, username)
    if user is None:
        # 存在確認とgeneration確認は後段でもfail closedに行う。
        return
    if any(
        scope.name == "admin" or str(scope.name).startswith("identity.")
        for scope in (user.scopes or [])
    ):
        require_scope(list(lease.scopes or []), "identity.admin")


def record_worker_outcome(db: Session, task: Any) -> None:
    """worker結果を追記監査し、30分内の失敗/unknownでbreakerを開く。"""

    lease_id = getattr(task, "lease_id", None)
    if not lease_id:
        return
    lease = db.query(AgentCapabilityLeaseModel).filter(
        AgentCapabilityLeaseModel.id == lease_id,
    ).one_or_none()
    if lease is None:
        raise AuthorizationError("lease_missing", "taskの能力leaseがありません")
    device = db.query(AgentDeviceModel).filter(
        AgentDeviceModel.id == lease.device_id,
    ).with_for_update().one()
    status = str(getattr(task, "status", "unknown"))
    failed = status in {"error", "lost", "unknown"}
    now = utc_now()
    already_counted = db.query(AuditEventModel.id).filter(
        AuditEventModel.event_type == "breaker.failure",
        AuditEventModel.correlation_id == (task.correlation_id or task.uuid),
    ).first()
    if failed and already_counted is None:
        window_start = device.failure_window_started_at
        if (
            window_start is None
            or as_utc(window_start) <= now - timedelta(minutes=BREAKER_WINDOW_MINUTES)
        ):
            device.failure_window_started_at = now
            device.failure_count = 1
        else:
            device.failure_count += 1
        if device.failure_count >= BREAKER_FAILURE_LIMIT:
            device.breaker_opened_at = now
        append_audit_event(
            db,
            event_type="breaker.failure",
            actor_id=str(getattr(task, "principal_id", None) or task.user_id),
            device_id=device.id,
            lease_id=lease.id,
            action_id=_task_action_id(db, task),
            policy_decision="allowed",
            operation_id=str(task.uuid),
            correlation_id=task.correlation_id or task.uuid,
            outcome="failed",
        )
    append_audit_event(
        db,
        event_type="worker.outcome",
        actor_id=str(getattr(task, "principal_id", None) or task.user_id),
        device_id=device.id,
        lease_id=lease.id,
        action_id=_task_action_id(db, task),
        policy_decision="allowed",
        operation_id=str(task.uuid),
        correlation_id=getattr(task, "correlation_id", None),
        outcome=_normalize_task_status(status),
        detail={
            "errorCode": getattr(task, "error_code", None),
            "retryable": bool(getattr(task, "retryable", False)),
        },
    )


def _task_operation_root(db: Session, task: Any) -> Any:
    """correlation/dependencyから唯一のoperation rootをfail closedで解決する。"""

    from task.models import TaskModel

    owner = getattr(task, "principal_id", None) or getattr(task, "user_id", None)
    correlation_id = getattr(task, "correlation_id", None)
    if correlation_id:
        candidates = db.query(TaskModel).filter(
            TaskModel.correlation_id == task.correlation_id,
            TaskModel.dependence_uuid.is_(None),
        ).order_by(TaskModel.post_time).all()
        roots = [
            candidate
            for candidate in candidates
            if (candidate.principal_id or candidate.user_id) == owner
        ]
        if len(roots) != 1:
            raise AuthorizationError(
                "operation_root_invalid_at_dispatch",
                "operation rootが唯一に解決できません",
            )
        root = roots[0]
    else:
        root = task
        visited: set[str] = set()
        while getattr(root, "dependence_uuid", None):
            if str(root.uuid) in visited:
                raise AuthorizationError(
                    "operation_dependency_cycle_at_dispatch",
                    "operation dependencyに循環があります",
                )
            visited.add(str(root.uuid))
            parent = db.get(TaskModel, root.dependence_uuid)
            if parent is None or (parent.principal_id or parent.user_id) != owner:
                raise AuthorizationError(
                    "operation_dependency_invalid_at_dispatch",
                    "operation dependencyが同一principalのrootへ到達しません",
                )
            root = parent

    # correlation検索で見つけたrootへcurrent taskの依存chainが
    # 実際に到達することを検証し、同一correlationへの混入を防ぐ。
    current = task
    visited = set()
    while str(current.uuid) != str(root.uuid):
        if str(current.uuid) in visited or not current.dependence_uuid:
            raise AuthorizationError(
                "operation_dependency_invalid_at_dispatch",
                "current taskがoperation rootの依存chainにありません",
            )
        visited.add(str(current.uuid))
        parent = db.get(TaskModel, current.dependence_uuid)
        if (
            parent is None
            or (parent.principal_id or parent.user_id) != owner
            or (
                correlation_id
                and parent.correlation_id != correlation_id
            )
        ):
            raise AuthorizationError(
                "operation_dependency_invalid_at_dispatch",
                "operation dependencyのprincipalまたはcorrelationが一致しません",
            )
        current = parent
    if root.dependence_uuid is not None:
        raise AuthorizationError(
            "operation_root_invalid_at_dispatch",
            "operation rootにdependencyが設定されています",
        )
    return root


def _task_action_id(db: Session, task: Any) -> str:
    """dependent refreshを含め、operation rootからcatalog IDを逆引きする。"""

    root = _task_operation_root(db, task)
    if root.method == "agent" and root.object in ACTIONS:
        return str(root.object)
    selector = (root.method, root.resource, root.object)
    for definition in ACTIONS.values():
        if definition.task_selector == selector:
            return definition.action_id
    return f"internal.{root.resource}.{root.object}.{root.method}"


def _normalize_task_status(status: str) -> str:
    return {
        "wait": "queued",
        "init": "queued",
        "start": "running",
        "finish": "succeeded",
        "error": "failed",
        "lost": "unknown",
    }.get(status, status)


def _validate_task_generations(db: Session, task: Any) -> None:
    expected = getattr(task, "expected_generation", None)
    if expected is None:
        return
    if str(expected) == "0":
        return
    targets = getattr(task, "resolved_targets", None) or []
    if isinstance(targets, dict):
        targets = [targets]
    marked = [
        target
        for target in targets
        if str(target.get("generationTarget", "")).lower() == "true"
    ]
    if marked:
        targets = marked
    if len(targets) != 1:
        raise ConflictError(
            "generation_target_invalid",
            "expectedGenerationの対象は1件である必要があります",
        )
    target = targets[0]
    current = resolve_generation(
        db,
        resource_type=str(target.get("resourceType") or target.get("resource_type")),
        resource_id=str(target.get("resourceId") or target.get("resource_id")),
    )
    if not secrets.compare_digest(str(expected), str(current)):
        raise ConflictError(
            "stale_generation",
            "対象resourceは要求後に変更されています",
        )


def _validate_task_constraints(
    db: Session,
    task: Any,
    lease: AgentCapabilityLeaseModel,
) -> None:
    targets = getattr(task, "resolved_targets", None) or []
    if isinstance(targets, dict):
        targets = [targets]
    operation_root = _task_operation_root(db, task)
    action_id = _task_action_id(db, task)
    definition = ACTIONS.get(action_id)
    if definition is not None:
        validate_mutation_lease_constraints(
            action_id=definition.action_id,
            mutation=definition.mutation,
            project_ids=lease.project_ids,
            node_ids=lease.node_ids,
        )
    validate_project_mutation_targets(
        db,
        principal_id=lease.principal_id,
        action_id=action_id,
        targets=targets,
    )
    # dependent inventory taskにexpectedGenerationを複製すると、更新後の
    # generationを古いtokenで検査してしまう。create/refreshの
    # placeholder判定だけはoperation rootのsentinelを正本にする。
    create_sentinel = str(
        getattr(operation_root, "expected_generation", ""),
    ) == "0"
    for index, target in enumerate(targets):
        if str(target.get("authorizationTarget", "true")).lower() == "false":
            continue
        project_id = target.get("projectId") or target.get("project_id")
        node_id = target.get("nodeId") or target.get("node_id")
        if lease.project_ids and project_id not in lease.project_ids:
            raise AuthorizationError(
                "project_denied_at_dispatch",
                "dispatch前にtarget projectがlease制約外になりました",
            )
        if lease.node_ids and node_id not in lease.node_ids:
            raise AuthorizationError(
                "node_denied_at_dispatch",
                "dispatch前にtarget nodeがlease制約外になりました",
            )
        if create_sentinel and index == 0:
            # create/refreshの主targetはまだ存在しない。既存node/projectを参照する
            # createだけは、その参照先の存続をdispatch直前にも確認する。
            if node_id is not None and action_id != "node.create":
                from node.models import NodeModel

                if db.get(NodeModel, node_id) is None:
                    raise AuthorizationError(
                        "node_missing_at_dispatch",
                        "dispatch前にtarget nodeが削除されました",
                    )
            if project_id is not None:
                from project.models import ProjectModel

                if db.get(ProjectModel, project_id) is None:
                    raise AuthorizationError(
                        "project_missing_at_dispatch",
                        "dispatch前にtarget projectが削除されました",
                    )
            continue
        _validate_related_target_binding(db, target, lease)


def _validate_related_target_binding(
    db: Session,
    target: dict[str, Any],
    lease: AgentCapabilityLeaseModel,
) -> None:
    """受付時に解決した参照resourceの所属をdispatch直前に再確認する。"""

    resource_type = str(target.get("resourceType") or "")
    resource_id = str(target.get("resourceId") or "")
    node_id = target.get("nodeId")
    project_id = target.get("projectId")
    model: Any = None
    if resource_type == "storage":
        from storage.models import StorageModel

        model = db.get(StorageModel, resource_id)
    elif resource_type == "vm":
        from domain.models import DomainModel

        model = db.get(DomainModel, resource_id)
    elif resource_type == "node":
        from node.models import NodeModel

        model = db.get(NodeModel, resource_id)
    elif resource_type == "network":
        from network.models import NetworkModel

        model = db.get(NetworkModel, resource_id)
    elif resource_type == "image":
        import json

        from storage.models import ImageModel, StorageModel

        try:
            storage_uuid, path = json.loads(resource_id)
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise AuthorizationError(
                "related_image_invalid",
                "参照image識別子が不正です",
            ) from exc
        image = db.query(ImageModel).filter(
            ImageModel.storage_uuid == storage_uuid,
            ImageModel.path == path,
        ).one_or_none()
        model = db.get(StorageModel, storage_uuid) if image is not None else None
    elif resource_type == "flavor":
        from flavor.models import FlavorModel

        try:
            model = db.get(FlavorModel, int(resource_id))
        except ValueError:
            model = None
    elif resource_type == "storage-pool":
        from storage.models import StoragePoolModel

        try:
            model = db.get(StoragePoolModel, int(resource_id))
        except ValueError:
            model = None
    elif resource_type == "network-pool":
        from network.models import NetworkPoolModel

        try:
            model = db.get(NetworkPoolModel, int(resource_id))
        except ValueError:
            model = None
    elif resource_type == "project":
        from project.models import ProjectModel

        model = db.get(ProjectModel, resource_id)
    elif resource_type == "user":
        from user.models import UserModel

        model = db.get(UserModel, resource_id)
    elif resource_type == "task":
        from task.models import TaskModel

        model = db.get(TaskModel, resource_id)
    if model is None:
        raise AuthorizationError(
            "related_target_missing_at_dispatch",
            "dispatch前に参照resourceが削除されました",
        )
    actual_node = (
        model.name if resource_type == "node" else getattr(model, "node_name", None)
    )
    if resource_type == "task" and node_id is not None:
        values = model.resolved_targets or []
        if isinstance(values, dict):
            values = [values]
        current_nodes = {
            item.get("nodeId") or item.get("node_id")
            for item in values
            if isinstance(item, dict)
            and str(item.get("authorizationTarget", "true")).lower() != "false"
        }
        if node_id not in current_nodes:
            raise AuthorizationError(
                "related_node_changed_at_dispatch",
                "dispatch前にtask targetのnode bindingが変わりました",
            )
    if node_id is not None and actual_node is not None and actual_node != node_id:
        raise AuthorizationError(
            "related_node_changed_at_dispatch",
            "dispatch前に参照resourceのnodeが変わりました",
        )
    if project_id is not None and not _resource_belongs_to_project(
        db,
        resource_type=resource_type,
        resource_id=resource_id,
        project_id=str(project_id),
    ):
        raise AuthorizationError(
            "related_project_changed_at_dispatch",
            "dispatch前に参照resourceのproject所属が変わりました",
        )


def _resource_belongs_to_project(
    db: Session,
    *,
    resource_type: str,
    resource_id: str,
    project_id: str,
) -> bool:
    from project.models import ProjectModel

    project = db.get(ProjectModel, project_id)
    if project is None:
        return False
    if resource_type == "project":
        return resource_id == project.id
    if resource_type == "vm":
        from domain.models import DomainModel

        vm = db.get(DomainModel, resource_id)
        return vm is not None and vm.owner_project_id == project.id
    if resource_type == "node":
        from domain.models import DomainModel
        from network.models import NetworkModel
        from storage.models import StorageModel

        if db.query(DomainModel.uuid).filter(
            DomainModel.node_name == resource_id,
            DomainModel.owner_project_id == project.id,
        ).first() is not None:
            return True
        project_storage_ids = {
            association.storage_uuid
            for pool in project.storage_pools
            for association in pool.storages
        }
        if db.query(StorageModel.uuid).filter(
            StorageModel.uuid.in_(project_storage_ids or {"__none__"}),
            StorageModel.node_name == resource_id,
        ).first() is not None:
            return True
        project_network_ids = {
            network.uuid
            for pool in project.network_pools
            for network in [*pool.networks, *(port.network for port in pool.ports)]
        }
        return db.query(NetworkModel.uuid).filter(
            NetworkModel.uuid.in_(project_network_ids or {"__none__"}),
            NetworkModel.node_name == resource_id,
        ).first() is not None
    if resource_type == "storage":
        return any(
            association.storage_uuid == resource_id
            for pool in project.storage_pools
            for association in pool.storages
        )
    if resource_type == "network":
        return any(
            network.uuid == resource_id
            for pool in project.network_pools
            for network in [*pool.networks, *(port.network for port in pool.ports)]
        )
    if resource_type == "image":
        import json

        try:
            storage_uuid, _ = json.loads(resource_id)
        except (TypeError, ValueError, json.JSONDecodeError):
            return False
        return _resource_belongs_to_project(
            db,
            resource_type="storage",
            resource_id=str(storage_uuid),
            project_id=project_id,
        )
    if resource_type == "flavor":
        try:
            flavor_id = int(resource_id)
        except ValueError:
            return False
        return any(flavor.id == flavor_id for flavor in project.flavors)
    if resource_type == "storage-pool":
        try:
            pool_id = int(resource_id)
        except ValueError:
            return False
        return any(pool.id == pool_id for pool in project.storage_pools)
    if resource_type == "network-pool":
        try:
            pool_id = int(resource_id)
        except ValueError:
            return False
        return any(pool.id == pool_id for pool in project.network_pools)
    if resource_type == "task":
        from task.models import TaskModel

        task = db.get(TaskModel, resource_id)
        values = [] if task is None else (task.resolved_targets or [])
        if isinstance(values, dict):
            values = [values]
        return any(
            (item.get("projectId") or item.get("project_id")) == project_id
            for item in values
            if isinstance(item, dict)
            and str(item.get("authorizationTarget", "true")).lower() != "false"
        )
    # user/system/metrics等、project bindingを定義していないglobal resourceは拒否する。
    return False


def resolve_generation(db: Session, *, resource_type: str, resource_id: str) -> str:
    """公開可能なresource状態からoptimistic generationを解決する。"""

    value: dict[str, Any] | None
    if resource_type == "vm":
        from domain.models import DomainModel

        domain = db.get(DomainModel, resource_id)
        value = None if domain is None else {
            "uuid": domain.uuid,
            "name": domain.name,
            "core": domain.core,
            "memory": domain.memory,
            "status": domain.status,
            "description": domain.description,
            "updateToken": domain.update_token,
            "storageUsed": domain.storage_used,
            "nodeName": domain.node_name,
            "ownerUserId": domain.owner_user_id,
            "ownerProjectId": domain.owner_project_id,
            "interfaces": sorted(
                (
                    item.mac,
                    item.type,
                    item.target,
                    item.bridge,
                    item.network,
                    item.port,
                    item.update_token,
                )
                for item in domain.interfaces
            ),
            "drives": sorted(
                (
                    item.target,
                    item.device,
                    item.type,
                    item.source,
                    item.update_token,
                )
                for item in domain.drives
            ),
        }
    elif resource_type == "network":
        from network.models import NetworkModel

        network = db.get(NetworkModel, resource_id)
        value = None if network is None else {
            "uuid": network.uuid,
            "name": network.name,
            "description": network.description,
            "nodeName": network.node_name,
            "bridge": network.bridge,
            "type": network.type,
            "active": network.active,
            "autoStart": network.auto_start,
            "dhcp": network.dhcp,
            "updateToken": network.update_token,
            "ip": network.ip,
            "mac": network.mac,
            "portgroups": sorted(
                (item.name, item.vlan_id, item.is_default)
                for item in network.portgroups
            ),
        }
    elif resource_type == "storage":
        from storage.models import StorageModel

        storage = db.get(StorageModel, resource_id)
        metadata = None if storage is None else storage.meta_data
        value = None if storage is None else {
            "uuid": storage.uuid,
            "name": storage.name,
            "nodeName": storage.node_name,
            "capacity": storage.capacity,
            "available": storage.available,
            "path": storage.path,
            "active": storage.active,
            "autoStart": storage.auto_start,
            "status": storage.status,
            "updateToken": storage.update_token,
            "metadata": None if metadata is None else (
                metadata.rool,
                metadata.protocol,
                metadata.device_type,
            ),
        }
    elif resource_type == "image":
        import json

        from storage.models import ImageModel

        image = None
        try:
            storage_uuid, path = json.loads(resource_id)
        except (TypeError, ValueError, json.JSONDecodeError):
            storage_uuid, path = None, None
        if storage_uuid and path:
            image = db.query(ImageModel).filter(
                ImageModel.storage_uuid == storage_uuid,
                ImageModel.path == path,
            ).one_or_none()
        value = None if image is None else {
            "storageUuid": image.storage_uuid,
            "name": image.name,
            "path": image.path,
            "capacity": image.capacity,
            "allocation": image.allocation,
            "domainUuid": image.domain_uuid,
            "flavorId": image.flavor_id,
            "updateToken": image.update_token,
        }
    else:
        generation = _hash_non_versioned_resource(db, resource_type, resource_id)
        if generation is None:
            raise ConflictError("target_not_found", "generation対象resourceがありません")
        return generation
    if value is None:
        raise ConflictError("target_not_found", "generation対象resourceがありません")
    return request_hash(value)


def _hash_non_versioned_resource(
    db: Session,
    resource_type: str,
    resource_id: str,
) -> str | None:
    value: Any
    if resource_type == "node":
        from node.models import NodeModel

        node = db.get(NodeModel, resource_id)
        if node is None:
            return None
        value = {
            column.name: getattr(node, column.name)
            for column in node.__table__.columns
        }
    elif resource_type == "project":
        from project.models import ProjectModel

        project = db.get(ProjectModel, resource_id)
        if project is None:
            return None
        value = {
            "id": project.id,
            "name": project.name,
            "members": sorted(user.username for user in project.users),
            "limits": [project.core, project.memory_g, project.storage_capacity_g],
            "resourceGrants": {
                "storagePoolIds": sorted(pool.id for pool in project.storage_pools),
                "networkPoolIds": sorted(pool.id for pool in project.network_pools),
                "flavorIds": sorted(flavor.id for flavor in project.flavors),
            },
        }
    elif resource_type == "user":
        from user.models import UserModel

        user = db.get(UserModel, resource_id)
        if user is None:
            return None
        value = {
            "username": user.username,
            "scopes": sorted(scope.name for scope in user.scopes),
            "projects": sorted(project.id for project in user.projects),
            "publicKeys": sorted(key.name for key in user.publickeys),
        }
    elif resource_type == "flavor":
        from flavor.models import FlavorModel

        try:
            key: Any = int(resource_id)
        except ValueError:
            return None
        flavor = db.get(FlavorModel, key)
        if flavor is None:
            return None
        value = {
            column.name: getattr(flavor, column.name)
            for column in flavor.__table__.columns
        }
    elif resource_type == "network-pool":
        from network.models import NetworkPoolModel

        try:
            pool_key = int(resource_id)
        except ValueError:
            return None
        network_pool = db.get(NetworkPoolModel, pool_key)
        if network_pool is None:
            return None
        value = {
            column.name: getattr(network_pool, column.name)
            for column in network_pool.__table__.columns
        }
        value["networks"] = sorted(
            network.uuid for network in network_pool.networks
        )
        value["ports"] = sorted(
            (port.network_uuid, port.name) for port in network_pool.ports
        )
    elif resource_type == "storage-pool":
        from storage.models import StoragePoolModel

        try:
            pool_key = int(resource_id)
        except ValueError:
            return None
        storage_pool = db.get(StoragePoolModel, pool_key)
        if storage_pool is None:
            return None
        value = {
            column.name: getattr(storage_pool, column.name)
            for column in storage_pool.__table__.columns
        }
        value["storages"] = sorted(
            association.storage_uuid for association in storage_pool.storages
        )
    elif resource_type == "task":
        from task.models import TaskModel

        task = db.get(TaskModel, resource_id)
        if task is None:
            return None
        value = [task.status, str(task.update_time), task.message]
    else:
        return None
    return request_hash(value)
