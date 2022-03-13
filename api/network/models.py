from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from mixin.database import Base


associations_networks_pools = Table('associations_networks_pools', Base.metadata,
    Column('pool_id', Integer, ForeignKey('networks_pools.id', onupdate='CASCADE', ondelete='CASCADE')),
    Column('port_id', Integer, ForeignKey('networks_portgroups.id', onupdate='CASCADE', ondelete='CASCADE'))
)

associations_networks = Table('associations_networks', Base.metadata,
    Column('pool_id', Integer, ForeignKey('networks_pools.id', onupdate='CASCADE', ondelete='CASCADE')),
    Column('network_uuid', String, ForeignKey('networks.uuid', onupdate='CASCADE', ondelete='CASCADE'))
)


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
    id = Column(Integer, autoincrement=True, primary_key=True)
    network_uuid = Column(String, ForeignKey('networks.uuid', onupdate='CASCADE', ondelete='CASCADE'))
    name = Column(String)
    vlan_id = Column(String)
    is_default = Column(Boolean)
    update_token = Column(String)


class NetworkPoolModel(Base):
    __tablename__ = "networks_pools"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String)
    networks = relationship("NetworkModel", secondary=associations_networks, lazy=False)
    ports = relationship("NetworkPortgroupModel", secondary=associations_networks_pools, lazy=False)