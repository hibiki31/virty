from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, relationship

from mixin.database import Base

if TYPE_CHECKING:
    from project.models import ProjectModel

association_users_to_projects = Table('users_to_projects', Base.metadata,
    Column('user_id', String, ForeignKey('users.username', onupdate='CASCADE', ondelete='CASCADE')),
    Column('project_id', String(6), ForeignKey('projects.id', onupdate='CASCADE', ondelete='CASCADE'))
)


class UserModel(Base):
    __tablename__ = "users"
    username: Mapped[str] = Column(String, primary_key=True, index=True)
    hashed_password: Mapped[str] = Column(String)
    
    scopes: Mapped[list["UserScopeModel"]] = relationship(
        "UserScopeModel",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )
    
    publickeys: Mapped[list["UserPublickeyModel"]] = relationship(
        "UserPublickeyModel",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    projects: Mapped[list["ProjectModel"]] = relationship(
        "ProjectModel",
        secondary=association_users_to_projects,
        back_populates="users",
        lazy=False,
        viewonly=True,
    )


class UserScopeModel(Base):
    __tablename__ = "users_scope"
    user_id: Mapped[str] = Column(String, ForeignKey('users.username', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    name: Mapped[str] = Column(String, primary_key=True)

class UserPublickeyModel(Base):
    __tablename__ = "users_publickey"
    user_id: Mapped[str] = Column(String, ForeignKey('users.username', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    name: Mapped[str] = Column(String, primary_key=True)
    publickey: Mapped[str] = Column(String)
