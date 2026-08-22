"""同期実装だったAgent mutationを既存worker queueで実行する。"""

from typing import Any

from sqlalchemy.orm import Session

from task.functions import TaskBase
from task.models import TaskModel
from task.schemas import TaskRequest

from .actions import (
    _load_input_model,
    _validate_identity_admin_scope,
    _validate_public_json,
)
from .adapters import DIRECT_ADAPTERS, ResolvedTarget
from .audit import append_audit_event, redact_secrets
from .catalog import ACTIONS, get_action
from .exceptions import AuditWriteError, AuthorizationError, ServiceUnavailableError
from .models import AgentCapabilityLeaseModel, AgentDeviceModel
from .policy import LeaseContext

worker_task = TaskBase()


def _worker_context(db: Session, task: TaskModel) -> LeaseContext:
    """dispatch policyで検査済みの永続情報からadapter contextを復元する。"""

    lease = db.get(AgentCapabilityLeaseModel, task.lease_id)
    if lease is None:
        raise AuthorizationError(
            "lease_missing_at_handler",
            "Agent direct handlerの能力leaseがありません",
        )
    device = db.get(AgentDeviceModel, lease.device_id)
    if device is None:
        raise AuthorizationError(
            "device_missing_at_handler",
            "Agent direct handlerの端末がありません",
        )
    if task.principal_id != lease.principal_id:
        raise AuthorizationError(
            "principal_mismatch_at_handler",
            "Agent direct handlerのprincipalがleaseと一致しません",
        )
    # token自体はworkerへ保存・伝搬しない。policy判断に必要な情報はDBを正本とする。
    return LeaseContext(lease=lease, device=device, claims={}, token="")


def _resolved_target(task: TaskModel, resource_type: str) -> ResolvedTarget:
    values = task.resolved_targets or []
    if isinstance(values, dict):
        values = [values]
    if not values or not isinstance(values[0], dict):
        raise AuthorizationError(
            "resolved_target_missing_at_handler",
            "Agent direct handlerのresolved targetがありません",
        )
    primary = values[0]
    related = tuple(
        dict(item)
        for item in values[1:]
        if isinstance(item, dict)
    )
    return ResolvedTarget(
        resource_type=resource_type,
        resource_id=str(primary.get("resourceId") or ""),
        project_id=primary.get("projectId"),
        node_id=primary.get("nodeId"),
        generation_resource_type=(
            str(primary.get("resourceType"))
            if str(primary.get("generationTarget", "")).lower() == "true"
            else None
        ),
        generation_resource_id=(
            str(primary.get("resourceId"))
            if str(primary.get("generationTarget", "")).lower() == "true"
            else None
        ),
        related_targets=related,
    )


def execute_direct_action(
    db: Session,
    model: TaskModel,
    req: TaskRequest,
) -> Any:
    """catalog済みdirect adapterだけをworker process内で実行する。"""

    action_id = str(model.object)
    definition = get_action(action_id)
    if definition.kind != "direct":
        raise ServiceUnavailableError(
            "direct_action_kind_mismatch",
            "Agent direct handlerへ非direct actionが渡されました",
        )
    adapter = DIRECT_ADAPTERS.get(definition.adapter)
    if adapter is None:
        raise ServiceUnavailableError(
            "action_adapter_missing",
            "direct action adapterが登録されていません",
        )
    raw_input = req.body or {}
    if not isinstance(raw_input, dict):
        raise AuthorizationError(
            "direct_request_invalid",
            "Agent direct request bodyがobjectではありません",
        )
    # DB改ざんやversion差でも未知fieldをworkerまで通さない。
    _validate_public_json(action_id, raw_input)
    input_model = _load_input_model(definition, raw_input)
    input_model.__dict__["_agent_operation_id"] = model.uuid
    target = _resolved_target(model, definition.resource_type)
    context = _worker_context(db, model)
    _validate_identity_admin_scope(db, context, definition, input_model)
    result = adapter(db, context, input_model, target)
    model.result = redact_secrets(result)
    model.message = "Agent direct operationが完了しました"
    try:
        append_audit_event(
            db,
            event_type="operation.completed",
            actor_id=context.principal_id,
            device_id=context.device.id,
            lease_id=context.lease.id,
            action_id=action_id,
            resource_type=target.resource_type,
            resource_id=target.resource_id,
            project_id=target.project_id,
            node_id=target.node_id,
            policy_decision="allowed",
            operation_id=model.uuid,
            correlation_id=model.correlation_id,
            outcome="succeeded",
        )
    except AuditWriteError as exc:
        if action_id == "node.ssh-key.write":
            # filesystemの鍵交換はDB rollbackで取り消せない。
            # 監査失敗時はunknownとし、target reservationを保持する。
            exc.outcome_unknown = True
        raise
    return result


for _definition in ACTIONS.values():
    if _definition.kind == "direct":
        worker_task(key=f"agent.direct.{_definition.action_id}")(
            execute_direct_action,
        )
