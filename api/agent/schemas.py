"""Agent APIの公開schema。"""

from datetime import datetime
from typing import Annotated, Any, Literal

from pydantic import ConfigDict, Field, SecretStr, field_validator

from mixin.schemas import BaseSchema as SharedBaseSchema

ScopeName = Annotated[str, Field(min_length=1, max_length=128)]
ConstraintId = Annotated[str, Field(min_length=1, max_length=255)]


class BaseSchema(SharedBaseSchema):
    """Agent公開境界では未知fieldを常に拒否する。"""

    model_config = ConfigDict(
        alias_generator=SharedBaseSchema.model_config["alias_generator"],
        from_attributes=True,
        populate_by_name=True,
        extra="forbid",
    )


class P256PublicKeyJwk(BaseSchema):
    model_config = BaseSchema.model_config | {"extra": "forbid"}

    kty: Literal["EC"]
    crv: Literal["P-256"]
    x: str = Field(min_length=43, max_length=44)
    y: str = Field(min_length=43, max_length=44)


class PairingCreateRequest(BaseSchema):
    device_name: str = Field(min_length=1, max_length=128)
    public_key_jwk: P256PublicKeyJwk
    requested_scopes: list[ScopeName] = Field(min_length=1, max_length=128)

    @field_validator("requested_scopes")
    @classmethod
    def validate_scopes(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("requestedScopesに重複は指定できません")
        if any(not item or len(item) > 128 for item in value):
            raise ValueError("requestedScopesが不正です")
        return value


class PairingCreatedResponse(BaseSchema):
    pairing_id: str
    pairing_code: str
    status: Literal["pending"]
    expires_at: datetime


class PairingStatusResponse(BaseSchema):
    pairing_id: str
    device_id: str | None = None
    status: Literal["pending", "active", "expired", "rejected"]
    expires_at: datetime


class PairingRequestSummary(BaseSchema):
    pairing_id: str
    device_id: str
    device_name: str
    requested_scopes: list[str]
    status: str
    created_at: datetime
    expires_at: datetime


class WebAuthnCredentialJSON(BaseSchema):
    """browserのPublicKeyCredential JSONを変更せず受け取る。"""

    id: str
    raw_id: str
    type: Literal["public-key"] = "public-key"
    response: dict[str, Any]
    client_extension_results: dict[str, Any] = Field(default_factory=dict)
    authenticator_attachment: str | None = None


class WebAuthnOptionsResponse(BaseSchema):
    challenge_id: str
    public_key: dict[str, Any]
    expires_at: datetime


class WebAuthnRegistrationOptionsRequest(BaseSchema):
    credential_name: str = Field(min_length=1, max_length=128)
    current_password: SecretStr = Field(min_length=1, max_length=128)


class WebAuthnRegistrationCompleteRequest(BaseSchema):
    challenge_id: str
    credential_name: str = Field(min_length=1, max_length=128)
    credential: WebAuthnCredentialJSON


class WebAuthnCredentialResponse(BaseSchema):
    credential_id: str
    credential_name: str
    created_at: datetime


class PairingApproveRequest(BaseSchema):
    pairing_code: str = Field(min_length=16, max_length=128)
    challenge_id: str
    credential: WebAuthnCredentialJSON
    allowed_scopes: list[ScopeName] | None = Field(
        default=None,
        min_length=1,
        max_length=128,
    )

    @field_validator("allowed_scopes")
    @classmethod
    def validate_allowed_scopes(cls, value: list[str] | None) -> list[str] | None:
        if value is not None and len(value) != len(set(value)):
            raise ValueError("allowedScopesに重複は指定できません")
        return value


class PairingApprovalOptionsRequest(BaseSchema):
    pairing_code: str = Field(min_length=16, max_length=128)


class LeaseRequest(BaseSchema):
    """端末が管理UIへ承認を依頼するためのrequest。"""

    device_id: str
    principal_id: str = Field(min_length=1, max_length=255)
    requested_scopes: list[ScopeName] = Field(min_length=1, max_length=128)
    project_ids: list[ConstraintId] = Field(default_factory=list, max_length=256)
    node_ids: list[ConstraintId] = Field(default_factory=list, max_length=256)
    max_mutations: int = Field(default=20, ge=0, le=20)
    allow_destructive: bool = False
    allow_delete_without_recovery: bool = False
    allow_network_change_without_oob: bool = False

    @field_validator("requested_scopes")
    @classmethod
    def validate_requested_scopes(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("requestedScopesに重複は指定できません")
        return value

    @field_validator("project_ids", "node_ids")
    @classmethod
    def validate_unique_constraints(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("projectIds/nodeIdsに重複は指定できません")
        return value


class LeasePendingResponse(BaseSchema):
    kind: Literal["pending"] = "pending"
    request_id: str
    status: Literal["pending"] = "pending"
    expires_at: datetime


class LeaseIssuedResponse(BaseSchema):
    kind: Literal["lease"] = "lease"
    access_token: str
    token_type: Literal["DPoP"] = "DPoP"
    expires_at: datetime
    lease_id: str
    max_mutations: int


class LeaseStatusResponse(BaseSchema):
    request_id: str
    device_id: str
    status: Literal["pending", "approved", "expired", "rejected"]
    expires_at: datetime


class LeaseApprovalResponse(BaseSchema):
    request_id: str
    status: Literal["approved"] = "approved"
    expires_at: datetime


class LeaseApproveRequest(BaseSchema):
    challenge_id: str
    credential: WebAuthnCredentialJSON


class LeaseRequestSummary(BaseSchema):
    request_id: str
    device_id: str
    device_name: str
    principal_id: str
    requested_scopes: list[str]
    project_ids: list[str]
    node_ids: list[str]
    max_mutations: int
    allow_destructive: bool
    allow_delete_without_recovery: bool
    allow_network_change_without_oob: bool
    status: str
    created_at: datetime
    expires_at: datetime


class ActionTarget(BaseSchema):
    resource_type: str = Field(min_length=1, max_length=64)
    resource_id: str | None = Field(default=None, max_length=256)
    project_id: str | None = Field(default=None, max_length=64)
    node_id: str | None = Field(default=None, max_length=256)


class ActionRequest(BaseSchema):
    input: dict[str, Any] = Field(default_factory=dict)
    target: ActionTarget
    idempotency_key: str | None = Field(default=None, min_length=8, max_length=128)
    expected_generation: str | None = Field(default=None, min_length=1, max_length=256)


class OperationAccepted(BaseSchema):
    operation_id: str
    task_ids: list[str]
    status: Literal[
        "queued",
        "running",
        "succeeded",
        "failed",
        "cancel_requested",
        "cancelled",
        "unknown",
    ] = "queued"
    risk: Literal["R1", "R2", "R3"]
    lease_id: str
    correlation_id: str


class ActionResult(BaseSchema):
    action: str
    result: Any
    correlation_id: str


class OperationResponse(BaseSchema):
    operation_id: str
    task_ids: list[str]
    action: str
    created_at: datetime
    updated_at: datetime
    status: Literal[
        "queued",
        "running",
        "succeeded",
        "failed",
        "cancel_requested",
        "cancelled",
        "reconciling",
        "unknown",
        "rejected",
    ]
    message: str | None = None
    error_code: str | None = None
    retryable: bool = False
    result: Any | None = None


class DeviceResponse(BaseSchema):
    id: str
    principal_id: str | None
    name: str
    status: str
    allowed_scopes: list[str]
    created_at: datetime
    approved_at: datetime | None = None
    revoked_at: datetime | None = None
    breaker_opened_at: datetime | None = None


class ControlResponse(BaseSchema):
    mutations_enabled: bool
    shadow_mode: bool
    enabled_risk_levels: list[Literal["R1", "R2", "R3"]]
    allow_delete_without_recovery: bool
    allow_network_change_without_oob: bool
    reason: str | None = None
    updated_at: datetime
    updated_by: str | None = None


class DeviceRevokeRequest(BaseSchema):
    challenge_id: str
    credential: WebAuthnCredentialJSON
    reason: str = Field(min_length=1, max_length=2000)


class WebAuthnApprovalRequest(BaseSchema):
    challenge_id: str
    credential: WebAuthnCredentialJSON
    reason: str = Field(min_length=1, max_length=2000)


class ControlChangeRequest(BaseSchema):
    mutations_enabled: bool
    shadow_mode: bool
    enabled_risk_levels: list[Literal["R1", "R2", "R3"]]
    allow_delete_without_recovery: bool = False
    allow_network_change_without_oob: bool = False
    reason: str = Field(min_length=1, max_length=2000)

    @field_validator("enabled_risk_levels")
    @classmethod
    def validate_risk_levels(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("enabledRiskLevelsに重複は指定できません")
        return value


class ControlApprovalRequest(ControlChangeRequest):
    challenge_id: str
    credential: WebAuthnCredentialJSON


class BreakerResetResponse(BaseSchema):
    device_id: str
    breaker_opened_at: datetime | None
    failure_count: int


class LeaseManagementResponse(BaseSchema):
    lease_id: str
    principal_id: str
    device_id: str
    scopes: list[str]
    issued_at: datetime
    expires_at: datetime
    revoked_at: datetime | None = None
    mutations_used: int
    max_mutations: int


class MutationResponse(BaseSchema):
    status: Literal["updated", "revoked", "reset"]


class OperationReconcileOptionsRequest(BaseSchema):
    resolution: Literal["effect_confirmed", "effect_absent"]
    reason: str = Field(min_length=1, max_length=2000)


class OperationReconcileRequest(OperationReconcileOptionsRequest):
    challenge_id: str
    credential: WebAuthnCredentialJSON
