from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from mixin.database import Base, Engine

from storage.models import StorageModel

node_to_noderole_table = Table('node_to_noderole', Base.metadata,
    Column('node_name', String, ForeignKey('nodes.name')),
    Column('role_id', String, ForeignKey('nodesrole.name'))
)


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
    storages = relationship('StorageModel', uselist=True, lazy=False, backref="node")
    roles = relationship("NodeRoleModel", secondary=node_to_noderole_table, back_populates="nodes", lazy=False)


class NodeRoleModel(Base):
    __tablename__ = "nodesrole"
    name = Column(String, primary_key=True, index=True)
    nodes = relationship("NodeModel", secondary=node_to_noderole_table, back_populates="roles",lazy=False)