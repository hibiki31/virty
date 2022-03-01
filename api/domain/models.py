from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from mixin.database import Base, Engine


class DomainModel(Base):
    __tablename__ = "domains"
    uuid = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True)
    core = Column(Integer)
    memory = Column(Integer)
    status = Column(Integer)
    description = Column(String)
    owner_user_id = Column(String, ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'))
    owner_group_id = Column(String, ForeignKey('groups.id', onupdate='CASCADE', ondelete='CASCADE'))
    owner_group = relationship("GroupModel")
    node_name = Column(String, ForeignKey('nodes.name', onupdate='CASCADE', ondelete='CASCADE'))
    interface = relationship('DomainInterfaceModel')
    drive = relationship('DomainDriveModel')
    vnc_token = relationship('DomainVNCTokenModel')
    update_token = Column(String)

class DomainVNCTokenModel(Base):
    __tablename__ = "domain_vnc_token"
    domain_uuid = Column(String, ForeignKey('domains.uuid', onupdate='CASCADE', ondelete='CASCADE'))
    token = Column(String)
    node_domain = Column(String, primary_key=True)
    node_port = Column(Integer, primary_key=True)



class DomainInterfaceModel(Base):
    __tablename__ = "domains_interfaces"
    domain_uuid = Column(String, ForeignKey('domains.uuid', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    mac = Column(String, primary_key=True)
    type = Column(String)
    target = Column(String)
    source = Column(String)
    network = Column(String)
    update_token = Column(String)


class DomainDriveModel(Base):
    __tablename__ = "domains_drives"
    domain_uuid = Column(String, ForeignKey('domains.uuid', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    target = Column(String, primary_key=True)
    type = Column(String)
    source = Column(String)
    update_token = Column(String)