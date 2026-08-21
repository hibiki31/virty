from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from mixin.database import Base


class TaskModel(Base):
    __tablename__ = "tasks"
    uuid: Mapped[str] = Column(String, primary_key=True, index=True)
    post_time: Mapped[datetime] = Column(DateTime(timezone=True))
    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    update_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    run_time: Mapped[float | None] = mapped_column(Float, nullable=True)
    user_id: Mapped[str] = Column(String, ForeignKey(
        'users.username', 
        onupdate='CASCADE', 
        ondelete='CASCADE'
    ))
    dependence_uuid: Mapped[str | None] = mapped_column(String, ForeignKey(
        'tasks.uuid', 
        onupdate='CASCADE', 
        ondelete='CASCADE'
    ), nullable=True)
    status: Mapped[str] = Column(String) # init, start, finish
    resource: Mapped[str] = Column(String) # node, domain, network...
    object: Mapped[str] = Column(String) # base, power...
    method: Mapped[str] = Column(String) # delete, post, update...
    request: Mapped[str] = Column(JSON)
    result: Mapped[dict[str, Any] | None] = Column(JSON)
    message: Mapped[str | None] = mapped_column(String, nullable=True)
    log: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    def write_log(self, msg: Any) -> None:
        self.log = self.log + str(msg) if self.log else str(msg)
