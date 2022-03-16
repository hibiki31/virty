from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from mixin.database import Base
from user.models import association_users_to_projects


class ProjectModel(Base):
    __tablename__ = "projects"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    users = relationship("UserModel", secondary=association_users_to_projects, back_populates="projects", lazy=False)
    domains = relationship("DomainModel", backref="project")