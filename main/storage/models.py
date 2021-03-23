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
    path = Column(String)
    active = Column(Boolean)
    auto_start = Column(Boolean)
    status = Column(Integer)
    images = relationship('ImageModel', lazy=False, backref="storage")
    update_token = Column(String)
    meta_data = relationship('StorageMetadataModel', uselist=False, lazy=False, backref="storages")




class StorageMetadataModel(Base):
    __tablename__ = "storages_metadata"
    device_type = Column(String) # HDD, SSD, NVME...
    protocol = Column(String) # NFS, Gluster, Ceph...
    uuid = Column(String, ForeignKey('storages.uuid', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    rool = Column(String) # iso, img, cloud-init, template




class ImageModel(Base):
    __tablename__ = "images"
    name = Column(String, primary_key=True)
    storage_uuid = Column(String, ForeignKey('storages.uuid', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    capacity = Column(Integer)
    allocation = Column(Integer)
    path = Column(String)
    update_token = Column(String)