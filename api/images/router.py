from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.router import CurrentUser, get_current_user
from domain.models import DomainDriveModel, DomainModel
from flavor.models import FlavorModel
from mixin.database import get_db
from mixin.log import setup_logger
from node.models import NodeModel
from storage.models import ImageModel, StorageMetadataModel, StorageModel

from .schemas import (
    Image,
    ImageDomain,
    ImageForQuery,
    ImageForUpdateImageFlavor,
    ImagePage,
)

app = APIRouter(prefix="/api/images", tags=["images"])
logger = setup_logger(__name__)


@app.get("", response_model=ImagePage)
def get_images(
        param: ImageForQuery = Depends(),
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
    query = db.query(
        ImageModel,
        DomainModel
    ).join(StorageModel).join(NodeModel).outerjoin(StorageMetadataModel).outerjoin(
        DomainDriveModel,
        DomainDriveModel.source==ImageModel.path
    ).outerjoin(
        DomainModel,
        DomainModel.uuid==DomainDriveModel.domain_uuid
    ).outerjoin(
        FlavorModel
    )

    if param.pool_uuid:
        query = query.filter(StorageModel.uuid==param.pool_uuid)

    if param.node_name:
        query = query.filter(NodeModel.name==param.node_name)

    if param.name_like:
        query = query.filter(ImageModel.name.like(f'%{param.name_like}%'))
        
    if param.name:
        query = query.filter(ImageModel.name==param.name)

    if param.rool:
        query = query.filter(StorageMetadataModel.rool==param.rool)

    res = []
    
    count = query.count()
    if param.limit > 0:
        query = query.limit(param.limit).offset(int(param.limit*param.page))

    for i in query.all():
        if i[1]:
            domain = ImageDomain(**i[1].__dict__)
        else:
            domain = None

        res.append(
            Image(
                name=i[0].name,
                storage=i[0].storage,
                capacity=i[0].capacity,
                allocation=i[0].allocation,
                path=i[0].path,
                flavor=i[0].flavor,
                storage_uuid=i[0].storage_uuid,
                domain=domain
            )
        )
    return {"count": count, "data": res}


@app.patch("")
def update_image_flavor(
        req: ImageForUpdateImageFlavor,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
    image_model = db.query(ImageModel).filter(
        ImageModel.storage_uuid==req.storage_uuid,
        ImageModel.path==req.path
        ).one()
    db.query(FlavorModel.id==req.flavor_id).one()
    image_model.flavor_id = req.flavor_id
    db.commit()

    res = image_model = db.query(ImageModel).filter(
        ImageModel.storage_uuid==req.storage_uuid,
        ImageModel.path==req.path
        ).one()
    return res

