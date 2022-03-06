from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from mixin.database import Base


class NetworkModel(Base):
    __tablename__ = "networks"
    uuid = Column(String, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    node_name = Column(String, ForeignKey('nodes.name', onupdate='CASCADE', ondelete='CASCADE'))
    bridge = Column(String)
    type = Column(String)
    active = Column(Boolean)
    auto_start = Column(Boolean)
    dhcp = Column(Boolean)
    update_token = Column(String)
    ip = Column(String)
    mac = Column(String)
    portgroups = relationship('NetworkPortgroupModel')


class NetworkPortgroupModel(Base):
    __tablename__ = "networks_portgroups"
    network_uuid = Column(String, ForeignKey('networks.uuid', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    name = Column(String, primary_key=True)
    vlan_id = Column(String)
    is_default = Column(Boolean)
    update_token = Column(String)