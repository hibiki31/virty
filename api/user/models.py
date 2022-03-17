from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from mixin.database import Base


association_users_to_projects = Table('users_to_projects', Base.metadata,
    Column('user_id', String, ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE')),
    Column('project_id', String(6), ForeignKey('projects.id', onupdate='CASCADE', ondelete='CASCADE'))
)


class UserModel(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    hashed_password = Column(String)
    scopes = relationship('UserScope', lazy=False)
    projects = relationship("ProjectModel", secondary=association_users_to_projects, back_populates="users", lazy=False)


class UserScope(Base):
    __tablename__ = "users_scope"
    user_id = Column(String, ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    name = Column(String, primary_key=True)
