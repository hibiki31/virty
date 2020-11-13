from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, JSON
from sqlalchemy.orm import relationship
from mixin.database import Base, Engine


class TaskModel(Base):
    __tablename__ = "queue"
    uuid = Column(String, primary_key=True, index=True)
    post_time = Column(DateTime)
    run_time = Column(Integer)
    user_id = Column(Integer(), ForeignKey('users.user_id', onupdate='CASCADE', ondelete='CASCADE'))
    status = Column(String)
    resource = Column(String)
    object = Column(String)
    method = Column(String)
    request = Column(JSON)
    message = Column(String)