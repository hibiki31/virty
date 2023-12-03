from fastapi import APIRouter, Depends, BackgroundTasks, Request, HTTPException
from sqlalchemy.orm import Session
from domain.models import DomainDriveModel, DomainModel

from flavor.models import FlavorModel

from storage.models import StorageModel, ImageModel, StorageMetadataModel
from .schemas import *

from auth.router import CurrentUser, get_current_user

from task.functions import TaskManager
from node.models import NodeModel
from mixin.database import get_db
from mixin.log import setup_logger

from module.sshlib import SSHManager


app = APIRouter()
logger = setup_logger(__name__)


@app.get("/api/images", tags=["images"], response_model=Image, operation_id="get_images")
def get_api_images(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        node_name: str = None,
        pool_uuid: str = None,
        name:str = None,
        rool:str = None,
        limit: int = 25,
        page: int = 0,
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

    if pool_uuid != None:
        query = query.filter(StorageModel.uuid==pool_uuid)

    if node_name != None:
        query = query.filter(NodeModel.name==node_name)

    if name != None:
        query = query.filter(ImageModel.name.like(f'%{name}%'))

    if rool != None:
        query = query.filter(StorageMetadataModel.rool==rool)

    res = []
    
    count = query.count()
    query = query.limit(limit).offset(int(limit*page))

    for i in query.all():
        if i[1]:
            domain = ImageDomain(**i[1].__dict__)
        else:
            domain = None

        res.append(
            ImagePage(
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


@app.put("/api/tasks/images", tags=["images-task"], operation_id="refresh_images")
def put_api_images(
        req: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    task = TaskManager(db=db)
    task.select(method='put', resource='storage', object='list')
    task.commit(user=cu, req=req)

    return [task.model]


@app.patch("/api/images", tags=["images"], operation_id="update_image_flavor")
def patch_api_images(
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


@app.put("/api/images/scp", tags=["images"], operation_id="scp_image")
def put_api_images_scp(
        bg: BackgroundTasks,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        request_model: ImageSCP = None
    ):

    to_node = db.query(NodeModel).filter(NodeModel.name==request_model.to_node_name).one()
    from_node = db.query(NodeModel).filter(NodeModel.name==request_model.from_node_name).one()


    sshl = SSHManager("user","domain","port")
    sshl.scp_other_node(
        to_node=to_node,
        from_node=from_node,
        to_path=request_model.to_file_path,
        from_path=request_model.from_file_path
    )


    return True


@app.post("/api/tasks/images/download", tags=["images-task"], operation_id="download_image")
def post_image_download(
        req: Request,
        body: ImageDownloadForCreate,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):

    task = TaskManager(db=db)
    task.select(method='post', resource='image', object='download')
    task.commit(user=cu, req=req, body=body)

    return [task.model]
