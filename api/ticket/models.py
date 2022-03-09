from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, DateTime
from sqlalchemy.orm import relationship

from network.models import NetworkPoolModel

from mixin.database import Base

association_tickets_to_networks_pools = Table('tickets_to_networks_pools', Base.metadata,
    Column('tickets_id', Integer, ForeignKey('tickets.id')),
    Column('networks_pools_id', Integer, ForeignKey('networks_pools.id'))
)

association_tickets_to_storages_pools = Table('tickets_to_storages_pools', Base.metadata,
    Column('tickets_id', Integer, ForeignKey('tickets.id')),
    Column('storages_pools_id', Integer, ForeignKey('storages_pools.id'))
)

association_tickets_to_flavors_pools = Table('tickets_to_flavors_pools', Base.metadata,
    Column('tickets_id', Integer, ForeignKey('tickets.id')),
    Column('flavors_id', Integer, ForeignKey('flavors.id'))
)


class TicketModel(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    core = Column(Integer, nullable=False, default=1)
    memory = Column(Integer, nullable=False, default=1024)
    network_pools = relationship("NetworkPoolModel", secondary=association_tickets_to_networks_pools, lazy=False)
    storage_pools = relationship("StoragePoolModel", secondary=association_tickets_to_storages_pools, lazy=False)
    flavors = relationship("FlavorModel", secondary=association_tickets_to_flavors_pools, lazy=False)
    user_installable = Column(Boolean, nullable=False, default=True)
    isolated_networks = Column(Integer, nullable=False, default=3)


class IssuanceModel(Base):
    __tablename__ = "issuances"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date = Column(DateTime, nullable=False)
    issued_by = Column(String, ForeignKey('users.id'))
    user_id = Column(String, ForeignKey('users.id'))
    ticket_id = Column(Integer, ForeignKey('tickets.id'))
    ticket = relationship("TicketModel")
