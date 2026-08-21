"""Agent taskの安全性metadataを追加する。

Revision ID: 9f2c6a8e41d7
Revises: 04543573864a
Create Date: 2026-08-22 09:00:00

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9f2c6a8e41d7"
down_revision = "04543573864a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("tasks_user_id_fkey", "tasks", type_="foreignkey")
    op.create_foreign_key(
        "tasks_user_id_fkey",
        "tasks",
        "users",
        ["user_id"],
        ["username"],
        onupdate="CASCADE",
        ondelete="SET NULL",
    )
    op.add_column("tasks", sa.Column("principal_id", sa.String(), nullable=True))
    op.add_column("tasks", sa.Column("idempotency_key", sa.String(), nullable=True))
    op.add_column("tasks", sa.Column("request_hash", sa.String(), nullable=True))
    op.add_column(
        "tasks",
        sa.Column("agent_request_hash", sa.String(length=64), nullable=True),
    )
    op.add_column("tasks", sa.Column("correlation_id", sa.String(), nullable=True))
    op.add_column("tasks", sa.Column("lease_id", sa.String(), nullable=True))
    op.add_column("tasks", sa.Column("risk", sa.String(), nullable=True))
    op.add_column("tasks", sa.Column("resolved_targets", sa.JSON(), nullable=True))
    op.add_column("tasks", sa.Column("expected_generation", sa.JSON(), nullable=True))
    op.add_column("tasks", sa.Column("error_code", sa.String(), nullable=True))
    op.add_column("tasks", sa.Column("retryable", sa.Boolean(), nullable=True))
    op.add_column(
        "tasks",
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
    )

    # 既存taskも所有者確認とoperation集約に利用できるようbackfillする。
    op.execute(
        "UPDATE tasks SET principal_id = user_id WHERE principal_id IS NULL"
    )
    op.execute(
        "UPDATE tasks SET correlation_id = uuid WHERE correlation_id IS NULL"
    )

    op.create_index("ix_tasks_principal_id", "tasks", ["principal_id"])
    op.create_index("ix_tasks_correlation_id", "tasks", ["correlation_id"])
    op.create_index("ix_tasks_lease_id", "tasks", ["lease_id"])
    op.create_unique_constraint(
        "uq_tasks_principal_id_idempotency_key",
        "tasks",
        ["principal_id", "idempotency_key"],
    )
    op.create_table(
        "task_target_reservations",
        sa.Column("reservation_id", sa.String(length=64), nullable=False),
        sa.Column("target_key", sa.String(length=64), nullable=False),
        sa.Column("lock_mode", sa.String(length=16), nullable=False),
        sa.Column("correlation_id", sa.String(), nullable=False),
        sa.Column("lease_id", sa.String(), nullable=False),
        sa.Column(
            "acquired_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.CheckConstraint(
            "lock_mode IN ('shared', 'exclusive')",
            name="ck_task_target_reservations_lock_mode",
        ),
        sa.PrimaryKeyConstraint("reservation_id"),
        sa.UniqueConstraint(
            "target_key",
            "correlation_id",
            name="uq_task_target_reservations_target_correlation",
        ),
    )
    op.create_index(
        "ix_task_target_reservations_target_key",
        "task_target_reservations",
        ["target_key"],
    )
    op.create_index(
        "ix_task_target_reservations_correlation_id",
        "task_target_reservations",
        ["correlation_id"],
    )
    op.create_index(
        "ix_task_target_reservations_lease_id",
        "task_target_reservations",
        ["lease_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_task_target_reservations_lease_id",
        table_name="task_target_reservations",
    )
    op.drop_index(
        "ix_task_target_reservations_correlation_id",
        table_name="task_target_reservations",
    )
    op.drop_index(
        "ix_task_target_reservations_target_key",
        table_name="task_target_reservations",
    )
    op.drop_table("task_target_reservations")
    op.drop_constraint(
        "uq_tasks_principal_id_idempotency_key",
        "tasks",
        type_="unique",
    )
    op.drop_index("ix_tasks_lease_id", table_name="tasks")
    op.drop_index("ix_tasks_correlation_id", table_name="tasks")
    op.drop_index("ix_tasks_principal_id", table_name="tasks")

    op.drop_column("tasks", "archived_at")
    op.drop_column("tasks", "retryable")
    op.drop_column("tasks", "error_code")
    op.drop_column("tasks", "expected_generation")
    op.drop_column("tasks", "resolved_targets")
    op.drop_column("tasks", "risk")
    op.drop_column("tasks", "lease_id")
    op.drop_column("tasks", "correlation_id")
    op.drop_column("tasks", "agent_request_hash")
    op.drop_column("tasks", "request_hash")
    op.drop_column("tasks", "idempotency_key")
    op.drop_column("tasks", "principal_id")
    op.drop_constraint("tasks_user_id_fkey", "tasks", type_="foreignkey")
    op.create_foreign_key(
        "tasks_user_id_fkey",
        "tasks",
        "users",
        ["user_id"],
        ["username"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )
