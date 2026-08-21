from typing import Any, TYPE_CHECKING

from sqlalchemy import JSON, Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mixin.database import Base

if TYPE_CHECKING:
    from storage.models import StorageModel


class NodeModel(Base):
    __tablename__ = "nodes"
    name: Mapped[str] = Column(String, primary_key=True, index=True)
    description: Mapped[str] = Column(String)
    domain: Mapped[str] = Column(String)
    user_name: Mapped[str] = Column(String)
    port: Mapped[int] = Column(Integer)
    core: Mapped[int] = Column(Integer)
    memory: Mapped[int] = Column(Integer)
    cpu_gen: Mapped[str] = Column(String)
    os_like: Mapped[str] = Column(String)
    os_name: Mapped[str] = Column(String)
    os_version: Mapped[str] = Column(String)
    status: Mapped[int] = Column(Integer)
    qemu_version: Mapped[str | None] = mapped_column(String, nullable=True)
    libvirt_version: Mapped[str | None] = mapped_column(String, nullable=True)
    storages: Mapped[list["StorageModel"]] = relationship('StorageModel', uselist=True, lazy=False, backref="node")
    ansible_facts: Mapped[dict[str, Any]] = Column(JSON)
    roles: Mapped[list["AssociationNodeToRoleModel"]] = relationship("AssociationNodeToRoleModel", back_populates="node")


class NodeRoleModel(Base):
    __tablename__ = "nodesrole"
    name: Mapped[str] = Column(String, primary_key=True, index=True)
    nodes: Mapped[list["AssociationNodeToRoleModel"]] = relationship("AssociationNodeToRoleModel", back_populates="role")


class AssociationNodeToRoleModel(Base):
    __tablename__ = 'association_node_to_role'
    node_name: Mapped[str] = Column(String, ForeignKey('nodes.name', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    role_name: Mapped[str] = Column(String, ForeignKey('nodesrole.name', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    extra_json: Mapped[dict[str, Any]] = Column(JSON)
    role: Mapped[NodeRoleModel] = relationship("NodeRoleModel", back_populates="nodes", lazy=False)
    node: Mapped[NodeModel] = relationship("NodeModel", back_populates="roles")


class AssociationPoolsCpuModel(Base):
    __tablename__ = 'association_pools_cpu'
    pool_id: Mapped[int] = Column(Integer, ForeignKey('pools_cpu.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    node_name: Mapped[str] = Column(String, ForeignKey('nodes.name', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    core: Mapped[int] = Column(Integer, default=0)
    nodes: Mapped[NodeModel] = relationship("NodeModel", lazy=False)


class PoolCpuModel(Base):
    __tablename__ = "pools_cpu"
    id: Mapped[int] = Column(Integer, autoincrement=True, primary_key=True)
    name: Mapped[str] = Column(String)
    nodes: Mapped[list[AssociationPoolsCpuModel]] = relationship("AssociationPoolsCpuModel", lazy=False)
