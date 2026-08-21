from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, ForeignKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from mixin.database import Base


associations_networks_pools = Table('associations_networks_pools', Base.metadata,
    Column('pool_id', Integer, ForeignKey('networks_pools.id', onupdate='CASCADE', ondelete='CASCADE')),
    Column('port_network_uuid', String, ForeignKey('networks.uuid', onupdate='CASCADE', ondelete='CASCADE')),
    Column('port_name', String),
    ForeignKeyConstraint(['port_network_uuid', 'port_name'], ['networks_portgroups.network_uuid', 'networks_portgroups.name']),
)

associations_networks = Table('associations_networks', Base.metadata,
    Column('pool_id', Integer, ForeignKey('networks_pools.id', onupdate='CASCADE', ondelete='CASCADE')),
    Column('network_uuid', String, ForeignKey('networks.uuid', onupdate='CASCADE', ondelete='CASCADE'))
)


class NetworkModel(Base):
    __tablename__ = "networks"
    uuid: Mapped[str] = Column(String, primary_key=True, index=True)
    name: Mapped[str] = Column(String)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    node_name: Mapped[str] = Column(String, ForeignKey('nodes.name', onupdate='CASCADE', ondelete='CASCADE'))
    bridge: Mapped[str] = Column(String)
    type: Mapped[str] = Column(String)
    active: Mapped[bool] = Column(Boolean)
    auto_start: Mapped[bool] = Column(Boolean)
    dhcp: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    update_token: Mapped[str] = Column(String)
    ip: Mapped[str | None] = mapped_column(String, nullable=True)
    mac: Mapped[str | None] = mapped_column(String, nullable=True)
    portgroups: Mapped[list["NetworkPortgroupModel"]] = relationship('NetworkPortgroupModel', viewonly=True)


class NetworkPortgroupModel(Base):
    __tablename__ = "networks_portgroups"
    network_uuid: Mapped[str] = Column(String, ForeignKey('networks.uuid', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    name: Mapped[str] = Column(String, primary_key=True)
    network: Mapped[NetworkModel] = relationship("NetworkModel")
    vlan_id: Mapped[str | None] = mapped_column(String, nullable=True)
    is_default: Mapped[bool] = Column(Boolean)
    update_token: Mapped[str] = Column(String)


class NetworkPoolModel(Base):
    __tablename__ = "networks_pools"
    id: Mapped[int] = Column(Integer, autoincrement=True, primary_key=True)
    name: Mapped[str] = Column(String)
    networks: Mapped[list[NetworkModel]] = relationship("NetworkModel", secondary=associations_networks, lazy=False)
    ports: Mapped[list[NetworkPortgroupModel]] = relationship("NetworkPortgroupModel", secondary=associations_networks_pools, lazy=False)
