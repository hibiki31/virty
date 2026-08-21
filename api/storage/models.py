from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from mixin.database import Base

if TYPE_CHECKING:
    from flavor.models import FlavorModel


class StorageModel(Base):
    __tablename__ = "storages"
    uuid: Mapped[str] = Column(String, primary_key=True, index=True)
    name: Mapped[str] = Column(String)
    node_name: Mapped[str] = Column(String, ForeignKey('nodes.name', onupdate='CASCADE', ondelete='CASCADE'))
    capacity: Mapped[int] = Column(Integer)
    available: Mapped[int] = Column(Integer)
    path: Mapped[str] = Column(String)
    active: Mapped[bool] = Column(Boolean)
    auto_start: Mapped[bool] = Column(Boolean)
    status: Mapped[int] = Column(Integer)
    images: Mapped[list["ImageModel"]] = relationship('ImageModel', viewonly=True)
    update_token: Mapped[str] = Column(String)
    meta_data: Mapped["StorageMetadataModel | None"] = relationship('StorageMetadataModel', uselist=False, backref="storages")
    allocation_commit: int = 0
    capacity_commit: int = 0




class StorageMetadataModel(Base):
    __tablename__ = "storages_metadata"
    device_type: Mapped[str | None] = mapped_column(String, nullable=True) # HDD, SSD, NVME...
    protocol: Mapped[str | None] = mapped_column(String, nullable=True) # NFS, Gluster, Ceph...
    uuid: Mapped[str] = Column(String, ForeignKey('storages.uuid', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    rool: Mapped[str | None] = mapped_column(String, nullable=True) # iso, img, cloud-init, template


class AssociationStoragePoolModel(Base):
    __tablename__ = 'associations_storages_pools'
    pool_id: Mapped[int] = Column(Integer, ForeignKey('storages_pools.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    storage_uuid: Mapped[str] = Column(String, ForeignKey('storages.uuid', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    storage: Mapped[StorageModel] = relationship("StorageModel")



class StoragePoolModel(Base):
    __tablename__ = "storages_pools"
    id: Mapped[int] = Column(Integer, autoincrement=True, primary_key=True)
    name: Mapped[str] = Column(String)
    storages: Mapped[list[AssociationStoragePoolModel]] = relationship("AssociationStoragePoolModel", lazy=False)


class ImageModel(Base):
    __tablename__ = "images"
    name: Mapped[str] = Column(String)
    storage_uuid: Mapped[str] = Column(String, ForeignKey('storages.uuid', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    storage: Mapped[StorageModel] = relationship("StorageModel", uselist=False)
    capacity: Mapped[int] = Column(Integer)
    allocation: Mapped[int] = Column(Integer)
    domain_uuid: Mapped[str | None] = mapped_column(String, nullable=True)
    path: Mapped[str] = Column(String, primary_key=True)
    update_token: Mapped[str] = Column(String)
    flavor_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('flavors.id', onupdate='CASCADE', ondelete='SET NULL'), nullable=True)
    flavor: Mapped["FlavorModel | None"] = relationship("FlavorModel", lazy=False)
