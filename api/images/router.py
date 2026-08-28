from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import tuple_
from sqlalchemy.orm import Session

from auth.router import CurrentUser, get_current_user
from domain.models import DomainDriveModel, DomainModel
from flavor.models import FlavorModel
from mixin.database import get_db
from mixin.log import setup_logger
from node.models import NodeModel
from project.models import ProjectModel
from resource_authorization import (
    allowed_image_keys,
    get_member_project,
    get_project_storage,
    project_flavor_ids,
)
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
    current_user.verify_scope(["image.read"])
    if param.project_id is not None:
        get_member_project(db, param.project_id, current_user)
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
    visible_images = allowed_image_keys(db, current_user, param.project_id)
    query = query.filter(tuple_(
        ImageModel.storage_uuid,
        ImageModel.path,
    ).in_(visible_images))

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
    query = query.order_by(ImageModel.name)
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


@app.patch("", response_model=Image)
def update_image_flavor(
        req: ImageForUpdateImageFlavor,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    current_user.verify_scope(["image.manage"])
    get_member_project(db, req.project_id, current_user)
    locked_project_id = (
        db.query(ProjectModel.id)
        .filter(ProjectModel.id == req.project_id)
        .with_for_update()
        .scalar()
    )
    if locked_project_id is None:
        raise HTTPException(status_code=404, detail="project not found")
    storage = get_project_storage(
        db,
        req.project_id,
        req.storage_uuid,
        current_user,
    )
    if storage.node_name != req.node_name:
        raise HTTPException(status_code=404, detail="image not found")
    if req.flavor_id not in project_flavor_ids(db, req.project_id):
        raise HTTPException(status_code=404, detail="flavor not found")
    image_model = db.query(ImageModel).filter(
        ImageModel.storage_uuid==req.storage_uuid,
        ImageModel.path==req.path
        ).one_or_none()
    if image_model is None:
        raise HTTPException(status_code=404, detail="image not found")
    if db.get(FlavorModel, req.flavor_id) is None:
        raise HTTPException(status_code=404, detail="flavor not found")
    image_model.flavor_id = req.flavor_id
    db.commit()
    db.refresh(image_model)
    return image_model
