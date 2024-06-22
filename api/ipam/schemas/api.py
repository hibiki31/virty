from mixin.schemas import BaseSchema


class IpamZoneForCreate(BaseSchema):
    id: str
    name: str
    token: str

class IpamZoneForGet(BaseSchema):
    id: str
    name: str

class IpamZoneRecordForCreate(BaseSchema):
    zone_id: str
    name: str
    ttl: int
    type: str
    content: str

class IpamZoneRecordForGet(IpamZoneRecordForCreate):
    zone: IpamZoneForGet