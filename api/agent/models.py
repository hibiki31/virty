"""Agent APIの永続モデル。

監査eventはtask履歴から分離し、ORM経由の更新・削除も拒否する。DB側の
append-only制約はAlembic migrationでも設定する。
"""

from datetime import UTC, datetime
from collections.abc import Callable
from typing import Any, TypeVar, cast

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
    event,
)
from sqlalchemy.orm import Mapped, mapped_column

from mixin.database import Base

_ModelT = TypeVar("_ModelT")


def new_agent_model(model_type: type[_ModelT], **values: Any) -> _ModelT:
    """動的declarative baseのconstructorを型安全な境界へ閉じ込める。"""

    constructor = cast(Callable[..., _ModelT], model_type)
    return constructor(**values)


def utc_now() -> datetime:
    return datetime.now(UTC)


class AgentDeviceModel(Base):
    __tablename__ = "agent_devices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    principal_id: Mapped[str | None] = mapped_column(
        String,
        ForeignKey("users.username", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    public_key_jwk: Mapped[dict[str, str]] = mapped_column(JSON, nullable=False)
    public_key_thumbprint: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    allowed_scopes: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    approved_by: Mapped[str | None] = mapped_column(String)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    failure_window_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    failure_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    breaker_opened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'active', 'revoked')",
            name="ck_agent_devices_status",
        ),
    )


class AgentPairingModel(Base):
    __tablename__ = "agent_pairings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    device_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("agent_devices.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    code_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    requested_scopes: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'active', 'expired', 'rejected')",
            name="ck_agent_pairings_status",
        ),
    )


class AgentWebAuthnCredentialModel(Base):
    __tablename__ = "agent_webauthn_credentials"

    credential_id: Mapped[str] = mapped_column(String(1024), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("users.username", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    credential_public_key: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    sign_count: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    transports: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_agent_webauthn_user_name"),
    )


class AgentWebAuthnChallengeModel(Base):
    __tablename__ = "agent_webauthn_challenges"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("users.username", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    purpose: Mapped[str] = mapped_column(String(32), nullable=False)
    subject_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    challenge: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint(
            "purpose IN ('registration', 'pairing', 'lease', "
            "'device-revoke', 'lease-revoke', 'control', 'breaker-reset', "
            "'operation-reconcile')",
            name="ck_agent_webauthn_challenges_purpose",
        ),
        Index(
            "ix_agent_webauthn_challenge_subject",
            "purpose",
            "subject_id",
        ),
    )


class AgentLeaseRequestModel(Base):
    __tablename__ = "agent_lease_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    device_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("agent_devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    principal_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    requested_scopes: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    project_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    node_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    max_mutations: Mapped[int] = mapped_column(Integer, nullable=False, default=20)
    allow_destructive: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    allow_delete_without_recovery: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    allow_network_change_without_oob: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    approved_by: Mapped[str | None] = mapped_column(String)
    issued_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    exchanged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    lease_id: Mapped[str | None] = mapped_column(String(36), unique=True)

    __table_args__ = (
        CheckConstraint(
            "max_mutations >= 0 AND max_mutations <= 20",
            name="ck_agent_lease_requests_mutation_limit",
        ),
        CheckConstraint(
            "status IN ('pending', 'approved', 'expired', 'rejected')",
            name="ck_agent_lease_requests_status",
        ),
    )


class AgentCapabilityLeaseModel(Base):
    __tablename__ = "agent_capability_leases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    jti: Mapped[str] = mapped_column(String(36), nullable=False, unique=True)
    principal_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,
    )
    device_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("agent_devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    scopes: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    project_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    node_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    max_mutations: Mapped[int] = mapped_column(Integer, nullable=False, default=20)
    mutations_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    allow_destructive: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    allow_delete_without_recovery: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    allow_network_change_without_oob: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint(
            "max_mutations >= 0 AND max_mutations <= 20",
            name="ck_agent_capability_leases_mutation_limit",
        ),
        CheckConstraint(
            "mutations_used >= 0 AND mutations_used <= max_mutations",
            name="ck_agent_capability_leases_mutations_used",
        ),
        Index(
            "ix_agent_capability_lease_active",
            "device_id",
            "expires_at",
            "revoked_at",
        ),
    )


class AgentDpopReplayModel(Base):
    __tablename__ = "agent_dpop_replays"

    device_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("agent_devices.id", ondelete="CASCADE"),
        primary_key=True,
    )
    jti: Mapped[str] = mapped_column(String(128), primary_key=True)
    seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)


class AgentControlModel(Base):
    __tablename__ = "agent_control"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    mutations_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    shadow_mode: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    enabled_risk_levels: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=lambda: ["R1"])
    allow_delete_without_recovery: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    allow_network_change_without_oob: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    reason: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_by: Mapped[str | None] = mapped_column(String)

    __table_args__ = (
        CheckConstraint("id = 1", name="ck_agent_control_singleton"),
    )


class AuditEventModel(Base):
    __tablename__ = "agent_audit_events"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    retention_until: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    actor_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    device_id: Mapped[str | None] = mapped_column(String(36), index=True)
    lease_id: Mapped[str | None] = mapped_column(String(36), index=True)
    action_id: Mapped[str | None] = mapped_column(String(128), index=True)
    resource_type: Mapped[str | None] = mapped_column(String(64))
    resource_id: Mapped[str | None] = mapped_column(String(256))
    project_id: Mapped[str | None] = mapped_column(String(64))
    node_id: Mapped[str | None] = mapped_column(String(256))
    request_hash: Mapped[str | None] = mapped_column(String(64))
    policy_decision: Mapped[str] = mapped_column(String(16), nullable=False)
    operation_id: Mapped[str | None] = mapped_column(String(36), index=True)
    correlation_id: Mapped[str | None] = mapped_column(String(36), index=True)
    outcome: Mapped[str | None] = mapped_column(String(32))
    detail: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)


@event.listens_for(AuditEventModel, "before_update", propagate=True)
def _prevent_audit_update(*_: object) -> None:
    raise RuntimeError("監査eventは更新できません")


@event.listens_for(AuditEventModel, "before_delete", propagate=True)
def _prevent_audit_delete(*_: object) -> None:
    raise RuntimeError("監査eventは削除できません")
