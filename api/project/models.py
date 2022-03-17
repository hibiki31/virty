from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from mixin.database import Base
from user.models import association_users_to_projects

from random import randint

def generate_project_id():
    return '{:06x}'.format(randint(1,2**24))

class ProjectModel(Base):
    __tablename__ = "projects"
    id = Column(String(6), primary_key=True, index=True, default=generate_project_id)
    name = Column(String)
    users = relationship("UserModel", secondary=association_users_to_projects, back_populates="projects", lazy=False)
    domains = relationship("DomainModel", backref="project")