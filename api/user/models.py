from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.orm import relationship

from mixin.database import Base

association_users_to_projects = Table('users_to_projects', Base.metadata,
    Column('user_id', String, ForeignKey('users.username', onupdate='CASCADE', ondelete='CASCADE')),
    Column('project_id', String(6), ForeignKey('projects.id', onupdate='CASCADE', ondelete='CASCADE'))
)


class UserModel(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True, index=True)
    hashed_password = Column(String)
    scopes = relationship('UserScopeModel', lazy=False)
    publickeys = relationship('UserPublickeyModel', lazy=False)
    projects = relationship("ProjectModel", secondary=association_users_to_projects, back_populates="users", lazy=False, viewonly=True)


class UserScopeModel(Base):
    __tablename__ = "users_scope"
    user_id = Column(String, ForeignKey('users.username', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    name = Column(String, primary_key=True)

class UserPublickeyModel(Base):
    __tablename__ = "users_publickey"
    user_id = Column(String, ForeignKey('users.username', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    name = Column(String, primary_key=True)
    publickey = Column(String)