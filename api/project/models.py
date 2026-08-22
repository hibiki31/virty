from random import randint
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, relationship

from mixin.database import Base
from user.models import association_users_to_projects

if TYPE_CHECKING:
    from domain.models import DomainModel
    from flavor.models import FlavorModel
    from network.models import NetworkPoolModel
    from storage.models import StoragePoolModel
    from user.models import UserModel

association_projects_to_networks_pools = Table(
    'projects_to_networks_pools', 
    Base.metadata,
    Column('projects_id', String(6), ForeignKey(
        'projects.id', 
        onupdate='CASCADE', 
        ondelete='CASCADE'
    )),
    Column('networks_pools_id', Integer, ForeignKey(
        'networks_pools.id', 
        onupdate='CASCADE', 
        ondelete='CASCADE'
    ))
)

association_projects_to_storages_pools = Table(
    'projects_to_storages_pools', 
    Base.metadata,
    Column('projects_id', String(6), ForeignKey(
        'projects.id', 
        onupdate='CASCADE', 
        ondelete='CASCADE'
    )),
    Column('storages_pools_id', Integer, ForeignKey(
        'storages_pools.id', 
        onupdate='CASCADE', 
        ondelete='CASCADE'
    ))
)

association_projects_to_flavors_pools = Table(
    'projects_to_flavors_pools', 
    Base.metadata,
    Column('projects_id', String(6), ForeignKey(
        'projects.id', 
        onupdate='CASCADE', 
        ondelete='CASCADE'
    )),
    Column('flavors_id', Integer, ForeignKey(
        'flavors.id', 
        onupdate='CASCADE',
        ondelete='CASCADE'
    ))
)


def generate_project_id():
    return '{:06x}'.format(randint(1,2**24))


class ProjectModel(Base):
    __tablename__ = "projects"
    id: Mapped[str] = Column(String(6), primary_key=True, index=True, default=generate_project_id)
    name: Mapped[str] = Column(String)
    users: Mapped[list["UserModel"]] = relationship(
        "UserModel", 
        secondary=association_users_to_projects, 
        back_populates="projects", 
        lazy=False, 
        passive_deletes=True
    )
    domains: Mapped[list["DomainModel"]] = relationship("DomainModel", backref="project", viewonly=True)
    # limit
    is_admin: Mapped[bool] = Column(Boolean, nullable=False, default=False)
    core: Mapped[int] = Column(Integer, nullable=False, default=8)
    memory_g: Mapped[int] = Column(Integer, nullable=False, default=16)
    storage_capacity_g: Mapped[int] = Column(Integer, default=128)
    network_pools: Mapped[list["NetworkPoolModel"]] = relationship(
        "NetworkPoolModel", 
        secondary=association_projects_to_networks_pools, 
        lazy=False
    )
    storage_pools: Mapped[list["StoragePoolModel"]] = relationship(
        "StoragePoolModel", 
        secondary=association_projects_to_storages_pools, 
        lazy=False
    )
    flavors: Mapped[list["FlavorModel"]] = relationship(
        "FlavorModel", 
        secondary=association_projects_to_flavors_pools,
        lazy=False
    )
    user_installable: Mapped[bool] = Column(Boolean, nullable=False, default=True)



class ProjectPortsModel(Base):
    __tablename__ = "projects_ports"
    project_id: Mapped[str] = Column(
        String(6), 
        ForeignKey('projects.id', onupdate='CASCADE', ondelete='CASCADE'), 
        primary_key=True
    )
    vlan_id: Mapped[int] = Column(Integer, primary_key=True)
    name: Mapped[str] = Column(String)
