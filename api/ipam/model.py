from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from mixin.database import Base

class IpamZoneModel(Base):
    __tablename__ = "ipam_zones"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    token = Column(String)
    records = relationship("IpamZoneRecordModel", back_populates="zone")

class IpamZoneRecordModel(Base):
    __tablename__ = "ipam_zone_records"
    id = Column(String, primary_key=True, index=True)
    zone_id = Column(String, ForeignKey('ipam_zones.id', onupdate='CASCADE', ondelete='CASCADE'))
    
    name = Column(String)
    ttl = Column(Integer)
    type = Column(String)
    content = Column(String)
    zone = relationship("IpamZoneModel", back_populates="records")