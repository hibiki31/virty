from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from mixin.database import Base
from user.models import association_users_to_projects

from random import randint


association_projects_to_networks_pools = Table('projects_to_networks_pools', Base.metadata,
    Column('projects_id', String(6), ForeignKey('projects.id', onupdate='CASCADE', ondelete='CASCADE')),
    Column('networks_pools_id', Integer, ForeignKey('networks_pools.id', onupdate='CASCADE', ondelete='CASCADE'))
)

association_projects_to_storages_pools = Table('projects_to_storages_pools', Base.metadata,
    Column('projects_id', String(6), ForeignKey('projects.id', onupdate='CASCADE', ondelete='CASCADE')),
    Column('storages_pools_id', Integer, ForeignKey('storages_pools.id', onupdate='CASCADE', ondelete='CASCADE'))
)

association_projects_to_flavors_pools = Table('projects_to_flavors_pools', Base.metadata,
    Column('projects_id', String(6), ForeignKey('projects.id', onupdate='CASCADE', ondelete='CASCADE')),
    Column('flavors_id', Integer, ForeignKey('flavors.id', onupdate='CASCADE', ondelete='CASCADE'))
)



def generate_project_id():
    return '{:06x}'.format(randint(1,2**24))


class ProjectModel(Base):
    __tablename__ = "projects"
    id = Column(String(6), primary_key=True, index=True, default=generate_project_id)
    name = Column(String)
    users = relationship("UserModel", secondary=association_users_to_projects, back_populates="projects", lazy=False)
    domains = relationship("DomainModel", backref="project")
    # limit
    is_admin = Column(Boolean, nullable=False, default=False)
    core = Column(Integer, nullable=False, default=4)
    memory_g = Column(Integer, nullable=False, default=1)
    storage_capacity_g = Column(Integer, default=64)
    network_pools = relationship("NetworkPoolModel", secondary=association_projects_to_networks_pools, lazy=False)
    storage_pools = relationship("StoragePoolModel", secondary=association_projects_to_storages_pools, lazy=False)
    flavors = relationship("FlavorModel", secondary=association_projects_to_flavors_pools, lazy=False)
    user_installable = Column(Boolean, nullable=False, default=True)



class ProjectPortsModel(Base):
    __tablename__ = "projects_ports"
    project_id = Column(String(6), ForeignKey('projects.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    vlan_id = Column(Integer, primary_key=True)
    name = Column(String)