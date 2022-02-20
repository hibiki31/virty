from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from mixin.database import Base


association_table = Table('users_to_groups', Base.metadata,
    Column('user_id', String, ForeignKey('users.id')),
    Column('group_id', String, ForeignKey('groups.id'))
)


class UserModel(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    hashed_password = Column(String)
    scopes = relationship('UserScope', lazy=False)
    groups = relationship("GroupModel", secondary=association_table, back_populates="users", lazy=False)


class UserScope(Base):
    __tablename__ = "users_scope"
    user_id = Column(String, ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    name = Column(String, primary_key=True)


class GroupModel(Base):
    __tablename__ = "groups"
    id = Column(String, primary_key=True, index=True)
    users = relationship("UserModel", secondary=association_table, back_populates="groups")