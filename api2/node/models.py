from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class NodeModel(Base):
    __tablename__ = "nodes"
    # 必須レコード
    uuid: Mapped[str] = mapped_column(primary_key=True)
    state: Mapped[str] = mapped_column()
    record: Mapped[JSON] = mapped_column(type_=JSON, nullable=False)
    message: Mapped[str] = mapped_column()
    
    hostname: Mapped[str] = mapped_column()
    core: Mapped[int] = mapped_column()
    memory_mb: Mapped[int] = mapped_column()