from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from mixin.database import Base


association_table = Table('users_to_groups', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.user_id')),
    Column('groups_id', Integer, ForeignKey('groups.group_id'))
)


class UserModel(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True, index=True)
    hashed_password = Column(String)
    roles = relationship('UserRole')
    groups = relationship("GroupModel", secondary=association_table, back_populates="users")


class UserRole(Base):
    __tablename__ = "users_role"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey('users.user_id', onupdate='CASCADE', ondelete='CASCADE'))
    name = Column(String)


class GroupModel(Base):
    __tablename__ = "groups"
    group_id = Column(String, primary_key=True, index=True)
    users = relationship("UserModel", secondary=association_table, back_populates="groups")
