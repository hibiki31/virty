"""Agent APIの認証・能力lease・監査modelを追加する。

Revision ID: a71e4f2d9c30
Revises: 9f2c6a8e41d7
Create Date: 2026-08-22 10:00:00

"""

from datetime import UTC, datetime

from alembic import op
import sqlalchemy as sa


revision = "a71e4f2d9c30"
down_revision = "9f2c6a8e41d7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 旧VNC passwordはDBからも廃止し、one-time ticketだけを保持する。
    op.drop_column("domains", "vnc_password")
    op.create_table(
        "domain_console_tickets",
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("domain_uuid", sa.String(), nullable=False),
        sa.Column("actor_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["domain_uuid"],
            ["domains.uuid"],
            name="domain_console_tickets_domain_uuid_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("token_hash"),
    )
    op.create_index(
        "ix_domain_console_tickets_domain_uuid",
        "domain_console_tickets",
        ["domain_uuid"],
    )
    op.create_index(
        "ix_domain_console_tickets_expires_at",
        "domain_console_tickets",
        ["expires_at"],
    )

    # user/project削除でVM cache rowまでcascade削除されないようにする。
    op.drop_constraint("domains_owner_user_id_fkey", "domains", type_="foreignkey")
    op.drop_constraint("domains_owner_project_id_fkey", "domains", type_="foreignkey")
    op.create_foreign_key(
        "domains_owner_user_id_fkey",
        "domains",
        "users",
        ["owner_user_id"],
        ["username"],
        onupdate="CASCADE",
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "domains_owner_project_id_fkey",
        "domains",
        "projects",
        ["owner_project_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="SET NULL",
    )

    op.create_table(
        "agent_devices",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("principal_id", sa.String(), nullable=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("public_key_jwk", sa.JSON(), nullable=False),
        sa.Column("public_key_thumbprint", sa.String(length=64), nullable=False),
        sa.Column("allowed_scopes", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_by", sa.String(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "failure_window_started_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column("failure_count", sa.Integer(), nullable=False),
        sa.Column("breaker_opened_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('pending', 'active', 'revoked')",
            name="ck_agent_devices_status",
        ),
        sa.ForeignKeyConstraint(
            ["principal_id"],
            ["users.username"],
            name="agent_devices_principal_id_fkey",
            onupdate="CASCADE",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "public_key_thumbprint",
            name="uq_agent_devices_public_key_thumbprint",
        ),
    )
    op.create_index("ix_agent_devices_principal_id", "agent_devices", ["principal_id"])

    op.create_table(
        "agent_pairings",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("device_id", sa.String(length=36), nullable=False),
        sa.Column("code_hash", sa.String(length=64), nullable=False),
        sa.Column("requested_scopes", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('pending', 'active', 'expired', 'rejected')",
            name="ck_agent_pairings_status",
        ),
        sa.ForeignKeyConstraint(
            ["device_id"],
            ["agent_devices.id"],
            name="agent_pairings_device_id_fkey",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("device_id", name="uq_agent_pairings_device_id"),
    )

    op.create_table(
        "agent_webauthn_credentials",
        sa.Column("credential_id", sa.String(length=1024), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("credential_public_key", sa.LargeBinary(), nullable=False),
        sa.Column("sign_count", sa.BigInteger(), nullable=False),
        sa.Column("transports", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.username"],
            name="agent_webauthn_credentials_user_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("credential_id"),
        sa.UniqueConstraint(
            "user_id",
            "name",
            name="uq_agent_webauthn_user_name",
        ),
    )
    op.create_index(
        "ix_agent_webauthn_credentials_user_id",
        "agent_webauthn_credentials",
        ["user_id"],
    )

    op.create_table(
        "agent_webauthn_challenges",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("purpose", sa.String(length=32), nullable=False),
        sa.Column("subject_id", sa.String(length=128), nullable=False),
        sa.Column("challenge", sa.LargeBinary(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "purpose IN ('registration', 'pairing', 'lease', "
            "'device-revoke', 'lease-revoke', 'control', 'breaker-reset', "
            "'operation-reconcile')",
            name="ck_agent_webauthn_challenges_purpose",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.username"],
            name="agent_webauthn_challenges_user_id_fkey",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_agent_webauthn_challenges_user_id",
        "agent_webauthn_challenges",
        ["user_id"],
    )
    op.create_index(
        "ix_agent_webauthn_challenges_subject_id",
        "agent_webauthn_challenges",
        ["subject_id"],
    )
    op.create_index(
        "ix_agent_webauthn_challenge_subject",
        "agent_webauthn_challenges",
        ["purpose", "subject_id"],
    )

    op.create_table(
        "agent_lease_requests",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("device_id", sa.String(length=36), nullable=False),
        sa.Column("principal_id", sa.String(), nullable=False),
        sa.Column("requested_scopes", sa.JSON(), nullable=False),
        sa.Column("project_ids", sa.JSON(), nullable=False),
        sa.Column("node_ids", sa.JSON(), nullable=False),
        sa.Column("max_mutations", sa.Integer(), nullable=False),
        sa.Column("allow_destructive", sa.Boolean(), nullable=False),
        sa.Column("allow_delete_without_recovery", sa.Boolean(), nullable=False),
        sa.Column("allow_network_change_without_oob", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_by", sa.String(), nullable=True),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("exchanged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("lease_id", sa.String(length=36), nullable=True),
        sa.CheckConstraint(
            "max_mutations >= 0 AND max_mutations <= 20",
            name="ck_agent_lease_requests_mutation_limit",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'approved', 'expired', 'rejected')",
            name="ck_agent_lease_requests_status",
        ),
        sa.ForeignKeyConstraint(
            ["device_id"],
            ["agent_devices.id"],
            name="agent_lease_requests_device_id_fkey",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("lease_id", name="uq_agent_lease_requests_lease_id"),
    )
    op.create_index(
        "ix_agent_lease_requests_device_id",
        "agent_lease_requests",
        ["device_id"],
    )

    op.create_table(
        "agent_capability_leases",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("jti", sa.String(length=36), nullable=False),
        sa.Column("principal_id", sa.String(), nullable=False),
        sa.Column("device_id", sa.String(length=36), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("scopes", sa.JSON(), nullable=False),
        sa.Column("project_ids", sa.JSON(), nullable=False),
        sa.Column("node_ids", sa.JSON(), nullable=False),
        sa.Column("max_mutations", sa.Integer(), nullable=False),
        sa.Column("mutations_used", sa.Integer(), nullable=False),
        sa.Column("allow_destructive", sa.Boolean(), nullable=False),
        sa.Column("allow_delete_without_recovery", sa.Boolean(), nullable=False),
        sa.Column("allow_network_change_without_oob", sa.Boolean(), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "max_mutations >= 0 AND max_mutations <= 20",
            name="ck_agent_capability_leases_mutation_limit",
        ),
        sa.CheckConstraint(
            "mutations_used >= 0 AND mutations_used <= max_mutations",
            name="ck_agent_capability_leases_mutations_used",
        ),
        sa.ForeignKeyConstraint(
            ["device_id"],
            ["agent_devices.id"],
            name="agent_capability_leases_device_id_fkey",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("jti", name="uq_agent_capability_leases_jti"),
        sa.UniqueConstraint(
            "token_hash",
            name="uq_agent_capability_leases_token_hash",
        ),
    )
    op.create_index(
        "ix_agent_capability_leases_principal_id",
        "agent_capability_leases",
        ["principal_id"],
    )
    op.create_index(
        "ix_agent_capability_leases_device_id",
        "agent_capability_leases",
        ["device_id"],
    )
    op.create_index(
        "ix_agent_capability_lease_active",
        "agent_capability_leases",
        ["device_id", "expires_at", "revoked_at"],
    )

    op.create_table(
        "agent_dpop_replays",
        sa.Column("device_id", sa.String(length=36), nullable=False),
        sa.Column("jti", sa.String(length=128), nullable=False),
        sa.Column("seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["device_id"],
            ["agent_devices.id"],
            name="agent_dpop_replays_device_id_fkey",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("device_id", "jti"),
    )
    op.create_index(
        "ix_agent_dpop_replays_expires_at",
        "agent_dpop_replays",
        ["expires_at"],
    )

    op.create_table(
        "agent_control",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("mutations_enabled", sa.Boolean(), nullable=False),
        sa.Column("shadow_mode", sa.Boolean(), nullable=False),
        sa.Column("enabled_risk_levels", sa.JSON(), nullable=False),
        sa.Column("allow_delete_without_recovery", sa.Boolean(), nullable=False),
        sa.Column("allow_network_change_without_oob", sa.Boolean(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_by", sa.String(), nullable=True),
        sa.CheckConstraint("id = 1", name="ck_agent_control_singleton"),
        sa.PrimaryKeyConstraint("id"),
    )
    control = sa.table(
        "agent_control",
        sa.column("id", sa.Integer()),
        sa.column("mutations_enabled", sa.Boolean()),
        sa.column("shadow_mode", sa.Boolean()),
        sa.column("enabled_risk_levels", sa.JSON()),
        sa.column("allow_delete_without_recovery", sa.Boolean()),
        sa.column("allow_network_change_without_oob", sa.Boolean()),
        sa.column("reason", sa.Text()),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    op.bulk_insert(
        control,
        [{
            "id": 1,
            "mutations_enabled": False,
            "shadow_mode": True,
            "enabled_risk_levels": ["R1"],
            "allow_delete_without_recovery": False,
            "allow_network_change_without_oob": False,
            "reason": "初期read-only/shadow mode",
            "updated_at": datetime.now(UTC),
        }],
    )

    op.create_table(
        "agent_audit_events",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("retention_until", sa.DateTime(timezone=True), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("actor_id", sa.String(), nullable=False),
        sa.Column("device_id", sa.String(length=36), nullable=True),
        sa.Column("lease_id", sa.String(length=36), nullable=True),
        sa.Column("action_id", sa.String(length=128), nullable=True),
        sa.Column("resource_type", sa.String(length=64), nullable=True),
        sa.Column("resource_id", sa.String(length=256), nullable=True),
        sa.Column("project_id", sa.String(length=64), nullable=True),
        sa.Column("node_id", sa.String(length=256), nullable=True),
        sa.Column("request_hash", sa.String(length=64), nullable=True),
        sa.Column("policy_decision", sa.String(length=16), nullable=False),
        sa.Column("operation_id", sa.String(length=36), nullable=True),
        sa.Column("correlation_id", sa.String(length=36), nullable=True),
        sa.Column("outcome", sa.String(length=32), nullable=True),
        sa.Column("detail", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in (
        "event_type",
        "actor_id",
        "device_id",
        "lease_id",
        "action_id",
        "operation_id",
        "correlation_id",
    ):
        op.create_index(
            f"ix_agent_audit_events_{column}",
            "agent_audit_events",
            [column],
        )

    if op.get_bind().dialect.name == "postgresql":
        op.execute(
            """
            CREATE FUNCTION virty_reject_agent_audit_mutation()
            RETURNS trigger AS $$
            BEGIN
              RAISE EXCEPTION 'agent_audit_events is append-only';
            END;
            $$ LANGUAGE plpgsql
            """
        )
        op.execute(
            """
            CREATE TRIGGER trg_agent_audit_events_append_only
            BEFORE UPDATE OR DELETE ON agent_audit_events
            FOR EACH ROW EXECUTE FUNCTION virty_reject_agent_audit_mutation()
            """
        )


def downgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.execute(
            "DROP TRIGGER IF EXISTS trg_agent_audit_events_append_only "
            "ON agent_audit_events"
        )
        op.execute("DROP FUNCTION IF EXISTS virty_reject_agent_audit_mutation()")

    op.drop_table("agent_audit_events")
    op.drop_table("agent_dpop_replays")
    op.drop_table("agent_capability_leases")
    op.drop_table("agent_lease_requests")
    op.drop_table("agent_webauthn_challenges")
    op.drop_table("agent_webauthn_credentials")
    op.drop_table("agent_pairings")
    op.drop_table("agent_control")
    op.drop_table("agent_devices")

    op.drop_constraint("domains_owner_user_id_fkey", "domains", type_="foreignkey")
    op.drop_constraint("domains_owner_project_id_fkey", "domains", type_="foreignkey")
    op.create_foreign_key(
        "domains_owner_user_id_fkey",
        "domains",
        "users",
        ["owner_user_id"],
        ["username"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "domains_owner_project_id_fkey",
        "domains",
        "projects",
        ["owner_project_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )
    op.drop_table("domain_console_tickets")
    op.add_column("domains", sa.Column("vnc_password", sa.String(), nullable=True))
