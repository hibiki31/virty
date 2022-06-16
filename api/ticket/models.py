from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, DateTime
from sqlalchemy.orm import relationship

from network.models import NetworkPoolModel

from mixin.database import Base

association_tickets_to_networks_pools = Table('tickets_to_networks_pools', Base.metadata,
    Column('tickets_id', Integer, ForeignKey('tickets.id', onupdate='CASCADE', ondelete='CASCADE')),
    Column('networks_pools_id', Integer, ForeignKey('networks_pools.id', onupdate='CASCADE', ondelete='CASCADE'))
)

association_tickets_to_storages_pools = Table('tickets_to_storages_pools', Base.metadata,
    Column('tickets_id', Integer, ForeignKey('tickets.id', onupdate='CASCADE', ondelete='CASCADE')),
    Column('storages_pools_id', Integer, ForeignKey('storages_pools.id', onupdate='CASCADE', ondelete='CASCADE'))
)

association_tickets_to_flavors_pools = Table('tickets_to_flavors_pools', Base.metadata,
    Column('tickets_id', Integer, ForeignKey('tickets.id', onupdate='CASCADE', ondelete='CASCADE')),
    Column('flavors_id', Integer, ForeignKey('flavors.id', onupdate='CASCADE', ondelete='CASCADE'))
)


class TicketModel(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    core = Column(Integer, nullable=False, default=1)
    memory = Column(Integer, nullable=False, default=1024)
    storage_capacity_g = Column(Integer, default=0)
    network_pools = relationship("NetworkPoolModel", secondary=association_tickets_to_networks_pools, lazy=False)
    storage_pools = relationship("StoragePoolModel", secondary=association_tickets_to_storages_pools, lazy=False)
    flavors = relationship("FlavorModel", secondary=association_tickets_to_flavors_pools, lazy=False)
    user_installable = Column(Boolean, nullable=False, default=True)
    isolated_networks = Column(Integer, nullable=False, default=3)


class IssuanceModel(Base):
    __tablename__ = "issuances"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    issued_date = Column(DateTime, nullable=False)
    issued_by = Column(String, ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'))
    project_id = Column(String(6), ForeignKey('projects.id', onupdate='CASCADE', ondelete='CASCADE'))
    project = relationship("ProjectModel")
    ticket_id = Column(Integer, ForeignKey('tickets.id', onupdate='CASCADE', ondelete='CASCADE'))
    ticket = relationship("TicketModel")
