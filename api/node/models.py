from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, JSON
from sqlalchemy.orm import relationship
from mixin.database import Base, Engine

from storage.models import StorageModel


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
    ansible_facts = Column(JSON)
    roles = relationship("AssociationNodeToRoleModel", back_populates="node")


class NodeRoleModel(Base):
    __tablename__ = "nodesrole"
    name = Column(String, primary_key=True, index=True)
    nodes = relationship("AssociationNodeToRoleModel", back_populates="role")


class AssociationNodeToRoleModel(Base):
    __tablename__ = 'association_node_to_role'
    node_name = Column(String, ForeignKey('nodes.name', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    role_name = Column(String, ForeignKey('nodesrole.name', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    extra_json = Column(JSON)
    role = relationship("NodeRoleModel", back_populates="nodes", lazy=False)
    node = relationship("NodeModel", back_populates="roles")


class AssociationPoolsCpuModel(Base):
    __tablename__ = 'association_pools_cpu'
    pool_id = Column(Integer, ForeignKey('pools_cpu.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    node_name = Column(String, ForeignKey('nodes.name', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    core = Column(Integer, default=0)
    nodes = relationship("NodeModel", lazy=False)


class PoolCpuModel(Base):
    __tablename__ = "pools_cpu"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String)
    nodes = relationship("AssociationPoolsCpuModel", lazy=False)