from sqlalchemy import Boolean, Column, Integer, String

from mixin.database import Base


# OS icon by https://icon-icons.com/
class FlavorModel(Base):
    __tablename__ = "flavors"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    os = Column(String, nullable=False)
    manual_url = Column(String, nullable=False)
    icon = Column(String, nullable=False)
    cloud_init_ready = Column(Boolean, nullable=False, default=False)
    cloud_init_user = Column(String, nullable=False, default="cloud-user")
    description = Column(String, nullable=False)