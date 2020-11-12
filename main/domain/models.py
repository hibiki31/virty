from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from mixin.database import Base, Engine


class DomainModel(Base):
    __tablename__ = "domains"
    uuid = Column(String, primary_key=True, index=True)
    name = Column(String)
    core = Column(Integer)
    memory = Column(Integer)
    status = Column(Integer)
    description = Column(String)
    owner_user = Column(String, ForeignKey('users.user_id', onupdate='CASCADE', ondelete='CASCADE'))
    owner_group = Column(String, ForeignKey('groups.group_id', onupdate='CASCADE', ondelete='CASCADE'))
    node_name = Column(String, ForeignKey('nodes.name', onupdate='CASCADE', ondelete='CASCADE'))
    interface = relationship('DomainInterfaceModel')
    drive = relationship('DomainDriveModel')
    is_lost = Column(Boolean)

class DomainInterfaceModel(Base):
    __tablename__ = "domains_interfaces"
    domain_uuid = Column(String, ForeignKey('domains.uuid', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    mac = Column(String, primary_key=True)
    type = Column(String)
    target = Column(String)
    source = Column(String)
    network = Column(String)
    is_updating = Column(Boolean)

class DomainDriveModel(Base):
    __tablename__ = "domains_drives"
    domain_uuid = Column(String, ForeignKey('domains.uuid', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    target = Column(String, primary_key=True)
    type = Column(String)
    source = Column(String)
    is_updating = Column(Boolean)