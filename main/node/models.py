from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from mixin.database import Base, Engine


class NodeModel(Base):
    __tablename__ = "nodes"
    name = Column(String, primary_key=True, index=True)
    description = Column(String)
    domain = Column(String)
    user_name = Column(String)
    port = Column(Integer)
    core = Column(Integer)
    memory = Column(Integer)
    cpu_gen = Column(String)
    os_like = Column(String)
    os_name = Column(String)
    os_version = Column(String)
    status = Column(Integer)
    qemu_version = Column(String)
    libvirt_version = Column(String)