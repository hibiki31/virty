from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from auth.router import CurrentUser, get_current_user
from mixin.database import get_db
from mixin.exception import NoResultFound, raise_notfound
from mixin.log import setup_logger
from node.models import NodeModel
from project.models import ProjectModel
from resource_authorization import (
    allowed_node_names,
    get_authorized_network,
    get_authorized_storage,
    require_admin,
)
from storage.models import ImageModel, StorageModel
from task.functions import TaskManager
from task.schemas import Task

from .authorization import get_authorized_domain
from .models import DomainModel
from .schemas import (
    CdromForUpdateDomain,
    DomainForCreate,
    DomainProjectForUpdate,
    NetworkForUpdateDomain,
    PowerStatusForUpdateDomain,
)

app = APIRouter(
    tags=["vms-task"],
    prefix="/api/tasks/vms"
)

logger = setup_logger(__name__)


@app.put('', response_model=List[Task])
def refresh_vms(
        req: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    cu.verify_scope(["vm.read"])
    require_admin(cu)
    task = TaskManager(db=db)
    task.select(method='put', resource='vm', object='list')
    task.commit(user=cu, req=req)

    return [task.model]


@app.post("", response_model=List[Task])
def create_vm(
        req: Request,
        body: DomainForCreate,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    cu.verify_scope(["vm.create"])
    node = db.query(NodeModel).filter(NodeModel.name == body.node_name).one_or_none()
    allowed_nodes = allowed_node_names(db, cu)
    if node is None or (
        allowed_nodes is not None and node.name not in allowed_nodes
    ):
        raise HTTPException(status_code=404, detail="Node not found")
    for interface in body.interface:
        network = get_authorized_network(
            db,
            interface.network_uuid,
            cu,
        )
        if network.node_name != node.name:
            raise HTTPException(
                status_code=400,
                detail="Network must belong to the selected node",
            )
    for disk in body.disks:
        destination = get_authorized_storage(
            db,
            disk.save_pool_uuid,
            cu,
        )
        if destination.node_name != node.name:
            raise HTTPException(
                status_code=400,
                detail="Destination storage must belong to the selected node",
            )
        if disk.type == "copy":
            if disk.original_pool_uuid is None or disk.original_name is None:
                raise HTTPException(
                    status_code=400,
                    detail="Copy source storage and image are required",
                )
            get_authorized_storage(db, disk.original_pool_uuid, cu)
            source = (
                db.query(ImageModel)
                .filter(
                    ImageModel.storage_uuid == disk.original_pool_uuid,
                    ImageModel.name == disk.original_name,
                )
                .one_or_none()
            )
            if source is None or source.storage.node_name != node.name:
                raise HTTPException(
                    status_code=400,
                    detail="Source image must belong to the selected node",
                )
    task = TaskManager(db=db)
    task.select(method='post', resource='vm', object='root')
    task.commit(user=cu, req=req, body=body)

    task_list = TaskManager(db=db)
    task_list.select('put', 'vm', 'list')
    task_list.commit(user=cu, dep_uuid=task.model.uuid)

    task_storage = TaskManager(db=db)
    task_storage.select('put', 'storage', 'list')
    task_storage.commit(user=cu, dep_uuid=task.model.uuid)

    return [ task.model, task_list.model, task_storage.model ]


@app.delete("/{uuid}", response_model=List[Task])
def delete_vm(
        uuid: str,
        req: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    cu.verify_scope(["vm.delete"])
    get_authorized_domain(db, uuid, cu)
    task = TaskManager(db=db)
    task.select(method='delete', resource='vm', object='root')
    task.commit(user=cu, req=req, param={"uuid": uuid})

    vm_list_task = TaskManager(db=db)
    vm_list_task.select('put', 'vm', 'list')
    vm_list_task.commit(user=cu, dep_uuid=task.model.uuid)

    return [task.model]


@app.patch("/{uuid}/power", response_model=List[Task])
def update_vm_power_status(
        uuid: str,
        req: Request,
        body: PowerStatusForUpdateDomain,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    cu.verify_scope(["vm.power"])
    get_authorized_domain(db, uuid, cu)
    task = TaskManager(db=db)
    task.select(method='patch', resource='vm', object='power')
    task.commit(user=cu, req=req, body=body, param={"uuid": uuid})

    task_vm_list = TaskManager(db=db)
    task_vm_list.select('put', 'vm', 'list')
    task_vm_list.commit(user=cu, dep_uuid=task.model.uuid)

    return [task.model]


@app.patch("/{uuid}/cdrom", response_model=List[Task])
def control_vm_cdrom(
        uuid: str,
        req: Request,
        body: CdromForUpdateDomain,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),

):
    """
    umount
    - path = null
    mount
    - path = iso file path
    """
    cu.verify_scope(["vm.attach"])
    domain = get_authorized_domain(db, uuid, cu)

    if body.path:
        image = (
            db.query(ImageModel)
            .join(StorageModel, ImageModel.storage_uuid == StorageModel.uuid)
            .filter(
                ImageModel.path == body.path,
                StorageModel.node_name == domain.node_name,
            )
            .one_or_none()
        )
        if image is None:
            raise HTTPException(status_code=404, detail="CD-ROM image not found")
        get_authorized_storage(db, image.storage_uuid, cu)

    task = TaskManager(db=db)
    task.select(method='patch', resource='vm', object='cdrom')
    task.commit(user=cu, req=req, body=body, param={"uuid": uuid})

    task_vm_list = TaskManager(db=db)
    task_vm_list.select('put', 'vm', 'list')
    task_vm_list.commit(user=cu, req=req, body=body,dep_uuid=task.model.uuid)

    return [task.model, task_vm_list.model]


# @app.patch("/name")
# def path_vms_name(
#         request: DomainPatchName,
#         current_user: CurrentUser = Depends(get_current_user),
#         db: Session = Depends(get_db),
#     ):
#     try:
#         vm = db.query(DomainModel).filter(DomainModel.uuid==request.uuid).one()
#     except:
#         raise notfound_exception(msg="not found vm")
    
#     if request.name != vm.name:
#         virt = VirtManager(vm.node)
#         virt.domain_rename(uuid=vm.uuid, new_name=request.name)
#         vm.name = request.name
#         db.commit()

#     return True


# @app.patch("/core")
# def path_vms_core(
#         request: DomainPatchCore,
#         current_user: CurrentUser = Depends(get_current_user),
#         db: Session = Depends(get_db),
#     ):
#     try:
#         vm = db.query(DomainModel).filter(DomainModel.uuid==request.uuid).one()
#     except:
#         raise notfound_exception(msg="not found vm")
    
#     if request.core != vm.core:
#         virt = VirtManager(vm.node)
#         virt.domain_core(uuid=request.uuid, core=request.core)
#         vm.core = request.core
#         db.commit()

#     return True


# @app.patch("/{uuid}/user")
# def path_vms_user(
#         uuid: str,
#         req: Request,
#         cu: CurrentUser = Depends(get_current_user),
#         db: Session = Depends(get_db),
#         body: DomainPatchUser = None
#     ):
#     try:
#         vm = db.query(DomainModel).filter(DomainModel.uuid==request.uuid).one()
#         db.query(UserModel).filter(UserModel.id==request.user_id).one()
#     except:
#         raise notfound_exception(msg="not found vm or user")
    
#     vm.owner_user_id = request.user_id
#     db.commit()

#     return vm


@app.patch("/{uuid}/project")
def update_vm_project(
        uuid: str,
        request: DomainProjectForUpdate,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    current_user.verify_scope(["vm.project"])
    get_authorized_domain(db, uuid, current_user)
    if not current_user.can_access_project(request.project_id):
        raise HTTPException(status_code=403, detail="Project is outside the granted scope")
    try:
        vm = db.query(DomainModel).filter(DomainModel.uuid == uuid).one()
        db.query(ProjectModel).filter(ProjectModel.id==request.project_id).one()
    except NoResultFound:
        raise_notfound(detail="Not found vm or group")
    
    vm.owner_project_id = request.project_id
    db.commit()

    return vm


@app.patch("/{uuid}/network", response_model=List[Task])
def update_vm_network(
        uuid: str,
        req: Request,
        body: NetworkForUpdateDomain,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    """
    **Power off required**

    Exception: Cannot switch the OVS while the VM is runningOperation not supported: unable to change config on 'network' network type
    """

    cu.verify_scope(["vm.attach"])
    vm = get_authorized_domain(db, uuid, cu)
    
    net = get_authorized_network(db, body.network_uuid, cu)
    if net.node_name != vm.node_name:
        raise HTTPException(
            status_code=400,
            detail="Network must belong to the VM node",
        )

    # タスクを追加
    task = TaskManager(db=db)
    task.select(method='patch', resource='vm', object='network')
    task.commit(user=cu, req=req, body=body, param={"uuid": uuid})

    task_vm_list = TaskManager(db=db)
    task_vm_list.select('put', 'vm', 'list')
    task_vm_list.commit(user=cu, dep_uuid=task.model.uuid)
   
    return [task.model]
