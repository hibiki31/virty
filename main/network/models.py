from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from mixin.database import Base, Engine


class NetworkModel(Base):
    __tablename__ = "networks"
    uuid = Column(String, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    node_name = Column(String, ForeignKey('nodes.name', onupdate='CASCADE', ondelete='CASCADE'))
    host_interface = Column(String)
    type = Column(String)
    active = Column(Boolean)
    auto_start = Column(Boolean)
    dhcp = Column(Boolean)
    update_token = Column(String)