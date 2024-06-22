import httpx
from os import chmod, makedirs
from typing import List

from fastapi import APIRouter, Depends

from auth.router import CurrentUser, get_current_user
from mixin.database import get_db
from mixin.exception import AlreadyExists, NotFound
from mixin.log import setup_logger
from module.sshlib import SSHManager
from sqlalchemy.orm import Session

from settings import CLOUDFLARE_API_URL
from ipam.model import IpamZoneModel, IpamZoneRecordModel
from ipam.schemas.api import (
    IpamZoneForCreate,
    IpamZoneRecordForCreate,
    IpamZoneRecordForGet,
)
from ipam.schemas import cloudflare

app = APIRouter(prefix="/api/ipams", tags=["ipam"])
logger = setup_logger(__name__)


@app.post("/zones", operation_id="create_ipam_zone")
def create_ipam_zone(
    body: IpamZoneForCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ipam_zone = (
        db.query(IpamZoneModel).filter(IpamZoneModel.id == body.id).one_or_none()
    )
    if ipam_zone:
        raise AlreadyExists()

    db.add(IpamZoneModel(id=body.id, name=body.name, token=body.token))
    db.commit()

    return {"msg": "success"}


@app.get("/zones", operation_id="get_ipam_zone")
def get_ipam_zone(
    current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)
):
    ipam_zones = db.query(IpamZoneModel).all()

    return ipam_zones


@app.get(
    "/zones/records",
    operation_id="get_ipam_zone_record",
)
def get_ipam_zone_record(
    current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)
):
    record = db.query(IpamZoneRecordModel).all()

    return record


@app.post("/zones/records", operation_id="create_ipam_zone_record")
def create_ipam_zone_record(
    body: IpamZoneRecordForCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    zone = db.query(IpamZoneModel).filter(IpamZoneModel.id == body.zone_id).one()

    url = f"{CLOUDFLARE_API_URL}/zones/{body.zone_id}/dns_records"
    headers = {"Authorization": f"Bearer {zone.token}"}
    payload = {
        "type": body.type,
        "name": body.name,
        "content": body.content,
        "ttl": body.ttl,
        "proxied": False,
    }

    res = httpx.post(url, headers=headers, json=payload)
    logger.debug([res.status_code, res.text])
    if res.status_code == 400:
        raise AlreadyExists()
    res_model = cloudflare.Model(**res.json())

    db.add(
        IpamZoneRecordModel(
            id=res_model.result.id,
            name=body.name,
            zone_id=body.zone_id,
            ttl=body.ttl,
            type=body.type,
            content=body.content,
        )
    )
    db.commit()

    return res.json()


@app.delete("/zones/records/{id}", operation_id="delete_ipam_zone_record")
def delete_ipam_zone_record(
    id:str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = db.query(IpamZoneRecordModel).filter(IpamZoneRecordModel.id == id).one_or_none()

    if record is None:
        raise NotFound()
    
    zone = db.query(IpamZoneModel).filter(IpamZoneModel.id == record.zone_id).one()
    headers = {"Authorization": f"Bearer {zone.token}"}
    
    url = f"{CLOUDFLARE_API_URL}/zones/{record.zone_id}/dns_records/{record.id}"
    response = httpx.delete(url, headers=headers)

    db.delete(record)
    db.commit()

    return response.json()
