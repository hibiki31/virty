from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mixin.database import Base

if TYPE_CHECKING:
    from node.models import NodeModel
    from project.models import ProjectModel
    from user.models import UserModel


class DomainModel(Base):
    __tablename__ = "domains"
    uuid: Mapped[str] = Column(String, primary_key=True, index=True)
    # name@user
    name: Mapped[str] = Column(String)
    core: Mapped[int] = Column(Integer)
    memory: Mapped[int] = Column(Integer)
    status: Mapped[int] = Column(Integer)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    update_token: Mapped[str] = Column(String)
    vnc_port: Mapped[str | None] = mapped_column(String, nullable=True)
    vnc_password: Mapped[str | None] = mapped_column(String, nullable=True)
    
    # Cache
    storage_used: Mapped[int] = Column(Integer, default=0)

    # One to Many
    interfaces: Mapped[list["DomainInterfaceModel"]] = relationship('DomainInterfaceModel')
    drives: Mapped[list["DomainDriveModel"]] = relationship('DomainDriveModel')

    # Many to One
    node: Mapped["NodeModel"] = relationship('NodeModel')
    node_name: Mapped[str] = Column(String, ForeignKey('nodes.name', onupdate='CASCADE', ondelete='CASCADE'))
    owner_user: Mapped["UserModel | None"] = relationship("UserModel")
    owner_user_id: Mapped[str | None] = mapped_column(String, ForeignKey('users.username', onupdate='CASCADE', ondelete='CASCADE'), nullable=True)
    owner_project: Mapped["ProjectModel | None"] = relationship("ProjectModel")
    owner_project_id: Mapped[str | None] = mapped_column(String, ForeignKey('projects.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=True)

class DomainInterfaceModel(Base):
    __tablename__ = "domains_interfaces"
    domain_uuid: Mapped[str] = Column(String, ForeignKey('domains.uuid', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    mac: Mapped[str] = Column(String, primary_key=True)
    type: Mapped[str] = Column(String)
    target: Mapped[str | None] = mapped_column(String, nullable=True)
    bridge: Mapped[str | None] = mapped_column(String, nullable=True)
    network: Mapped[str | None] = mapped_column(String, nullable=True)
    port: Mapped[str | None] = mapped_column(String, nullable=True)
    update_token: Mapped[str] = Column(String)


class DomainDriveModel(Base):
    __tablename__ = "domains_drives"
    domain_uuid: Mapped[str] = Column(String, ForeignKey('domains.uuid', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    target: Mapped[str] = Column(String, primary_key=True)
    device: Mapped[str] = Column(String)
    type: Mapped[str] = Column(String)
    source: Mapped[str | None] = mapped_column(String, nullable=True)
    update_token: Mapped[str] = Column(String)
