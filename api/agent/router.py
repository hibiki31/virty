"""閉域Agent APIの明示route。"""

from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import Depends, Header, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute, APIRouter
from sqlalchemy.orm import Session

from auth.router import CurrentUser, get_current_user
from mixin.database import get_db
from task.functions import (
    TaskNotFoundError,
    TaskOwnershipError,
    get_operation,
    request_cancel_operation,
)
from task.models import TaskModel

from .actions import execute_action
from .audit import append_audit_event, redact_secrets
from .catalog import ACTIONS, catalog_document, get_action
from .crypto import expected_htu
from .exceptions import AgentError, AuthorizationError, NotFoundError
from .policy import authenticate_lease, authorize_operation_access
from .schemas import (
    ActionRequest,
    ActionResult,
    BreakerResetResponse,
    ControlApprovalRequest,
    ControlChangeRequest,
    ControlResponse,
    DeviceResponse,
    DeviceRevokeRequest,
    LeaseApprovalResponse,
    LeaseApproveRequest,
    LeaseIssuedResponse,
    LeaseManagementResponse,
    LeasePendingResponse,
    LeaseRequest,
    LeaseRequestSummary,
    LeaseStatusResponse,
    MutationResponse,
    OperationAccepted,
    OperationReconcileOptionsRequest,
    OperationReconcileRequest,
    OperationResponse,
    PairingApproveRequest,
    PairingApprovalOptionsRequest,
    PairingCreateRequest,
    PairingCreatedResponse,
    PairingRequestSummary,
    PairingStatusResponse,
    WebAuthnApprovalRequest,
    WebAuthnCredentialResponse,
    WebAuthnOptionsResponse,
    WebAuthnRegistrationCompleteRequest,
    WebAuthnRegistrationOptionsRequest,
)
from .service import AgentIdentityService, AgentManagementService, ensure_control


class AgentAPIRoute(APIRoute):
    """秘密値を含み得るvalidation detailを安全な形式へ縮退する。"""

    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Any]]:
        original = super().get_route_handler()

        async def handler(request: Request) -> Any:
            try:
                response = await original(request)
            except AgentError as exc:
                response = JSONResponse(
                    status_code=exc.status_code,
                    content={"detail": {"code": exc.code, "message": exc.detail}},
                )
            except RequestValidationError as exc:
                errors = [
                    {
                        "field": ".".join(str(value) for value in item["loc"]),
                        "type": item["type"],
                    }
                    for item in exc.errors(include_input=False, include_url=False)
                ]
                response = JSONResponse(
                    status_code=422,
                    content={
                        "detail": {
                            "code": "validation_error",
                            "message": "request schemaが不正です",
                            "errors": errors,
                        }
                    },
                )
            response.headers["Cache-Control"] = "no-store"
            return response

        return handler


app = APIRouter(
    prefix="/api/agent/v1",
    tags=["agent"],
    route_class=AgentAPIRoute,
)


def _admin(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    current_user.verify_scope(["admin"])
    return current_user


def _options_response(challenge: Any, options: dict[str, Any]) -> WebAuthnOptionsResponse:
    return WebAuthnOptionsResponse(
        challenge_id=challenge.id,
        public_key=options,
        expires_at=challenge.expires_at,
    )


def _operation_action(db: Session, task: TaskModel) -> str:
    if task.method == "agent" and task.object in ACTIONS:
        return str(task.object)
    selector = (task.method, task.resource, task.object)
    for definition in ACTIONS.values():
        if definition.task_selector == selector:
            return definition.action_id
    raise NotFoundError(
        "operation_action_not_found",
        "operationに対応するcatalog actionがありません",
    )


def _operation_response(
    db: Session,
    operation_id: str,
    *,
    principal_id: str,
) -> OperationResponse:
    root = db.get(TaskModel, operation_id)
    if root is None:
        raise NotFoundError("operation_not_found", "operationがありません")
    owner = root.principal_id or root.user_id
    if owner != principal_id:
        # 別principalのoperation有無を公開しない。
        raise NotFoundError("operation_not_found", "operationがありません")
    try:
        operation = get_operation(db, operation_id)
    except TaskNotFoundError as exc:
        raise NotFoundError("operation_not_found", "operationがありません") from exc
    tasks = db.query(TaskModel).filter(
        TaskModel.uuid.in_(operation["task_ids"]),
    ).all()
    timestamps = [
        value
        for task in tasks
        for value in (task.update_time, task.start_time, task.post_time)
        if value is not None
    ]
    created_at = root.post_time or root.start_time or root.update_time
    if created_at is None or not timestamps:
        raise NotFoundError(
            "operation_timestamp_missing",
            "operation時刻が記録されていません",
        )
    return OperationResponse(
        operation_id=operation["operation_id"],
        task_ids=operation["task_ids"],
        action=_operation_action(db, root),
        created_at=created_at,
        updated_at=max(timestamps),
        status=operation["normalized_status"],
        message=operation.get("message"),
        error_code=operation.get("error_code"),
        retryable=bool(operation.get("retryable", False)),
        result=redact_secrets(root.result),
    )


def _root_operation_task(db: Session, task: TaskModel) -> TaskModel:
    """dependency chainを遡り、操作APIへ渡すroot task UUIDを確定する。"""

    owner = task.principal_id or task.user_id
    current = task
    visited = {current.uuid}
    while current.dependence_uuid and current.dependence_uuid not in visited:
        parent = db.get(TaskModel, current.dependence_uuid)
        if parent is None or (parent.principal_id or parent.user_id) != owner:
            break
        current = parent
        visited.add(current.uuid)
    return current


@app.post("/pairings", response_model=PairingCreatedResponse, status_code=201)
def create_pairing(
    body: PairingCreateRequest,
    db: Session = Depends(get_db),
) -> PairingCreatedResponse:
    pairing, code = AgentIdentityService().create_pairing(db, body)
    db.commit()
    return PairingCreatedResponse(
        pairing_id=pairing.id,
        pairing_code=code,
        status="pending",
        expires_at=pairing.expires_at,
    )


@app.get("/pairings/{pairing_id}", response_model=PairingStatusResponse)
def pairing_status(
    pairing_id: str,
    pairing_code: str = Header(alias="X-Pairing-Code"),
    db: Session = Depends(get_db),
) -> PairingStatusResponse:
    pairing, device = AgentIdentityService().get_pairing_status(
        db,
        pairing_id=pairing_id,
        code=pairing_code,
    )
    db.commit()
    return PairingStatusResponse(
        pairing_id=pairing.id,
        device_id=device.id if pairing.status == "active" else None,
        status=pairing.status,
        expires_at=pairing.expires_at,
    )


@app.get("/pairing-requests", response_model=list[PairingRequestSummary])
def pending_pairings(
    _: CurrentUser = Depends(_admin),
    db: Session = Depends(get_db),
) -> list[PairingRequestSummary]:
    rows = AgentIdentityService().list_pending_pairings(db)
    db.commit()
    return [
        PairingRequestSummary(
            pairing_id=pairing.id,
            device_id=device.id,
            device_name=device.name,
            requested_scopes=list(pairing.requested_scopes),
            status=pairing.status,
            created_at=pairing.created_at,
            expires_at=pairing.expires_at,
        )
        for pairing, device in rows
    ]


@app.post(
    "/pairing-requests/{pairing_id}/approval-options",
    response_model=WebAuthnOptionsResponse,
)
def pairing_approval_options(
    pairing_id: str,
    body: PairingApprovalOptionsRequest,
    current_user: CurrentUser = Depends(_admin),
    db: Session = Depends(get_db),
) -> WebAuthnOptionsResponse:
    challenge, options = AgentIdentityService().pairing_approval_options(
        db,
        pairing_id=pairing_id,
        admin_id=current_user.id,
        pairing_code_value=body.pairing_code,
    )
    db.commit()
    return _options_response(challenge, options)


@app.post(
    "/pairing-requests/{pairing_id}/approve",
    response_model=PairingStatusResponse,
)
def approve_pairing(
    pairing_id: str,
    body: PairingApproveRequest,
    current_user: CurrentUser = Depends(_admin),
    db: Session = Depends(get_db),
) -> PairingStatusResponse:
    pairing = AgentIdentityService().approve_pairing(
        db,
        pairing_id=pairing_id,
        admin_id=current_user.id,
        pairing_code_value=body.pairing_code,
        challenge_id=body.challenge_id,
        credential=body.credential.model_dump(mode="json", by_alias=True),
        allowed_scopes=body.allowed_scopes,
    )
    db.commit()
    return PairingStatusResponse(
        pairing_id=pairing.id,
        device_id=pairing.device_id,
        status="active",
        expires_at=pairing.expires_at,
    )


@app.post(
    "/webauthn/registration-options",
    response_model=WebAuthnOptionsResponse,
)
def webauthn_registration_options(
    body: WebAuthnRegistrationOptionsRequest,
    current_user: CurrentUser = Depends(_admin),
    db: Session = Depends(get_db),
) -> WebAuthnOptionsResponse:
    challenge, options = AgentIdentityService().registration_options(
        db,
        admin_id=current_user.id,
        current_password=body.current_password.get_secret_value(),
    )
    db.commit()
    return _options_response(challenge, options)


@app.post(
    "/webauthn/registrations",
    response_model=WebAuthnCredentialResponse,
    status_code=201,
)
def complete_webauthn_registration(
    body: WebAuthnRegistrationCompleteRequest,
    current_user: CurrentUser = Depends(_admin),
    db: Session = Depends(get_db),
) -> WebAuthnCredentialResponse:
    credential = AgentIdentityService().complete_registration(
        db,
        admin_id=current_user.id,
        challenge_id=body.challenge_id,
        credential_name=body.credential_name,
        credential=body.credential.model_dump(mode="json", by_alias=True),
    )
    db.commit()
    return WebAuthnCredentialResponse(
        credential_id=credential.credential_id,
        credential_name=credential.name,
        created_at=credential.created_at,
    )


@app.post("/leases", response_model=LeasePendingResponse, status_code=202)
def request_lease(
    request: Request,
    body: LeaseRequest,
    dpop: str = Header(alias="DPoP"),
    db: Session = Depends(get_db),
) -> LeasePendingResponse:
    model = AgentIdentityService().create_lease_request(
        db,
        request=body,
        dpop_proof=dpop,
        method=request.method,
        url=expected_htu(request.url.path),
    )
    db.commit()
    return LeasePendingResponse(request_id=model.id, expires_at=model.expires_at)


@app.get("/leases/{request_id}", response_model=LeaseStatusResponse)
def lease_status(
    request_id: str,
    request: Request,
    dpop: str = Header(alias="DPoP"),
    db: Session = Depends(get_db),
) -> LeaseStatusResponse:
    model = AgentIdentityService().get_lease_request_for_device(
        db,
        request_id=request_id,
        dpop_proof=dpop,
        method=request.method,
        url=expected_htu(request.url.path),
    )
    db.commit()
    return LeaseStatusResponse(
        request_id=model.id,
        device_id=model.device_id,
        status=model.status,
        expires_at=model.expires_at,
    )


@app.post("/leases/{request_id}/exchange", response_model=LeaseIssuedResponse)
def exchange_lease(
    request_id: str,
    request: Request,
    dpop: str = Header(alias="DPoP"),
    db: Session = Depends(get_db),
) -> LeaseIssuedResponse:
    lease, token = AgentIdentityService().exchange_approved_lease(
        db,
        request_id=request_id,
        dpop_proof=dpop,
        method=request.method,
        url=expected_htu(request.url.path),
    )
    db.commit()
    return LeaseIssuedResponse(
        access_token=token,
        expires_at=lease.expires_at,
        lease_id=lease.id,
        max_mutations=lease.max_mutations,
    )


@app.get("/lease-requests", response_model=list[LeaseRequestSummary])
def pending_lease_requests(
    current_user: CurrentUser = Depends(_admin),
    db: Session = Depends(get_db),
) -> list[LeaseRequestSummary]:
    rows = AgentIdentityService().list_pending_lease_requests(
        db,
        admin_id=current_user.id,
    )
    db.commit()
    return [
        LeaseRequestSummary(
            request_id=model.id,
            device_id=device.id,
            device_name=device.name,
            principal_id=model.principal_id,
            requested_scopes=list(model.requested_scopes),
            project_ids=list(model.project_ids),
            node_ids=list(model.node_ids),
            max_mutations=model.max_mutations,
            allow_destructive=model.allow_destructive,
            allow_delete_without_recovery=model.allow_delete_without_recovery,
            allow_network_change_without_oob=model.allow_network_change_without_oob,
            status=model.status,
            created_at=model.created_at,
            expires_at=model.expires_at,
        )
        for model, device in rows
    ]


@app.post(
    "/lease-requests/{request_id}/approval-options",
    response_model=WebAuthnOptionsResponse,
)
def lease_approval_options(
    request_id: str,
    current_user: CurrentUser = Depends(_admin),
    db: Session = Depends(get_db),
) -> WebAuthnOptionsResponse:
    challenge, options = AgentIdentityService().lease_approval_options(
        db,
        request_id=request_id,
        admin_id=current_user.id,
    )
    db.commit()
    return _options_response(challenge, options)


@app.post(
    "/lease-requests/{request_id}/approve",
    response_model=LeaseApprovalResponse,
)
def approve_lease(
    request_id: str,
    body: LeaseApproveRequest,
    current_user: CurrentUser = Depends(_admin),
    db: Session = Depends(get_db),
) -> LeaseApprovalResponse:
    model, _ = AgentIdentityService().approve_lease_request(
        db,
        request_id=request_id,
        admin_id=current_user.id,
        challenge_id=body.challenge_id,
        credential=body.credential.model_dump(mode="json", by_alias=True),
    )
    db.commit()
    return LeaseApprovalResponse(request_id=model.id, expires_at=model.expires_at)


@app.post(
    "/actions/{action_id}",
    response_model=ActionResult | OperationAccepted,
)
def run_action(
    action_id: str,
    body: ActionRequest,
    request: Request,
    authorization: str = Header(alias="Authorization"),
    dpop: str = Header(alias="DPoP"),
    db: Session = Depends(get_db),
) -> ActionResult | OperationAccepted:
    context = authenticate_lease(
        db,
        authorization=authorization,
        dpop_proof=dpop,
        method=request.method,
        url=expected_htu(request.url.path),
    )
    return execute_action(
        db,
        context=context,
        action_id=action_id,
        request=body,
    )


@app.get("/operations/{operation_id}", response_model=OperationResponse)
def operation_status(
    operation_id: str,
    request: Request,
    authorization: str = Header(alias="Authorization"),
    dpop: str = Header(alias="DPoP"),
    db: Session = Depends(get_db),
) -> OperationResponse:
    context = authenticate_lease(
        db,
        authorization=authorization,
        dpop_proof=dpop,
        method=request.method,
        url=expected_htu(request.url.path),
    )
    response = _operation_response(
        db,
        operation_id,
        principal_id=context.principal_id,
    )
    root = db.get(TaskModel, operation_id)
    if root is None:  # pragma: no cover - _operation_responseで検査済み
        raise NotFoundError("operation_not_found", "operationがありません")
    authorize_operation_access(
        db,
        context=context,
        definition=get_action(response.action),
        task=root,
    )
    append_audit_event(
        db,
        event_type="operation.read",
        actor_id=context.principal_id,
        device_id=context.device.id,
        lease_id=context.lease.id,
        action_id=response.action,
        operation_id=operation_id,
        policy_decision="allowed",
        outcome=response.status,
    )
    db.commit()
    return response


@app.post("/operations/{operation_id}", response_model=OperationResponse)
def cancel_operation(
    operation_id: str,
    request: Request,
    authorization: str = Header(alias="Authorization"),
    dpop: str = Header(alias="DPoP"),
    db: Session = Depends(get_db),
) -> OperationResponse:
    context = authenticate_lease(
        db,
        authorization=authorization,
        dpop_proof=dpop,
        method=request.method,
        url=expected_htu(request.url.path),
    )
    # getで所有者を先に確認し、Task helperのadmin例外は使用しない。
    response = _operation_response(
        db,
        operation_id,
        principal_id=context.principal_id,
    )
    root = db.get(TaskModel, operation_id)
    if root is None:  # pragma: no cover - _operation_responseで検査済み
        raise NotFoundError("operation_not_found", "operationがありません")
    authorize_operation_access(
        db,
        context=context,
        definition=get_action(response.action),
        task=root,
    )
    try:
        request_cancel_operation(
            db,
            operation_id,
            context.principal_id,
            admin=False,
            commit_transaction=False,
        )
    except TaskNotFoundError as exc:
        raise NotFoundError("operation_not_found", "operationがありません") from exc
    except TaskOwnershipError as exc:
        raise AuthorizationError(
            "operation_owner_mismatch",
            "operation作成者だけが取消できます",
        ) from exc
    append_audit_event(
        db,
        event_type="operation.cancel-requested",
        actor_id=context.principal_id,
        device_id=context.device.id,
        lease_id=context.lease.id,
        action_id=response.action,
        operation_id=operation_id,
        policy_decision="allowed",
        outcome="cancel_requested",
    )
    db.commit()
    return _operation_response(
        db,
        operation_id,
        principal_id=context.principal_id,
    )


@app.get("/catalog")
def get_catalog(_: CurrentUser = Depends(_admin)) -> dict[str, object]:
    return catalog_document()


@app.get("/devices", response_model=list[DeviceResponse])
def list_devices(
    _: CurrentUser = Depends(_admin),
    db: Session = Depends(get_db),
) -> list[DeviceResponse]:
    return [DeviceResponse.model_validate(item) for item in AgentManagementService().list_devices(db)]


@app.post(
    "/devices/{device_id}/revoke-options",
    response_model=WebAuthnOptionsResponse,
)
def device_revoke_options(
    device_id: str,
    current_user: CurrentUser = Depends(_admin),
    db: Session = Depends(get_db),
) -> WebAuthnOptionsResponse:
    challenge, options = AgentManagementService().approval_options(
        db,
        admin_id=current_user.id,
        purpose="device-revoke",
        subject_id=device_id,
    )
    db.commit()
    return _options_response(challenge, options)


@app.post("/devices/{device_id}/revoke", response_model=MutationResponse)
def revoke_device(
    device_id: str,
    body: DeviceRevokeRequest,
    current_user: CurrentUser = Depends(_admin),
    db: Session = Depends(get_db),
) -> MutationResponse:
    AgentManagementService().revoke_device(
        db,
        admin_id=current_user.id,
        device_id=device_id,
        challenge_id=body.challenge_id,
        credential=body.credential.model_dump(mode="json", by_alias=True),
        reason=body.reason,
    )
    db.commit()
    return MutationResponse(status="revoked")


@app.post(
    "/devices/{device_id}/breaker-reset-options",
    response_model=WebAuthnOptionsResponse,
)
def breaker_reset_options(
    device_id: str,
    current_user: CurrentUser = Depends(_admin),
    db: Session = Depends(get_db),
) -> WebAuthnOptionsResponse:
    challenge, options = AgentManagementService().approval_options(
        db,
        admin_id=current_user.id,
        purpose="breaker-reset",
        subject_id=device_id,
    )
    db.commit()
    return _options_response(challenge, options)


@app.post(
    "/devices/{device_id}/breaker-reset",
    response_model=BreakerResetResponse,
)
def reset_breaker(
    device_id: str,
    body: WebAuthnApprovalRequest,
    current_user: CurrentUser = Depends(_admin),
    db: Session = Depends(get_db),
) -> BreakerResetResponse:
    device = AgentManagementService().reset_breaker(
        db,
        admin_id=current_user.id,
        device_id=device_id,
        challenge_id=body.challenge_id,
        credential=body.credential.model_dump(mode="json", by_alias=True),
        reason=body.reason,
    )
    db.commit()
    return BreakerResetResponse(
        device_id=device.id,
        breaker_opened_at=device.breaker_opened_at,
        failure_count=device.failure_count,
    )


@app.get("/capability-leases", response_model=list[LeaseManagementResponse])
def list_capability_leases(
    current_user: CurrentUser = Depends(_admin),
    db: Session = Depends(get_db),
) -> list[LeaseManagementResponse]:
    return [
        LeaseManagementResponse(
            lease_id=item.id,
            principal_id=item.principal_id,
            device_id=item.device_id,
            scopes=list(item.scopes),
            issued_at=item.issued_at,
            expires_at=item.expires_at,
            revoked_at=item.revoked_at,
            mutations_used=item.mutations_used,
            max_mutations=item.max_mutations,
        )
        for item in AgentManagementService().list_leases(
            db,
            admin_id=current_user.id,
        )
    ]


@app.post(
    "/capability-leases/{lease_id}/revoke-options",
    response_model=WebAuthnOptionsResponse,
)
def lease_revoke_options(
    lease_id: str,
    current_user: CurrentUser = Depends(_admin),
    db: Session = Depends(get_db),
) -> WebAuthnOptionsResponse:
    challenge, options = AgentManagementService().approval_options(
        db,
        admin_id=current_user.id,
        purpose="lease-revoke",
        subject_id=lease_id,
    )
    db.commit()
    return _options_response(challenge, options)


@app.post(
    "/capability-leases/{lease_id}/revoke",
    response_model=MutationResponse,
)
def revoke_lease(
    lease_id: str,
    body: WebAuthnApprovalRequest,
    current_user: CurrentUser = Depends(_admin),
    db: Session = Depends(get_db),
) -> MutationResponse:
    AgentManagementService().revoke_lease(
        db,
        admin_id=current_user.id,
        lease_id=lease_id,
        challenge_id=body.challenge_id,
        credential=body.credential.model_dump(mode="json", by_alias=True),
        reason=body.reason,
    )
    db.commit()
    return MutationResponse(status="revoked")


@app.get("/control", response_model=ControlResponse)
def get_agent_control(
    _: CurrentUser = Depends(_admin),
    db: Session = Depends(get_db),
) -> ControlResponse:
    return ControlResponse.model_validate(ensure_control(db))


@app.get(
    "/operation-reconciliations",
    response_model=list[OperationResponse],
)
def list_operation_reconciliations(
    _: CurrentUser = Depends(_admin),
    db: Session = Depends(get_db),
) -> list[OperationResponse]:
    """unknownを含むAgent operationをroot task単位で返す。"""

    unknown_tasks = db.query(TaskModel).filter(
        TaskModel.lease_id.is_not(None),
        TaskModel.archived_at.is_(None),
        TaskModel.status == "unknown",
    ).order_by(TaskModel.post_time.desc(), TaskModel.uuid).all()
    roots = {
        root.uuid: root
        for root in (_root_operation_task(db, task) for task in unknown_tasks)
    }
    responses = [
        _operation_response(
            db,
            root.uuid,
            principal_id=str(root.principal_id or root.user_id),
        )
        for root in roots.values()
    ]
    return sorted(responses, key=lambda item: item.updated_at, reverse=True)


@app.post("/control/approval-options", response_model=WebAuthnOptionsResponse)
def control_approval_options(
    body: ControlChangeRequest,
    current_user: CurrentUser = Depends(_admin),
    db: Session = Depends(get_db),
) -> WebAuthnOptionsResponse:
    challenge, options = AgentManagementService().control_approval_options(
        db,
        admin_id=current_user.id,
        change=body,
    )
    db.commit()
    return _options_response(challenge, options)


@app.put("/control", response_model=ControlResponse)
def update_agent_control(
    body: ControlApprovalRequest,
    current_user: CurrentUser = Depends(_admin),
    db: Session = Depends(get_db),
) -> ControlResponse:
    change = ControlChangeRequest.model_validate(
        body.model_dump(exclude={"challenge_id", "credential"}),
    )
    control = AgentManagementService().update_control(
        db,
        admin_id=current_user.id,
        change=change,
        challenge_id=body.challenge_id,
        credential=body.credential.model_dump(mode="json", by_alias=True),
    )
    db.commit()
    return ControlResponse.model_validate(control)


@app.post(
    "/operation-reconciliations/{operation_id}/approval-options",
    response_model=WebAuthnOptionsResponse,
)
def operation_reconcile_options(
    operation_id: str,
    body: OperationReconcileOptionsRequest,
    current_user: CurrentUser = Depends(_admin),
    db: Session = Depends(get_db),
) -> WebAuthnOptionsResponse:
    challenge, options = AgentManagementService().operation_reconcile_options(
        db,
        admin_id=current_user.id,
        operation_id=operation_id,
        resolution=body.resolution,
        reason=body.reason,
    )
    db.commit()
    return _options_response(challenge, options)


@app.post(
    "/operation-reconciliations/{operation_id}/resolve",
    response_model=OperationResponse,
)
def reconcile_operation(
    operation_id: str,
    body: OperationReconcileRequest,
    current_user: CurrentUser = Depends(_admin),
    db: Session = Depends(get_db),
) -> OperationResponse:
    AgentManagementService().reconcile_operation(
        db,
        admin_id=current_user.id,
        operation_id=operation_id,
        resolution=body.resolution,
        reason=body.reason,
        challenge_id=body.challenge_id,
        credential=body.credential.model_dump(mode="json", by_alias=True),
    )
    db.commit()
    root = db.get(TaskModel, operation_id)
    if root is None:
        raise NotFoundError("operation_not_found", "operationがありません")
    return _operation_response(
        db,
        operation_id,
        principal_id=str(root.principal_id or root.user_id),
    )
