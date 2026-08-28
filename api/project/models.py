import secrets
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    String,
    Table,
    UniqueConstraint,
)
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
    ), nullable=False),
    Column('networks_pools_id', Integer, ForeignKey(
        'networks_pools.id',
        onupdate='CASCADE',
        ondelete='CASCADE'
    ), nullable=False),
    UniqueConstraint(
        'projects_id',
        'networks_pools_id',
        name='uq_projects_to_networks_pools_project_pool',
    ),
)

association_projects_to_storages_pools = Table(
    'projects_to_storages_pools',
    Base.metadata,
    Column('projects_id', String(6), ForeignKey(
        'projects.id',
        onupdate='CASCADE',
        ondelete='CASCADE'
    ), nullable=False),
    Column('storages_pools_id', Integer, ForeignKey(
        'storages_pools.id',
        onupdate='CASCADE',
        ondelete='CASCADE'
    ), nullable=False),
    UniqueConstraint(
        'projects_id',
        'storages_pools_id',
        name='uq_projects_to_storages_pools_project_pool',
    ),
)

association_projects_to_flavors_pools = Table(
    'projects_to_flavors_pools',
    Base.metadata,
    Column('projects_id', String(6), ForeignKey(
        'projects.id',
        onupdate='CASCADE',
        ondelete='CASCADE'
    ), nullable=False),
    Column('flavors_id', Integer, ForeignKey(
        'flavors.id',
        onupdate='CASCADE',
        ondelete='CASCADE'
    ), nullable=False),
    UniqueConstraint(
        'projects_id',
        'flavors_id',
        name='uq_projects_to_flavors_pools_project_flavor',
    ),
)


def generate_project_id() -> str:
    """暗号学的乱数から6桁の小文字hex IDを作る。"""

    return secrets.token_hex(3)


class ProjectModel(Base):
    __tablename__ = "projects"
    __table_args__ = (
        CheckConstraint(
            "length(trim(name)) BETWEEN 1 AND 64",
            name="ck_projects_name_length",
        ),
    )

    id: Mapped[str] = Column(
        String(6),
        primary_key=True,
        index=True,
        default=generate_project_id,
    )
    name: Mapped[str] = Column(String(64), nullable=False)
    users: Mapped[list["UserModel"]] = relationship(
        "UserModel",
        secondary=association_users_to_projects,
        back_populates="projects",
        lazy=False,
        passive_deletes=True
    )
    domains: Mapped[list["DomainModel"]] = relationship(
        "DomainModel",
        backref="project",
        viewonly=True,
    )
    # 上限値は互換情報として保持し、現時点では強制しない。
    core: Mapped[int] = Column(Integer, nullable=False, default=8)
    memory_g: Mapped[int] = Column(Integer, nullable=False, default=16)
    # SQLAlchemy pluginはPython defaultだけを見てnon-nullと推論するが、既存DB列はnullable。
    storage_capacity_g: Mapped[int | None] = Column(  # type: ignore[misc]
        Integer,
        nullable=True,
        default=128,
    )
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
