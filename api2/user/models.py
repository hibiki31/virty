from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from database import Base


class UserModel(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True, index=True)
    hashed_password = Column(String)
    scopes = relationship('UserScopeModel', lazy=False)


class UserScopeModel(Base):
    __tablename__ = "users_scope"
    user_id = Column(String, ForeignKey('users.username', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    name = Column(String, primary_key=True)
