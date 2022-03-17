from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from mixin.database import Base, Engine


class DomainModel(Base):
    __tablename__ = "domains"
    uuid = Column(String, primary_key=True, index=True)
    # name@user
    name = Column(String)
    core = Column(Integer)
    memory = Column(Integer)
    status = Column(Integer)
    description = Column(String)
    update_token = Column(String)
    vnc_port = Column(String)
    vnc_password = Column(String)
    
    # One to Many
    interfaces = relationship('DomainInterfaceModel')
    drives = relationship('DomainDriveModel')

    # Many to One
    node = relationship('NodeModel')
    node_name = Column(String, ForeignKey('nodes.name', onupdate='CASCADE', ondelete='CASCADE'))
    owner_user = relationship("UserModel")
    owner_user_id = Column(String, ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'))
    owner_project = relationship("ProjectModel")
    owner_project_id = Column(String, ForeignKey('projects.id', onupdate='CASCADE', ondelete='CASCADE'))
    issuance_id = Column(Integer, ForeignKey('issuances.id', onupdate='CASCADE', ondelete='SET NULL'))


class DomainInterfaceModel(Base):
    __tablename__ = "domains_interfaces"
    domain_uuid = Column(String, ForeignKey('domains.uuid', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    mac = Column(String, primary_key=True)
    type = Column(String)
    target = Column(String)
    bridge = Column(String)
    network = Column(String)
    port = Column(String)
    update_token = Column(String)


class DomainDriveModel(Base):
    __tablename__ = "domains_drives"
    domain_uuid = Column(String, ForeignKey('domains.uuid', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    target = Column(String, primary_key=True)
    device = Column(String)
    type = Column(String)
    source = Column(String)
    update_token = Column(String)