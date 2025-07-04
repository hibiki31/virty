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
    images = relationship('ImageModel', viewonly=True)
    update_token = Column(String)
    meta_data = relationship('StorageMetadataModel', uselist=False, backref="storages")
    allocation_commit = 0
    capacity_commit = 0




class StorageMetadataModel(Base):
    __tablename__ = "storages_metadata"
    device_type = Column(String) # HDD, SSD, NVME...
    protocol = Column(String) # NFS, Gluster, Ceph...
    uuid = Column(String, ForeignKey('storages.uuid', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    rool = Column(String) # iso, img, cloud-init, template


class AssociationStoragePoolModel(Base):
    __tablename__ = 'associations_storages_pools'
    pool_id = Column(Integer, ForeignKey('storages_pools.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    storage_uuid = Column(String, ForeignKey('storages.uuid', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    storage = relationship("StorageModel")



class StoragePoolModel(Base):
    __tablename__ = "storages_pools"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String)
    storages = relationship("AssociationStoragePoolModel", lazy=False)


class ImageModel(Base):
    __tablename__ = "images"
    name = Column(String)
    storage_uuid = Column(String, ForeignKey('storages.uuid', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    storage = relationship("StorageModel", uselist=False)
    capacity = Column(Integer)
    allocation = Column(Integer)
    domain_uuid = Column(String, nullable=True)
    path = Column(String, primary_key=True)
    update_token = Column(String)
    flavor_id = Column(Integer, ForeignKey('flavors.id', onupdate='CASCADE', ondelete='SET NULL'))
    flavor = relationship("FlavorModel", lazy=False)
