from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, JSON, Float
from mixin.database import Base

from user.models import UserModel


class TaskModel(Base):
    __tablename__ = "tasks"
    uuid = Column(String, primary_key=True, index=True)
    post_time = Column(DateTime)
    run_time = Column(Float)
    user_id = Column(String, ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'))
    status = Column(String)
    resource = Column(String)
    object = Column(String)
    method = Column(String)
    request = Column(JSON)
    message = Column(String)