from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)

from mixin.database import Base


class TaskModel(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        UniqueConstraint(
            "principal_id",
            "idempotency_key",
            name="uq_tasks_principal_id_idempotency_key",
        ),
    )

    uuid = Column(String, primary_key=True, index=True)
    post_time = Column(DateTime(timezone=True))
    start_time = Column(DateTime(timezone=True))
    update_time = Column(DateTime(timezone=True))
    run_time = Column(Float)
    user_id = Column(
        String,
        ForeignKey(
            "users.username",
            onupdate="CASCADE",
            ondelete="SET NULL",
        ),
    )
    dependence_uuid = Column(
        String,
        ForeignKey(
            "tasks.uuid",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
    )
    status = Column(String)  # init, start, finish
    resource = Column(String)  # node, domain, network...
    object = Column(String)  # base, power...
    method = Column(String)  # delete, post, update...
    request = Column(JSON)
    result = Column(JSON)
    message = Column(String)
    log = Column(Text)

    # Agent経路のtask metadata。既存REST taskではnullableのまま利用できる。
    principal_id = Column(String, index=True)
    idempotency_key = Column(String)
    request_hash = Column(String)
    agent_request_hash = Column(String(64))
    correlation_id = Column(String, index=True)
    lease_id = Column(String, index=True)
    risk = Column(String)
    resolved_targets = Column(JSON)
    expected_generation = Column(JSON)
    error_code = Column(String)
    retryable = Column(Boolean)
    archived_at = Column(DateTime(timezone=True))

    def write_log(self, msg: object) -> None:
        self.log = self.log + str(msg) if self.log else str(msg)


class TaskTargetReservationModel(Base):
    __tablename__ = "task_target_reservations"
    __table_args__ = (
        UniqueConstraint(
            "target_key",
            "correlation_id",
            name="uq_task_target_reservations_target_correlation",
        ),
        CheckConstraint(
            "lock_mode IN ('shared', 'exclusive')",
            name="ck_task_target_reservations_lock_mode",
        ),
    )

    reservation_id = Column(String(64), primary_key=True)
    target_key = Column(String(64), nullable=False, index=True)
    lock_mode = Column(String(16), nullable=False)
    correlation_id = Column(String, nullable=False, index=True)
    lease_id = Column(String, nullable=False, index=True)
    acquired_at = Column(DateTime(timezone=True), nullable=False)
