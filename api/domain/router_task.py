from urllib import request
from fastapi import APIRouter, Depends, Request
from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .models import *
from .schemas import *

from auth.router import CurrentUser, get_current_user
from task.schemas import TaskSelect, TaskRequest
from task.functions import TaskManager
from user.models import UserModel
from network.models import NetworkModel
from project.models import ProjectModel
from mixin.database import get_db
from mixin.log import setup_logger
from mixin.exception import notfound_exception

from celery import chain, group

from module.virtlib import VirtManager


app = APIRouter(
    tags=["vm-task"],
    prefix="/api/tasks/vms"
)

logger = setup_logger(__name__)


@app.put('', response_model=List[TaskSelect])
def publish_task_to_update_vm_list(
        req: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):

    task = TaskManager(db=db)
    task.select(method='put', resource='vm', object='list')
    task.commit(user=cu, req=req)

    return [task.model]


@app.post("", response_model=List[TaskSelect])
def post_api_vms(
        req: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        body: DomainInsert = None
    ):
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


@app.delete("/{uuid}", response_model=List[TaskSelect])
def delete_api_domains(
        uuid: str,
        req: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    task = TaskManager(db=db)
    task.select(method='delete', resource='vm', object='root')
    task.commit(user=cu, req=req, param={"uuid": uuid})

    vm_list_task = TaskManager(db=db)
    vm_list_task.select('put', 'vm', 'list')
    vm_list_task.commit(user=cu, dep_uuid=task.model.uuid)

    return [task.model]


@app.patch("/{uuid}/power", response_model=List[TaskSelect])
def patch_api_tasks_vms_uuid_power(
        uuid: str,
        req: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        body: PatchDomainPower = None,
    ):
    
    task = TaskManager(db=db)
    task.select(method='patch', resource='vm', object='power')
    task.commit(user=cu, req=req, body=body, param={"uuid": uuid})

    task_vm_list = TaskManager(db=db)
    task_vm_list.select('put', 'vm', 'list')
    task_vm_list.commit(user=cu, dep_uuid=task.model.uuid)

    return [task.model]


@app.patch("/{uuid}/cdrom", response_model=List[TaskSelect])
def patch_api_tasks_vms_uuid_cdrom(
        uuid: str,
        req: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        body: PatchDominCdrom = None,
    ):
    """
    umount
    - path = null
    
    mount
    - path = iso file path
    """
    
    task = TaskManager(db=db)
    task.select(method='patch', resource='vm', object='cdrom')
    task.commit(user=cu, req=req, body=body, param={"uuid": uuid})

    task_vm_list = TaskManager(db=db)
    task_vm_list.select('put', 'vm', 'list')
    task_vm_list.commit(user=cu, dep_uuid=task.model.uuid)

    return [task.model]


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


# @app.patch("/project")
# def path_vms_project(
#         request: DomainProjectPatch,
#         current_user: CurrentUser = Depends(get_current_user),
#         db: Session = Depends(get_db),
#     ):
#     try:
#         vm = db.query(DomainModel).filter(DomainModel.uuid==request.uuid).one()
#         db.query(ProjectModel).filter(ProjectModel.id==request.project_id).one()
#     except:
#         raise notfound_exception(msg="not found vm or group")
    
#     vm.owner_project_id = request.project_id
#     db.commit()

#     return vm


@app.patch("/{uuid}/network", response_model=List[TaskSelect])
def patch_api_vm_network(
        uuid: str,
        req: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        body: DomainNetworkChange = None
    ):
    """
    **Power off required**

    Exception: Cannot switch the OVS while the VM is runningOperation not supported: unable to change config on 'network' network type
    """

    
    vm = db.query(DomainModel).filter(DomainModel.uuid==uuid).one_or_none()
    if vm == None:
        raise HTTPException(status_code=404, detail="domain not found")
    
    net = db.query(NetworkModel).filter(NetworkModel.uuid==body.network_uuid).one_or_none()
    if net == None:
        raise HTTPException(status_code=400, detail="network uuid is worng")

    # タスクを追加
    task = TaskManager(db=db)
    task.select(method='patch', resource='vm', object='network')
    task.commit(user=cu, req=req, body=body, param={"uuid": uuid})

    task_vm_list = TaskManager(db=db)
    task_vm_list.select('put', 'vm', 'list')
    task_vm_list.commit(user=cu, dep_uuid=task.model.uuid)
   
    return [task.model]