from datetime import datetime
from typing import Any

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
from sqlalchemy.orm import Mapped

from mixin.database import Base


class TaskModel(Base):
    __tablename__ = "tasks"
    __allow_unmapped__ = True
    __table_args__ = (
        UniqueConstraint(
            "principal_id",
            "idempotency_key",
            name="uq_tasks_principal_id_idempotency_key",
        ),
    )

    uuid: Mapped[str] = Column(String, primary_key=True, index=True)
    post_time: Mapped[datetime] = Column(DateTime(timezone=True))
    # legacy declarative baseのpluginはnullableなColumn RHSを非Optionalと推論する。
    # DBのnullable契約はMapped側へ明示し、誤った推論だけを局所的に抑止する。
    start_time: Mapped[datetime | None] = Column(  # type: ignore[misc]
        DateTime(timezone=True),
        nullable=True,
    )
    update_time: Mapped[datetime | None] = Column(  # type: ignore[misc]
        DateTime(timezone=True),
        nullable=True,
    )
    run_time: Mapped[float | None] = Column(Float, nullable=True)  # type: ignore[misc]
    user_id: Mapped[str | None] = Column(  # type: ignore[misc]
        String,
        ForeignKey(
            "users.username",
            onupdate="CASCADE",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    dependence_uuid: Mapped[str | None] = Column(  # type: ignore[misc]
        String,
        ForeignKey(
            "tasks.uuid",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=True,
    )
    status: Mapped[str] = Column(String)  # init, start, finish
    resource: Mapped[str] = Column(String)  # node, domain, network...
    object: Mapped[str] = Column(String)  # base, power...
    method: Mapped[str] = Column(String)  # delete, post, update...
    request: Mapped[str] = Column(JSON)
    result: Mapped[dict[str, Any] | None] = Column(JSON, nullable=True)
    message: Mapped[str | None] = Column(String, nullable=True)  # type: ignore[misc]
    log: Mapped[str | None] = Column(Text, nullable=True)  # type: ignore[misc]

    # Agent経路のtask metadata。既存REST taskではnullableのまま利用できる。
    principal_id: Mapped[str | None] = Column(  # type: ignore[misc]
        String,
        nullable=True,
        index=True,
    )
    idempotency_key: Mapped[str | None] = Column(String, nullable=True)  # type: ignore[misc]
    request_hash: Mapped[str | None] = Column(String, nullable=True)  # type: ignore[misc]
    agent_request_hash: Mapped[str | None] = Column(  # type: ignore[misc]
        String(64),
        nullable=True,
    )
    correlation_id: Mapped[str | None] = Column(  # type: ignore[misc]
        String,
        nullable=True,
        index=True,
    )
    lease_id: Mapped[str | None] = Column(  # type: ignore[misc]
        String,
        nullable=True,
        index=True,
    )
    risk: Mapped[str | None] = Column(String, nullable=True)  # type: ignore[misc]
    resolved_targets: Mapped[list[Any] | None] = Column(JSON, nullable=True)
    expected_generation: Mapped[Any | None] = Column(JSON, nullable=True)
    error_code: Mapped[str | None] = Column(String, nullable=True)  # type: ignore[misc]
    retryable: Mapped[bool | None] = Column(Boolean, nullable=True)  # type: ignore[misc]
    archived_at: Mapped[datetime | None] = Column(  # type: ignore[misc]
        DateTime(timezone=True),
        nullable=True,
    )
    # 永続化せず、同一process内のcommit呼出し結果だけを通知する。
    idempotency_replayed: bool = False

    def write_log(self, msg: Any) -> None:
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

    reservation_id: Mapped[str] = Column(String(64), primary_key=True)
    target_key: Mapped[str] = Column(
        String(64),
        nullable=False,
        index=True,
    )
    lock_mode: Mapped[str] = Column(String(16), nullable=False)
    correlation_id: Mapped[str] = Column(
        String,
        nullable=False,
        index=True,
    )
    lease_id: Mapped[str] = Column(
        String,
        nullable=False,
        index=True,
    )
    acquired_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        nullable=False,
    )
