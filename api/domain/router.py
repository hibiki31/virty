from urllib import request
from fastapi import APIRouter, Depends
from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .models import *
from .schemas import *

from auth.router import CurrentUser, get_current_user
from task.schemas import TaskSelect
from task.functions import TaskManager
from user.models import UserModel
from project.models import ProjectModel
from mixin.database import get_db
from mixin.log import setup_logger
from mixin.exception import notfound_exception

from celery import chain, group

from module.virtlib import VirtManager


app = APIRouter(
    tags=["vms"]
)

logger = setup_logger(__name__)


@app.get("/api/vms",response_model=List[GetDomain])
def get_api_domain(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        admin: bool = False,
    ):
    
    query = db.query(DomainModel).order_by(DomainModel.node_name,DomainModel.name)\

    if admin:
        current_user.verify_scope(scopes=["admin"])
    else:
        query = query.filter(or_(
                DomainModel.owner_user_id==current_user.id,
                DomainModel.project.has(ProjectModel.users.any(username=current_user.id))
        ))

    return query.all()


@app.get("/api/vms/{uuid}",response_model=GetDomainDetail)
def get_api_domain_uuid(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        uuid:str = None
    ):
    try:
        domain:DomainModel = db.query(DomainModel).filter(DomainModel.uuid==uuid).one()
    except:
        raise HTTPException(status_code=404, detail="Not found domain")

    return domain


@app.put('/api/tasks/vms', response_model=List[TaskSelect])
def publish_task_to_update_vm_list(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):

    task = TaskManager(db=db)
    task.select(
        method='put',
        resource='vm', 
        object='list',
    )
    task.commit(user=current_user)

    return [task.model]


@app.delete("/api/tasks/vms", response_model=List[TaskSelect])
def delete_api_domains(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        request: DomainDelete = None
    ):
    task = TaskManager(db=db)
    task.select(method='delete', resource='vm', object='root')
    task.commit(user=current_user, request=request)

    vm_list_task = TaskManager(db=db)
    vm_list_task.select('put', 'vm', 'list')
    vm_list_task.commit(user=current_user, dependence_uuid=task.model.uuid)

    return [task.model]


@app.post("/api/tasks/vms", response_model=List[TaskSelect])
def post_api_vms(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        request: DomainInsert = None
    ):
    task = TaskManager(db=db)
    task.select('post', 'vm', 'root')
    task.commit(user=current_user, request=request)

    vm_list_task = TaskManager(db=db)
    vm_list_task.select('put', 'vm', 'list')
    vm_list_task.commit(user=current_user, dependence_uuid=task.model.uuid)

    storage_task = TaskManager(db=db)
    storage_task.select('put', 'storage', 'list')
    storage_task.commit(user=current_user, dependence_uuid=task.model.uuid)

    return [ task.model, storage_task.model ]


@app.post("/api/tasks/vms/ticket")
def post_api_vms(
        request: PostDomainTicket,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    task = TaskManager(db=db)
    task.select(method='post', resource='vm', object='root')
    task.commit(user=current_user, request=request)

    storage_task = TaskManager(db=db)
    storage_task.select(method='put', resource='storage', object='list')
    storage_task.commit(user=current_user, dependence_uuid=task.model.uuid)

    return task.model


@app.patch("/api/tasks/vms", response_model=List[TaskSelect])
def patch_api_domains(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        request: DomainPatch = None
    ):
    task = TaskManager(db=db)
    task.select(method='patch', resource='vm', object='root')
    task.commit(user=current_user, request=request)

    vm_list_task = TaskManager(db=db)
    vm_list_task.select('put', 'vm', 'list')
    vm_list_task.commit(user=current_user, dependence_uuid=task.model.uuid)

    return [task.model]


@app.patch("/api/tasks/vms/name")
def path_vms_name(
        request: DomainPatchName,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
    try:
        vm = db.query(DomainModel).filter(DomainModel.uuid==request.uuid).one()
    except:
        raise notfound_exception(msg="not found vm")
    
    if request.name != vm.name:
        virt = VirtManager(vm.node)
        virt.domain_rename(uuid=vm.uuid, new_name=request.name)
        vm.name = request.name
        db.commit()

    return True


@app.patch("/api/tasks/vms/core")
def path_vms_core(
        request: DomainPatchCore,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
    try:
        vm = db.query(DomainModel).filter(DomainModel.uuid==request.uuid).one()
    except:
        raise notfound_exception(msg="not found vm")
    
    if request.core != vm.core:
        virt = VirtManager(vm.node)
        virt.domain_core(uuid=request.uuid, core=request.core)
        vm.core = request.core
        db.commit()

    return True


@app.patch("/api/tasks/vms/user")
def path_vms_user(
        request: DomainPatchUser,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
    try:
        vm = db.query(DomainModel).filter(DomainModel.uuid==request.uuid).one()
        db.query(UserModel).filter(UserModel.id==request.user_id).one()
    except:
        raise notfound_exception(msg="not found vm or user")
    
    vm.owner_user_id = request.user_id
    db.commit()

    return vm


@app.patch("/api/tasks/vms/project")
def path_vms_project(
        request: DomainProjectPatch,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
    try:
        vm = db.query(DomainModel).filter(DomainModel.uuid==request.uuid).one()
        db.query(ProjectModel).filter(ProjectModel.id==request.project_id).one()
    except:
        raise notfound_exception(msg="not found vm or group")
    
    vm.owner_project_id = request.project_id
    db.commit()

    return vm


@app.patch("/api/tasks/vms/network", response_model=TaskSelect)
def patch_api_vm_network(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        request: DomainNetworkChange = None
    ):
    # タスクを追加
    task = TaskManager(db=db)
    task.select(method='patch', resource='vm', object='network')
    task.commit(user=current_user, request=request)
   
    return task.model


@app.get("/api/vms/vnc/{token}")
def get_api_domain(
        token: str,
        db: Session = Depends(get_db),
    ):

    domain_model = db.query(DomainModel).filter(DomainModel.uuid==token).one()

    return { "host": domain_model.node.domain, "port": domain_model.vnc_port }