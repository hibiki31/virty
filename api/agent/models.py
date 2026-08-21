"""Agent APIの永続モデル。

監査eventはtask履歴から分離し、ORM経由の更新・削除も拒否する。DB側の
append-only制約はAlembic migrationでも設定する。
"""

from datetime import UTC, datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
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

from mixin.database import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class AgentDeviceModel(Base):
    __tablename__ = "agent_devices"

    id = Column(String(36), primary_key=True)
    principal_id = Column(
        String,
        ForeignKey("users.username", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    name = Column(String(128), nullable=False)
    public_key_jwk = Column(JSON, nullable=False)
    public_key_thumbprint = Column(String(64), nullable=False, unique=True)
    allowed_scopes = Column(JSON, nullable=False, default=list)
    status = Column(String(16), nullable=False, default="pending")
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    approved_at = Column(DateTime(timezone=True))
    approved_by = Column(String)
    revoked_at = Column(DateTime(timezone=True))
    last_seen_at = Column(DateTime(timezone=True))
    failure_window_started_at = Column(DateTime(timezone=True))
    failure_count = Column(Integer, nullable=False, default=0)
    breaker_opened_at = Column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'active', 'revoked')",
            name="ck_agent_devices_status",
        ),
    )


class AgentPairingModel(Base):
    __tablename__ = "agent_pairings"

    id = Column(String(36), primary_key=True)
    device_id = Column(
        String(36),
        ForeignKey("agent_devices.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    code_hash = Column(String(64), nullable=False)
    requested_scopes = Column(JSON, nullable=False, default=list)
    status = Column(String(16), nullable=False, default="pending")
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    approved_at = Column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'active', 'expired', 'rejected')",
            name="ck_agent_pairings_status",
        ),
    )


class AgentWebAuthnCredentialModel(Base):
    __tablename__ = "agent_webauthn_credentials"

    credential_id = Column(String(1024), primary_key=True)
    user_id = Column(
        String,
        ForeignKey("users.username", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(128), nullable=False)
    credential_public_key = Column(LargeBinary, nullable=False)
    sign_count = Column(BigInteger, nullable=False, default=0)
    transports = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    last_used_at = Column(DateTime(timezone=True))
    revoked_at = Column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_agent_webauthn_user_name"),
    )


class AgentWebAuthnChallengeModel(Base):
    __tablename__ = "agent_webauthn_challenges"

    id = Column(String(36), primary_key=True)
    user_id = Column(
        String,
        ForeignKey("users.username", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    purpose = Column(String(32), nullable=False)
    subject_id = Column(String(128), nullable=False, index=True)
    challenge = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True))

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

    id = Column(String(36), primary_key=True)
    device_id = Column(
        String(36),
        ForeignKey("agent_devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    principal_id = Column(
        String,
        nullable=False,
    )
    requested_scopes = Column(JSON, nullable=False, default=list)
    project_ids = Column(JSON, nullable=False, default=list)
    node_ids = Column(JSON, nullable=False, default=list)
    max_mutations = Column(Integer, nullable=False, default=20)
    allow_destructive = Column(Boolean, nullable=False, default=False)
    allow_delete_without_recovery = Column(Boolean, nullable=False, default=False)
    allow_network_change_without_oob = Column(Boolean, nullable=False, default=False)
    status = Column(String(16), nullable=False, default="pending")
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    approved_at = Column(DateTime(timezone=True))
    approved_by = Column(String)
    issued_at = Column(DateTime(timezone=True))
    exchanged_at = Column(DateTime(timezone=True))
    lease_id = Column(String(36), unique=True)

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

    id = Column(String(36), primary_key=True)
    jti = Column(String(36), nullable=False, unique=True)
    principal_id = Column(
        String,
        nullable=False,
        index=True,
    )
    device_id = Column(
        String(36),
        ForeignKey("agent_devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash = Column(String(64), nullable=False, unique=True)
    scopes = Column(JSON, nullable=False, default=list)
    project_ids = Column(JSON, nullable=False, default=list)
    node_ids = Column(JSON, nullable=False, default=list)
    max_mutations = Column(Integer, nullable=False, default=20)
    mutations_used = Column(Integer, nullable=False, default=0)
    allow_destructive = Column(Boolean, nullable=False, default=False)
    allow_delete_without_recovery = Column(Boolean, nullable=False, default=False)
    allow_network_change_without_oob = Column(Boolean, nullable=False, default=False)
    issued_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_used_at = Column(DateTime(timezone=True))
    revoked_at = Column(DateTime(timezone=True))

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

    device_id = Column(
        String(36),
        ForeignKey("agent_devices.id", ondelete="CASCADE"),
        primary_key=True,
    )
    jti = Column(String(128), primary_key=True)
    seen_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)


class AgentControlModel(Base):
    __tablename__ = "agent_control"

    id = Column(Integer, primary_key=True, default=1)
    mutations_enabled = Column(Boolean, nullable=False, default=False)
    shadow_mode = Column(Boolean, nullable=False, default=True)
    enabled_risk_levels = Column(JSON, nullable=False, default=lambda: ["R1"])
    allow_delete_without_recovery = Column(Boolean, nullable=False, default=False)
    allow_network_change_without_oob = Column(Boolean, nullable=False, default=False)
    reason = Column(Text)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_by = Column(String)

    __table_args__ = (
        CheckConstraint("id = 1", name="ck_agent_control_singleton"),
    )


class AuditEventModel(Base):
    __tablename__ = "agent_audit_events"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    occurred_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    retention_until = Column(DateTime(timezone=True), nullable=False)
    event_type = Column(String(64), nullable=False, index=True)
    actor_id = Column(String, nullable=False, index=True)
    device_id = Column(String(36), index=True)
    lease_id = Column(String(36), index=True)
    action_id = Column(String(128), index=True)
    resource_type = Column(String(64))
    resource_id = Column(String(256))
    project_id = Column(String(64))
    node_id = Column(String(256))
    request_hash = Column(String(64))
    policy_decision = Column(String(16), nullable=False)
    operation_id = Column(String(36), index=True)
    correlation_id = Column(String(36), index=True)
    outcome = Column(String(32))
    detail = Column(JSON, nullable=False, default=dict)


@event.listens_for(AuditEventModel, "before_update", propagate=True)
def _prevent_audit_update(*_: object) -> None:
    raise RuntimeError("監査eventは更新できません")


@event.listens_for(AuditEventModel, "before_delete", propagate=True)
def _prevent_audit_delete(*_: object) -> None:
    raise RuntimeError("監査eventは削除できません")
