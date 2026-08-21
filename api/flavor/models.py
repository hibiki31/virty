from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import Mapped

from mixin.database import Base


# OS icon by https://icon-icons.com/
class FlavorModel(Base):
    __tablename__ = "flavors"
    id: Mapped[int] = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = Column(String, unique=True, nullable=False)
    os: Mapped[str] = Column(String, nullable=False)
    manual_url: Mapped[str] = Column(String, nullable=False)
    icon: Mapped[str] = Column(String, nullable=False)
    cloud_init_ready: Mapped[bool] = Column(Boolean, nullable=False, default=False)
    cloud_init_user: Mapped[str] = Column(String, nullable=False, default="cloud-user")
    description: Mapped[str] = Column(String, nullable=False)
