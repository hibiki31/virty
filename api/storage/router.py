from email.mime import image
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import false, func, true
from domain.models import DomainDriveModel, DomainModel

from flavor.models import FlavorModel

from .models import *
from .schemas import *

from auth.router import CurrentUser, get_current_user
from task.models import TaskModel
from task.schemas import TaskSelect
from task.functions import TaskManager
from node.models import NodeModel
from mixin.database import get_db
from mixin.log import setup_logger

from module import virtlib
from module import xmllib
from module.sshlib import SSHManager


app = APIRouter()
logger = setup_logger(__name__)


@app.get("/api/storages", tags=["storage"], response_model=List[StorageSelect])
def get_api_storages(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):

    image_sum = db.query(
        ImageModel.storage_uuid, 
        func.sum(ImageModel.capacity).label('sum_capacity'),
        func.sum(ImageModel.allocation).label('sum_allocation')
    ).group_by(ImageModel.storage_uuid).subquery('image_sum')

    models = db.query(
        StorageModel,
        image_sum.c.sum_capacity,
        image_sum.c.sum_allocation
    ).outerjoin(
        image_sum,
        StorageModel.uuid==image_sum.c.storage_uuid
    ).order_by(StorageModel.node_name,StorageModel.name).all()

    res = []

    for model in models:
        tmp = model[0]
        tmp.capacity_commit = model[1]
        tmp.allocation_commit = model[2]
        res.append(tmp)

    return res


@app.get("/api/images", tags=["storage"], response_model=List[ImageSelect])
def get_api_images(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        node_name: str = None,
        pool_uuid: str = None,
        name:str = None,
        rool:str = None,
    ):
    query = db.query(
        ImageModel,DomainModel
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

    for i in query.all():
        if i[1]:
            domain = GetImageDomain(**i[1].__dict__)
        else:
            domain = None

        res.append(
            ImageSelect(
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

    return res


@app.put("/api/images", tags=["storage"])
def put_api_images(
        bg: BackgroundTasks,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    # タスクを追加
    task = TaskManager(db=db, bg=bg)
    task.select('put', 'storage', 'list')
    task.commit(user=current_user)
   
    return task.model


@app.patch("/api/images", tags=["storage"])
def patch_api_images(
        req: PatchImageFlavor,
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



@app.post("/api/storages", tags=["storage"], response_model=TaskSelect)
def post_api_storage(
        bg: BackgroundTasks,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        request: StorageInsert = None
    ):
    task = TaskManager(db=db, bg=bg)
    task.select('post', 'storage', 'root')
    task.commit(user=current_user, request=request)

    put_task = TaskManager(db=db, bg=bg)
    put_task.select('put', 'storage', 'list')
    put_task.commit(user=current_user, dependence_uuid=task.model.uuid)

    return task.model


@app.patch("/api/storages", tags=["storage"])
def post_api_storage(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        request_model: StorageMetadataPatch = None
    ):
    db.merge(StorageMetadataModel(**request_model.dict()))
    db.commit()
    return db.query(StorageModel).filter(StorageModel.uuid==request_model.uuid).all()


@app.delete("/api/storages", tags=["storage"], response_model=TaskSelect)
def delete_api_storages(
        bg: BackgroundTasks,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        request_model: StorageDelete = None
    ):
    # タスクを追加
    post_task = PostTask(db=db, user=current_user, model=request_model)
    task_model = post_task.commit("storage","base","delete", bg)

    return task_model


@app.get("/api/storages/pools", tags=["storage"], response_model=List[GetStoragePool])
def get_api_storages_pools(
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ):

    return db.query(StoragePoolModel).all()


@app.post("/api/storages/pools", tags=["storage"])
def post_api_storages_pools(
        request_model: PostStoragePool,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    storage_pool_model = StoragePoolModel(name=request_model.name)
    db.add(storage_pool_model)
    for storage_uuid in request_model.storage_uuids:
        storage_pool_model.storages.append(
            AssociationStoragePool(storage_uuid=storage_uuid, pool_id=storage_pool_model.id)
        )
    db.commit()
    return db.query(StoragePoolModel).filter(StoragePoolModel.id==storage_pool_model.id).one()


@app.patch("/api/storages/pools", tags=["storage"])
def post_api_storages_pools(
        request_model: PatchStoragePool,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    storage_pool_model = db.query(StoragePoolModel).filter(StoragePoolModel.id==request_model.id).one()
    for storage_uuid in request_model.storage_uuids:
        storage_pool_model.storages.append(
            AssociationStoragePool(storage_uuid=storage_uuid, pool_id=storage_pool_model.id)
        )
    db.commit()
    return db.query(StoragePoolModel).filter(StoragePoolModel.id==storage_pool_model.id).one()


@app.put("/api/images/scp", tags=["storage"])
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
