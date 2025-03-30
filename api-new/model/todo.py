from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from model.database import Base


class TodoModel(Base):
    __tablename__ = "todo"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    created_date = Column(DateTime, default=datetime.utcnow)
