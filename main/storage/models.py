from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from mixin.database import Base, Engine


class StorageModel(Base):
    __tablename__ = "storages"
    uuid = Column(String, primary_key=True, index=True)
    name = Column(String)
    node_name = Column(String, ForeignKey('nodes.name', onupdate='CASCADE', ondelete='CASCADE'))
    capacity = Column(Integer)
    available = Column(Integer)
    type = Column(String)
    protocol = Column(String)
    path = Column(String)
    active = Column(Boolean)
    auto_start = Column(Boolean)
    status = Column(Integer)
    images = relationship('ImageModel')
    update_token = Column(String)



class ImageModel(Base):
    __tablename__ = "images"
    name = Column(String, primary_key=True)
    storage_uuid = Column(String, ForeignKey('storages.name', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    capacity = Column(Integer)
    allocation = Column(Integer)
    path = Column(String)
    update_token = Column(String)