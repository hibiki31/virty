"""pairing、WebAuthn承認、能力leaseのapplication service。"""

import secrets
from datetime import timedelta
from typing import Any

from sqlalchemy.orm import Session

from auth.function import verify_password
from task.functions import (
    TaskNotFoundError,
    get_operation,
    release_target_reservations_if_terminal,
)
from task.models import TaskModel
from user.models import UserModel

from .audit import append_audit_event
from .catalog import ACTIONS
from .crypto import (
    as_utc,
    create_capability_token,
    jwk_thumbprint,
    new_uuid,
    pairing_code,
    pairing_code_hash,
    request_hash,
    sha256_hex,
    utc_now,
    verify_dpop_proof,
)
from .exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    NotFoundError,
)
from .models import (
    AgentCapabilityLeaseModel,
    AgentControlModel,
    AgentDeviceModel,
    AgentLeaseRequestModel,
    AgentPairingModel,
    AgentWebAuthnCredentialModel,
    new_agent_model,
)
from .policy import scope_allows
from .schemas import ControlChangeRequest, LeaseRequest, PairingCreateRequest
from .webauthn import WebAuthnService

PAIRING_TTL_MINUTES = 10
LEASE_APPROVAL_TTL_MINUTES = 10
LEASE_TTL_MINUTES = 30
MAX_PENDING_PAIRINGS = 100
MAX_PENDING_LEASE_REQUESTS = 100


class AgentIdentityService:
    def __init__(self, webauthn: WebAuthnService | None = None) -> None:
        self.webauthn = webauthn or WebAuthnService()

    def create_pairing(
        self,
        db: Session,
        request: PairingCreateRequest,
    ) -> tuple[AgentPairingModel, str]:
        now = utc_now()
        db.query(AgentPairingModel).filter(
            AgentPairingModel.status == "pending",
            AgentPairingModel.expires_at <= now,
        ).update({AgentPairingModel.status: "expired"}, synchronize_session=False)
        pending_count = db.query(AgentPairingModel.id).filter(
            AgentPairingModel.status == "pending",
        ).count()
        if pending_count >= MAX_PENDING_PAIRINGS:
            raise ConflictError(
                "pairing_capacity_exceeded",
                "承認待ちpairing数が上限に達しています",
            )
        jwk = request.public_key_jwk.model_dump()
        thumbprint = jwk_thumbprint(jwk)
        if db.query(AgentDeviceModel).filter(
            AgentDeviceModel.public_key_thumbprint == thumbprint,
        ).one_or_none():
            raise ConflictError(
                "device_key_exists",
                "この端末公開鍵は既に登録されています",
            )
        self._validate_catalog_scopes(request.requested_scopes)
        code = pairing_code()
        device = new_agent_model(
            AgentDeviceModel,
            id=new_uuid(),
            principal_id=None,
            name=request.device_name,
            public_key_jwk=jwk,
            public_key_thumbprint=thumbprint,
            allowed_scopes=[],
            status="pending",
            created_at=now,
        )
        pairing = new_agent_model(
            AgentPairingModel,
            id=new_uuid(),
            device_id=device.id,
            code_hash=pairing_code_hash(code),
            requested_scopes=request.requested_scopes,
            status="pending",
            created_at=now,
            expires_at=now + timedelta(minutes=PAIRING_TTL_MINUTES),
        )
        db.add_all([device, pairing])
        append_audit_event(
            db,
            event_type="pairing.requested",
            actor_id=f"unpaired:{device.id}",
            device_id=device.id,
            policy_decision="pending",
            detail={"requestedScopes": request.requested_scopes},
        )
        return pairing, code

    def list_pending_pairings(
        self,
        db: Session,
    ) -> list[tuple[AgentPairingModel, AgentDeviceModel]]:
        rows = db.query(AgentPairingModel, AgentDeviceModel).join(
            AgentDeviceModel,
            AgentDeviceModel.id == AgentPairingModel.device_id,
        ).filter(
            AgentPairingModel.status == "pending",
        ).order_by(AgentPairingModel.created_at).all()
        result: list[tuple[AgentPairingModel, AgentDeviceModel]] = []
        for pairing, device in rows:
            if as_utc(pairing.expires_at) <= utc_now():
                pairing.status = "expired"
            else:
                result.append((pairing, device))
        return result

    def registration_options(
        self,
        db: Session,
        *,
        admin_id: str,
        current_password: str,
    ) -> tuple[Any, dict[str, Any]]:
        user = db.get(UserModel, admin_id)
        if user is None or not verify_password(current_password, user.hashed_password):
            raise AuthenticationError(
                "password_reauthentication_failed",
                "現在のpasswordを確認できません",
            )
        return self.webauthn.create_registration_options(db, user_id=admin_id)

    def complete_registration(
        self,
        db: Session,
        *,
        admin_id: str,
        challenge_id: str,
        credential_name: str,
        credential: dict[str, Any],
    ) -> AgentWebAuthnCredentialModel:
        model = self.webauthn.complete_registration(
            db,
            user_id=admin_id,
            challenge_id=challenge_id,
            credential_name=credential_name,
            credential=credential,
        )
        append_audit_event(
            db,
            event_type="webauthn.registered",
            actor_id=admin_id,
            policy_decision="allowed",
            detail={"credentialName": credential_name},
        )
        return model

    def get_pairing_status(
        self,
        db: Session,
        *,
        pairing_id: str,
        code: str,
    ) -> tuple[AgentPairingModel, AgentDeviceModel]:
        pairing = db.query(AgentPairingModel).filter(
            AgentPairingModel.id == pairing_id,
        ).with_for_update().one_or_none()
        if pairing is None or not secrets.compare_digest(
            pairing.code_hash,
            pairing_code_hash(code),
        ):
            raise NotFoundError("pairing_not_found", "pairingがありません")
        if pairing.status == "pending" and as_utc(pairing.expires_at) <= utc_now():
            pairing.status = "expired"
        device = db.get(AgentDeviceModel, pairing.device_id)
        if device is None:
            raise NotFoundError("device_not_found", "pairing端末がありません")
        return pairing, device

    def pairing_approval_options(
        self,
        db: Session,
        *,
        pairing_id: str,
        admin_id: str,
        pairing_code_value: str,
    ) -> tuple[Any, dict[str, Any]]:
        pairing = self._pending_pairing(db, pairing_id, pairing_code_value)
        return self.webauthn.create_authentication_options(
            db,
            user_id=admin_id,
            purpose="pairing",
            subject_id=pairing.id,
        )

    def approve_pairing(
        self,
        db: Session,
        *,
        pairing_id: str,
        admin_id: str,
        pairing_code_value: str,
        challenge_id: str,
        credential: dict[str, Any],
        allowed_scopes: list[str] | None,
    ) -> AgentPairingModel:
        pairing = self._pending_pairing(db, pairing_id, pairing_code_value)
        self.webauthn.verify_authentication(
            db,
            user_id=admin_id,
            purpose="pairing",
            subject_id=pairing.id,
            challenge_id=challenge_id,
            credential=credential,
        )
        granted = (
            list(pairing.requested_scopes)
            if allowed_scopes is None
            else allowed_scopes
        )
        self._validate_catalog_scopes(granted)
        for scope in granted:
            if not any(
                scope_allows(requested, scope)
                for requested in pairing.requested_scopes
            ):
                raise AuthorizationError(
                    "pairing_scope_escalation",
                    "承認scopeは端末の要求範囲を超えています",
                )
        now = utc_now()
        device = db.get(AgentDeviceModel, pairing.device_id)
        if device is None:
            raise NotFoundError("device_not_found", "pairing端末がありません")
        device.principal_id = admin_id
        device.allowed_scopes = granted
        device.status = "active"
        device.approved_at = now
        device.approved_by = admin_id
        pairing.status = "active"
        pairing.approved_at = now
        append_audit_event(
            db,
            event_type="pairing.approved",
            actor_id=admin_id,
            device_id=device.id,
            policy_decision="allowed",
            detail={"allowedScopes": granted},
        )
        return pairing

    def create_lease_request(
        self,
        db: Session,
        *,
        request: LeaseRequest,
        dpop_proof: str,
        method: str,
        url: str,
    ) -> AgentLeaseRequestModel:
        now = utc_now()
        device = db.query(AgentDeviceModel).filter(
            AgentDeviceModel.id == request.device_id,
        ).one_or_none()
        if device is None or device.status != "active" or device.revoked_at is not None:
            raise AuthenticationError("device_inactive", "端末は有効ではありません")
        verify_dpop_proof(
            db,
            proof=dpop_proof,
            device=device,
            method=method,
            url=url,
        )
        device = db.query(AgentDeviceModel).filter(
            AgentDeviceModel.id == request.device_id,
        ).populate_existing().with_for_update().one_or_none()
        if device is None or device.status != "active" or device.revoked_at is not None:
            raise AuthenticationError(
                "device_inactive_after_dpop",
                "DPoP検証中に端末が無効になりました",
            )
        db.query(AgentLeaseRequestModel).filter(
            AgentLeaseRequestModel.status == "pending",
            AgentLeaseRequestModel.expires_at <= now,
        ).update(
            {AgentLeaseRequestModel.status: "expired"},
            synchronize_session=False,
        )
        pending = db.query(AgentLeaseRequestModel).filter(
            AgentLeaseRequestModel.status == "pending",
        )
        existing_pending = pending.filter(
            AgentLeaseRequestModel.device_id == request.device_id,
        ).one_or_none()
        if existing_pending is not None:
            same_request = (
                existing_pending.principal_id == request.principal_id
                and list(existing_pending.requested_scopes) == request.requested_scopes
                and list(existing_pending.project_ids) == request.project_ids
                and list(existing_pending.node_ids) == request.node_ids
                and existing_pending.max_mutations == request.max_mutations
                and existing_pending.allow_destructive == request.allow_destructive
                and existing_pending.allow_delete_without_recovery
                == request.allow_delete_without_recovery
                and existing_pending.allow_network_change_without_oob
                == request.allow_network_change_without_oob
            )
            if same_request:
                return existing_pending
            raise ConflictError(
                "lease_request_already_pending",
                "この端末には別の承認待ちlease requestがあります",
            )
        if pending.count() >= MAX_PENDING_LEASE_REQUESTS:
            raise ConflictError(
                "lease_request_capacity_exceeded",
                "承認待ちlease request数が上限に達しています",
            )
        if request.principal_id != device.principal_id:
            raise AuthorizationError(
                "principal_mismatch",
                "lease principalはpairing承認者と一致する必要があります",
            )
        self._validate_catalog_scopes(request.requested_scopes)
        for scope in request.requested_scopes:
            if not any(
                scope_allows(granted, scope)
                for granted in list(device.allowed_scopes or [])
            ):
                raise AuthorizationError(
                    "lease_scope_escalation",
                    "要求scopeは端末の承認範囲を超えています",
                )
        self._validate_project_constraints(
            db,
            principal_id=request.principal_id,
            requested_projects=request.project_ids,
        )
        model = new_agent_model(
            AgentLeaseRequestModel,
            id=new_uuid(),
            device_id=device.id,
            principal_id=request.principal_id,
            requested_scopes=request.requested_scopes,
            project_ids=request.project_ids,
            node_ids=request.node_ids,
            max_mutations=request.max_mutations,
            allow_destructive=request.allow_destructive,
            allow_delete_without_recovery=request.allow_delete_without_recovery,
            allow_network_change_without_oob=request.allow_network_change_without_oob,
            status="pending",
            created_at=now,
            expires_at=now + timedelta(minutes=LEASE_APPROVAL_TTL_MINUTES),
        )
        db.add(model)
        append_audit_event(
            db,
            event_type="lease.requested",
            actor_id=request.principal_id,
            device_id=device.id,
            policy_decision="pending",
            detail={
                "requestedScopes": request.requested_scopes,
                "projectIds": request.project_ids,
                "nodeIds": request.node_ids,
                "maxMutations": request.max_mutations,
                "allowDestructive": request.allow_destructive,
                "allowDeleteWithoutRecovery": request.allow_delete_without_recovery,
                "allowNetworkChangeWithoutOob": request.allow_network_change_without_oob,
            },
        )
        return model

    def get_lease_request_for_device(
        self,
        db: Session,
        *,
        request_id: str,
        dpop_proof: str,
        method: str,
        url: str,
    ) -> AgentLeaseRequestModel:
        model, device = self._lease_request_and_device(db, request_id, lock=False)
        verify_dpop_proof(
            db,
            proof=dpop_proof,
            device=device,
            method=method,
            url=url,
        )
        self._expire_pending_lease_request(model)
        return model

    def list_pending_lease_requests(
        self,
        db: Session,
        *,
        admin_id: str,
    ) -> list[tuple[AgentLeaseRequestModel, AgentDeviceModel]]:
        rows = db.query(AgentLeaseRequestModel, AgentDeviceModel).join(
            AgentDeviceModel,
            AgentDeviceModel.id == AgentLeaseRequestModel.device_id,
        ).filter(
            AgentLeaseRequestModel.principal_id == admin_id,
            AgentLeaseRequestModel.status == "pending",
        ).order_by(AgentLeaseRequestModel.created_at).all()
        result = []
        for lease_request, device in rows:
            self._expire_pending_lease_request(lease_request)
            if lease_request.status == "pending":
                result.append((lease_request, device))
        return result

    def lease_approval_options(
        self,
        db: Session,
        *,
        request_id: str,
        admin_id: str,
    ) -> tuple[Any, dict[str, Any]]:
        model = self._pending_lease_request(db, request_id, admin_id)
        return self.webauthn.create_authentication_options(
            db,
            user_id=admin_id,
            purpose="lease",
            subject_id=model.id,
        )

    def approve_lease_request(
        self,
        db: Session,
        *,
        request_id: str,
        admin_id: str,
        challenge_id: str,
        credential: dict[str, Any],
    ) -> tuple[AgentLeaseRequestModel, AgentCapabilityLeaseModel]:
        model = self._pending_lease_request(db, request_id, admin_id)
        self.webauthn.verify_authentication(
            db,
            user_id=admin_id,
            purpose="lease",
            subject_id=model.id,
            challenge_id=challenge_id,
            credential=credential,
        )
        device = db.get(AgentDeviceModel, model.device_id)
        if device is None or device.status != "active" or device.principal_id != admin_id:
            raise AuthorizationError(
                "device_inactive",
                "承認対象端末は有効ではありません",
            )
        now = utc_now()
        expires_at = now + timedelta(minutes=LEASE_TTL_MINUTES)
        lease_id = new_uuid()
        jti = new_uuid()
        token = create_capability_token(
            lease_id=lease_id,
            jti=jti,
            principal_id=model.principal_id,
            device_id=model.device_id,
            device_thumbprint=device.public_key_thumbprint,
            scopes=list(model.requested_scopes),
            project_ids=list(model.project_ids),
            node_ids=list(model.node_ids),
            max_mutations=model.max_mutations,
            allow_destructive=model.allow_destructive,
            allow_delete_without_recovery=model.allow_delete_without_recovery,
            allow_network_change_without_oob=model.allow_network_change_without_oob,
            issued_at=now,
            expires_at=expires_at,
        )
        lease = new_agent_model(
            AgentCapabilityLeaseModel,
            id=lease_id,
            jti=jti,
            principal_id=model.principal_id,
            device_id=model.device_id,
            token_hash=sha256_hex(token),
            scopes=list(model.requested_scopes),
            project_ids=list(model.project_ids),
            node_ids=list(model.node_ids),
            max_mutations=model.max_mutations,
            mutations_used=0,
            allow_destructive=model.allow_destructive,
            allow_delete_without_recovery=model.allow_delete_without_recovery,
            allow_network_change_without_oob=model.allow_network_change_without_oob,
            issued_at=now,
            expires_at=expires_at,
        )
        model.status = "approved"
        model.approved_at = now
        model.approved_by = admin_id
        model.issued_at = now
        model.expires_at = expires_at
        model.lease_id = lease.id
        db.add(lease)
        append_audit_event(
            db,
            event_type="lease.approved",
            actor_id=admin_id,
            device_id=device.id,
            lease_id=lease.id,
            policy_decision="allowed",
            detail={"maxMutations": lease.max_mutations},
        )
        return model, lease

    def exchange_approved_lease(
        self,
        db: Session,
        *,
        request_id: str,
        dpop_proof: str,
        method: str,
        url: str,
    ) -> tuple[AgentCapabilityLeaseModel, str]:
        model, device = self._lease_request_and_device(db, request_id, lock=False)
        verify_dpop_proof(
            db,
            proof=dpop_proof,
            device=device,
            method=method,
            url=url,
        )
        model, device = self._lease_request_and_device(db, request_id, lock=True)
        if model.status != "approved" or not model.lease_id:
            raise ConflictError(
                "lease_not_approved",
                "lease requestはまだ承認されていません",
            )
        if model.exchanged_at is not None:
            raise ConflictError(
                "lease_already_exchanged",
                "能力leaseは既に端末へ交付されています",
            )
        lease = db.get(AgentCapabilityLeaseModel, model.lease_id)
        if lease is None or lease.revoked_at is not None or as_utc(lease.expires_at) <= utc_now():
            raise AuthenticationError("lease_expired", "能力leaseは無効です")
        token = self._recreate_token(lease, device)
        if not secrets.compare_digest(lease.token_hash, sha256_hex(token)):
            raise AuthenticationError(
                "lease_integrity_error",
                "能力leaseのintegrity検査に失敗しました",
            )
        model.exchanged_at = utc_now()
        append_audit_event(
            db,
            event_type="lease.exchanged",
            actor_id=lease.principal_id,
            device_id=device.id,
            lease_id=lease.id,
            policy_decision="allowed",
            outcome="issued",
        )
        return lease, token

    @staticmethod
    def _recreate_token(
        lease: AgentCapabilityLeaseModel,
        device: AgentDeviceModel,
    ) -> str:
        return create_capability_token(
            lease_id=lease.id,
            jti=lease.jti,
            principal_id=lease.principal_id,
            device_id=lease.device_id,
            device_thumbprint=device.public_key_thumbprint,
            scopes=list(lease.scopes),
            project_ids=list(lease.project_ids),
            node_ids=list(lease.node_ids),
            max_mutations=lease.max_mutations,
            allow_destructive=lease.allow_destructive,
            allow_delete_without_recovery=lease.allow_delete_without_recovery,
            allow_network_change_without_oob=lease.allow_network_change_without_oob,
            issued_at=as_utc(lease.issued_at),
            expires_at=as_utc(lease.expires_at),
        )

    @staticmethod
    def _pending_pairing(
        db: Session,
        pairing_id: str,
        pairing_code_value: str,
    ) -> AgentPairingModel:
        pairing = db.query(AgentPairingModel).filter(
            AgentPairingModel.id == pairing_id,
        ).with_for_update().one_or_none()
        if pairing is None:
            raise NotFoundError("pairing_not_found", "pairingがありません")
        if not secrets.compare_digest(
            pairing.code_hash,
            pairing_code_hash(pairing_code_value),
        ):
            raise NotFoundError("pairing_not_found", "pairingがありません")
        if pairing.status != "pending":
            raise ConflictError("pairing_not_pending", "pairingは承認待ちではありません")
        if as_utc(pairing.expires_at) <= utc_now():
            pairing.status = "expired"
            raise AuthenticationError("pairing_expired", "pairingの有効期限が切れています")
        return pairing

    @staticmethod
    def _lease_request_and_device(
        db: Session,
        request_id: str,
        *,
        lock: bool,
    ) -> tuple[AgentLeaseRequestModel, AgentDeviceModel]:
        model_query = db.query(AgentLeaseRequestModel).filter(
            AgentLeaseRequestModel.id == request_id,
        )
        if lock:
            model_query = model_query.populate_existing().with_for_update()
        model = model_query.one_or_none()
        if model is None:
            raise NotFoundError("lease_request_not_found", "lease requestがありません")
        device_query = db.query(AgentDeviceModel).filter(
            AgentDeviceModel.id == model.device_id,
        )
        if lock:
            device_query = device_query.populate_existing().with_for_update()
        device = device_query.one_or_none()
        if device is None or device.status != "active":
            raise AuthenticationError("device_inactive", "端末は有効ではありません")
        return model, device

    def _pending_lease_request(
        self,
        db: Session,
        request_id: str,
        admin_id: str,
    ) -> AgentLeaseRequestModel:
        model = db.query(AgentLeaseRequestModel).filter(
            AgentLeaseRequestModel.id == request_id,
        ).with_for_update().one_or_none()
        if model is None:
            raise NotFoundError("lease_request_not_found", "lease requestがありません")
        if model.principal_id != admin_id:
            raise AuthorizationError(
                "lease_principal_mismatch",
                "別のprincipalのlease requestは承認できません",
            )
        self._expire_pending_lease_request(model)
        if model.status != "pending":
            raise ConflictError(
                "lease_request_not_pending",
                "lease requestは承認待ちではありません",
            )
        return model

    @staticmethod
    def _expire_pending_lease_request(model: AgentLeaseRequestModel) -> None:
        if model.status == "pending" and as_utc(model.expires_at) <= utc_now():
            model.status = "expired"

    @staticmethod
    def _validate_project_constraints(
        db: Session,
        *,
        principal_id: str,
        requested_projects: list[str],
    ) -> None:
        user = db.get(UserModel, principal_id)
        if user is None:
            raise NotFoundError("principal_not_found", "lease principalがありません")
        scopes = {scope.name for scope in user.scopes}
        if "admin" in scopes:
            return
        allowed_projects = {project.id for project in user.projects}
        if any(project not in allowed_projects for project in requested_projects):
            raise AuthorizationError(
                "project_scope_escalation",
                "要求projectはprincipalの所属範囲を超えています",
            )

    @staticmethod
    def _validate_catalog_scopes(scopes: list[str]) -> None:
        for scope in scopes:
            if scope == "identity.admin":
                continue
            if scope == "*":
                continue
            if scope.endswith(".*"):
                if any(action.startswith(scope[:-1]) for action in ACTIONS):
                    continue
            elif scope in ACTIONS:
                continue
            raise AuthorizationError(
                "unknown_action_scope",
                f"catalogに存在しないaction scopeです: {scope}",
            )


def ensure_control(db: Session) -> AgentControlModel:
    control = db.get(AgentControlModel, 1)
    if control is None:
        control = new_agent_model(
            AgentControlModel,
            id=1,
            mutations_enabled=False,
            shadow_mode=True,
            enabled_risk_levels=["R1"],
        )
        db.add(control)
        db.flush()
    return control


class AgentManagementService:
    """WebAuthn再承認を伴う独立停止・失効操作。"""

    def __init__(self, webauthn: WebAuthnService | None = None) -> None:
        self.webauthn = webauthn or WebAuthnService()

    def list_devices(self, db: Session) -> list[AgentDeviceModel]:
        return db.query(AgentDeviceModel).order_by(AgentDeviceModel.created_at).all()

    def list_leases(
        self,
        db: Session,
        *,
        admin_id: str,
    ) -> list[AgentCapabilityLeaseModel]:
        return db.query(AgentCapabilityLeaseModel).filter(
            AgentCapabilityLeaseModel.principal_id == admin_id,
        ).order_by(AgentCapabilityLeaseModel.issued_at.desc()).all()

    def approval_options(
        self,
        db: Session,
        *,
        admin_id: str,
        purpose: str,
        subject_id: str,
    ) -> tuple[Any, dict[str, Any]]:
        self._validate_subject(db, admin_id, purpose, subject_id)
        return self.webauthn.create_authentication_options(
            db,
            user_id=admin_id,
            purpose=purpose,
            subject_id=subject_id,
        )

    def control_approval_options(
        self,
        db: Session,
        *,
        admin_id: str,
        change: ControlChangeRequest,
    ) -> tuple[Any, dict[str, Any]]:
        subject_id = self.control_subject(change)
        return self.approval_options(
            db,
            admin_id=admin_id,
            purpose="control",
            subject_id=subject_id,
        )

    def revoke_device(
        self,
        db: Session,
        *,
        admin_id: str,
        device_id: str,
        challenge_id: str,
        credential: dict[str, Any],
        reason: str,
    ) -> AgentDeviceModel:
        device = self._device(db, device_id)
        self._verify(
            db,
            admin_id=admin_id,
            purpose="device-revoke",
            subject_id=device_id,
            challenge_id=challenge_id,
            credential=credential,
        )
        now = utc_now()
        device.status = "revoked"
        device.revoked_at = now
        db.query(AgentCapabilityLeaseModel).filter(
            AgentCapabilityLeaseModel.device_id == device_id,
            AgentCapabilityLeaseModel.revoked_at.is_(None),
        ).update({AgentCapabilityLeaseModel.revoked_at: now}, synchronize_session=False)
        db.query(AgentLeaseRequestModel).filter(
            AgentLeaseRequestModel.device_id == device_id,
            AgentLeaseRequestModel.status == "pending",
        ).update({AgentLeaseRequestModel.status: "rejected"}, synchronize_session=False)
        append_audit_event(
            db,
            event_type="device.revoked",
            actor_id=admin_id,
            device_id=device_id,
            policy_decision="allowed",
            outcome="revoked",
            detail={"reason": reason},
        )
        return device

    def revoke_lease(
        self,
        db: Session,
        *,
        admin_id: str,
        lease_id: str,
        challenge_id: str,
        credential: dict[str, Any],
        reason: str,
    ) -> AgentCapabilityLeaseModel:
        lease = self._lease(db, lease_id, admin_id)
        self._verify(
            db,
            admin_id=admin_id,
            purpose="lease-revoke",
            subject_id=lease_id,
            challenge_id=challenge_id,
            credential=credential,
        )
        if lease.revoked_at is None:
            lease.revoked_at = utc_now()
        append_audit_event(
            db,
            event_type="lease.revoked",
            actor_id=admin_id,
            device_id=lease.device_id,
            lease_id=lease.id,
            policy_decision="allowed",
            outcome="revoked",
            detail={"reason": reason},
        )
        return lease

    def update_control(
        self,
        db: Session,
        *,
        admin_id: str,
        change: ControlChangeRequest,
        challenge_id: str,
        credential: dict[str, Any],
    ) -> AgentControlModel:
        subject_id = self.control_subject(change)
        self._verify(
            db,
            admin_id=admin_id,
            purpose="control",
            subject_id=subject_id,
            challenge_id=challenge_id,
            credential=credential,
        )
        control = ensure_control(db)
        control.mutations_enabled = change.mutations_enabled
        control.shadow_mode = change.shadow_mode
        control.enabled_risk_levels = list(change.enabled_risk_levels)
        control.allow_delete_without_recovery = change.allow_delete_without_recovery
        control.allow_network_change_without_oob = (
            change.allow_network_change_without_oob
        )
        control.reason = change.reason
        control.updated_at = utc_now()
        control.updated_by = admin_id
        append_audit_event(
            db,
            event_type="control.updated",
            actor_id=admin_id,
            policy_decision="allowed",
            outcome="updated",
            detail={
                "mutationsEnabled": change.mutations_enabled,
                "shadowMode": change.shadow_mode,
                "enabledRiskLevels": list(change.enabled_risk_levels),
                "allowDeleteWithoutRecovery": change.allow_delete_without_recovery,
                "allowNetworkChangeWithoutOob": (
                    change.allow_network_change_without_oob
                ),
                "reason": change.reason,
            },
        )
        return control

    def reset_breaker(
        self,
        db: Session,
        *,
        admin_id: str,
        device_id: str,
        challenge_id: str,
        credential: dict[str, Any],
        reason: str,
    ) -> AgentDeviceModel:
        device = self._device(db, device_id)
        self._verify(
            db,
            admin_id=admin_id,
            purpose="breaker-reset",
            subject_id=device_id,
            challenge_id=challenge_id,
            credential=credential,
        )
        device.breaker_opened_at = None
        device.failure_window_started_at = None
        device.failure_count = 0
        append_audit_event(
            db,
            event_type="breaker.reset",
            actor_id=admin_id,
            device_id=device_id,
            policy_decision="allowed",
            outcome="reset",
            detail={"reason": reason},
        )
        return device

    def operation_reconcile_options(
        self,
        db: Session,
        *,
        admin_id: str,
        operation_id: str,
        resolution: str,
        reason: str,
    ) -> tuple[Any, dict[str, Any]]:
        self._unknown_operation_tasks(db, operation_id)
        subject_id = self.operation_reconcile_subject(
            operation_id,
            resolution,
            reason,
        )
        return self.webauthn.create_authentication_options(
            db,
            user_id=admin_id,
            purpose="operation-reconcile",
            subject_id=subject_id,
        )

    def reconcile_operation(
        self,
        db: Session,
        *,
        admin_id: str,
        operation_id: str,
        resolution: str,
        reason: str,
        challenge_id: str,
        credential: dict[str, Any],
    ) -> dict[str, Any]:
        subject_id = self.operation_reconcile_subject(
            operation_id,
            resolution,
            reason,
        )
        self._verify(
            db,
            admin_id=admin_id,
            purpose="operation-reconcile",
            subject_id=subject_id,
            challenge_id=challenge_id,
            credential=credential,
        )
        tasks = self._unknown_operation_tasks(db, operation_id)
        now = utc_now()
        for task in tasks:
            if task.status != "unknown":
                continue
            if resolution == "effect_confirmed":
                task.status = "finish"
                task.message = f"管理者が外部効果を確認しました: {reason}"
                task.error_code = None
                task.retryable = False
            elif resolution == "effect_absent":
                task.status = "error"
                task.message = f"管理者が外部効果なしを確認しました: {reason}"
                task.error_code = "AGENT_EFFECT_CONFIRMED_ABSENT"
                task.retryable = False
            else:
                raise ConflictError(
                    "invalid_operation_resolution",
                    "operation resolutionが不正です",
                )
            task.update_time = now
        if resolution == "effect_absent":
            for task in tasks:
                if task.status in {"wait", "init", "cancel_requested"}:
                    task.status = "cancelled"
                    task.message = "親operationの外部効果なし確認により取消しました"
                    task.error_code = "AGENT_PARENT_EFFECT_ABSENT"
                    task.retryable = False
                    task.update_time = now
        root = next(task for task in tasks if task.uuid == operation_id)
        action_id = self._operation_action(root)
        append_audit_event(
            db,
            event_type="operation.reconciled",
            actor_id=admin_id,
            lease_id=root.lease_id,
            action_id=action_id,
            operation_id=operation_id,
            correlation_id=root.correlation_id or root.uuid,
            policy_decision="allowed",
            outcome=resolution,
            detail={"reason": reason},
        )
        release_target_reservations_if_terminal(
            db,
            root.correlation_id or root.uuid,
        )
        db.flush()
        return get_operation(db, operation_id)

    @staticmethod
    def control_subject(change: ControlChangeRequest) -> str:
        return request_hash(change.model_dump(mode="json", by_alias=True))

    @staticmethod
    def operation_reconcile_subject(
        operation_id: str,
        resolution: str,
        reason: str,
    ) -> str:
        return request_hash({
            "operationId": operation_id,
            "resolution": resolution,
            "reason": reason,
        })

    @staticmethod
    def _unknown_operation_tasks(
        db: Session,
        operation_id: str,
    ) -> list[TaskModel]:
        try:
            operation = get_operation(db, operation_id)
        except TaskNotFoundError as exc:
            raise NotFoundError("operation_not_found", "operationがありません") from exc
        tasks = db.query(TaskModel).filter(
            TaskModel.uuid.in_(operation["task_ids"]),
        ).with_for_update().all()
        if operation["normalized_status"] != "unknown" or not any(
            task.status == "unknown" for task in tasks
        ):
            raise ConflictError(
                "operation_not_unknown",
                "unknown状態のoperationだけをreconcileできます",
            )
        return tasks

    @staticmethod
    def _operation_action(task: TaskModel) -> str:
        if task.method == "agent" and task.object in ACTIONS:
            return str(task.object)
        selector = (task.method, task.resource, task.object)
        for definition in ACTIONS.values():
            if definition.task_selector == selector:
                return definition.action_id
        return f"internal.{task.resource}.{task.object}.{task.method}"

    def _verify(
        self,
        db: Session,
        *,
        admin_id: str,
        purpose: str,
        subject_id: str,
        challenge_id: str,
        credential: dict[str, Any],
    ) -> None:
        self.webauthn.verify_authentication(
            db,
            user_id=admin_id,
            purpose=purpose,
            subject_id=subject_id,
            challenge_id=challenge_id,
            credential=credential,
        )

    @staticmethod
    def _device(db: Session, device_id: str) -> AgentDeviceModel:
        device = db.query(AgentDeviceModel).filter(
            AgentDeviceModel.id == device_id,
        ).with_for_update().one_or_none()
        if device is None:
            raise NotFoundError("device_not_found", "端末がありません")
        return device

    @staticmethod
    def _lease(
        db: Session,
        lease_id: str,
        admin_id: str,
    ) -> AgentCapabilityLeaseModel:
        lease = db.query(AgentCapabilityLeaseModel).filter(
            AgentCapabilityLeaseModel.id == lease_id,
            AgentCapabilityLeaseModel.principal_id == admin_id,
        ).with_for_update().one_or_none()
        if lease is None:
            raise NotFoundError("lease_not_found", "能力leaseがありません")
        return lease

    def _validate_subject(
        self,
        db: Session,
        admin_id: str,
        purpose: str,
        subject_id: str,
    ) -> None:
        if purpose in {"device-revoke", "breaker-reset"}:
            self._device(db, subject_id)
        elif purpose == "lease-revoke":
            self._lease(db, subject_id, admin_id)
        else:
            raise ConflictError("invalid_webauthn_purpose", "承認目的が不正です")
