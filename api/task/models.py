from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, JSON, Float
from mixin.database import Base

from user.models import UserModel


class TaskModel(Base):
    __tablename__ = "tasks"
    uuid = Column(String, primary_key=True, index=True)
    post_time = Column(DateTime(timezone=True))
    start_time = Column(DateTime(timezone=True))
    update_time = Column(DateTime(timezone=True))
    run_time = Column(Float)
    user_id = Column(String, ForeignKey('users.username', onupdate='CASCADE', ondelete='CASCADE'))
    dependence_uuid = Column(String, ForeignKey('tasks.uuid', onupdate='CASCADE', ondelete='CASCADE'))
    status = Column(String) # init, start, finish
    resource = Column(String) # node, domain, network...
    object = Column(String) # base, power...
    method = Column(String) # delete, post, update...
    request = Column(JSON)
    result = Column(JSON)
    message = Column(String)