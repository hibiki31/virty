from urllib import request
from fastapi import APIRouter, Depends, BackgroundTasks
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

from module.virtlib import VirtManager


app = APIRouter(
    prefix="/api/vms",
    tags=["vms"]
)

logger = setup_logger(__name__)


@app.get("",response_model=List[GetDomain])
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
                DomainModel.project.has(ProjectModel.users.any(id=current_user.id))
        ))

    return query.all()


@app.get("/{uuid}",response_model=GetDomainDetail)
def get_api_domain_uuid(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        uuid:str = None
    ):
    try:
        domain:DomainModel = db.query(DomainModel).filter(DomainModel.uuid==uuid).one()
    except:
        raise notfound_exception(msg="not found domain")

    return domain


@app.put('', response_model=TaskSelect)
def publish_task_to_update_vm_list(
        bg: BackgroundTasks,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    task = TaskManager(db=db, bg=bg)
    task.select('put', 'vm', 'list')
    task.commit(user=current_user)

    return task.model


@app.delete("", response_model=TaskSelect)
def delete_api_domains(
        bg: BackgroundTasks,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        request: DomainDelete = None
    ):
    task = TaskManager(db=db, bg=bg)
    task.select('delete', 'vm', 'root')
    task.commit(user=current_user, request=request)

    return task.model


@app.post("", response_model=TaskSelect)
def post_api_vms(
        bg: BackgroundTasks,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        request: DomainInsert = None
    ):
    task = TaskManager(db=db, bg=bg)
    task.select('post', 'vm', 'root')
    task.commit(user=current_user, request=request)

    storage_task = TaskManager(db=db, bg=bg)
    storage_task.select('put', 'storage', 'list')
    storage_task.commit(user=current_user, dependence_uuid=task.model.uuid)

    return task.model


@app.post("/ticket")
def post_api_vms(
        bg: BackgroundTasks,
        request: PostDomainTicket,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    task = TaskManager(db=db, bg=bg)
    task.select('post', 'vm', 'root')
    task.commit(user=current_user, request=request)

    storage_task = TaskManager(db=db, bg=bg)
    storage_task.select('put', 'storage', 'list')
    storage_task.commit(user=current_user, dependence_uuid=task.model.uuid)

    return task.model


@app.patch("", response_model=TaskSelect)
def patch_api_domains(
        bg: BackgroundTasks,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        request: DomainPatch = None
    ):
    task = TaskManager(db=db, bg=bg)
    task.select('patch', 'vm', 'root')
    task.commit(user=current_user, request=request)

    return task.model


@app.patch("/name")
def path_vms_name(
        model: DomainPatchName,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
    try:
        vm = db.query(DomainModel).filter(DomainModel.uuid==model.uuid).one()
    except:
        raise notfound_exception(msg="not found vm")
    
    if model.name != vm.name:
        virt = VirtManager(vm.node)
        virt.domain_rename(uuid=vm.uuid, new_name=model.name)
        vm.name = model.name
        db.commit()

    return True


@app.patch("/core")
def path_vms_core(
        model: DomainPatchCore,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
    try:
        vm = db.query(DomainModel).filter(DomainModel.uuid==model.uuid).one()
    except:
        raise notfound_exception(msg="not found vm")
    
    if model.core != vm.core:
        virt = VirtManager(vm.node)
        virt.domain_core(uuid=model.uuid, core=model.core)
        vm.core = model.core
        db.commit()

    return True


@app.patch("/user")
def path_vms_user(
        model: DomainPatchUser,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
    try:
        vm = db.query(DomainModel).filter(DomainModel.uuid==model.uuid).one()
        db.query(UserModel).filter(UserModel.id==model.user_id).one()
    except:
        raise notfound_exception(msg="not found vm or user")
    
    vm.owner_user_id = model.user_id
    db.commit()

    return vm


@app.patch("/project")
def path_vms_project(
        model: DomainProjectPatch,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
    try:
        vm = db.query(DomainModel).filter(DomainModel.uuid==model.uuid).one()
        db.query(ProjectModel).filter(ProjectModel.id==model.project_id).one()
    except:
        raise notfound_exception(msg="not found vm or group")
    
    vm.owner_project = model
    db.commit()

    return vm


@app.patch("/network", response_model=TaskSelect)
def patch_api_vm_network(
        bg: BackgroundTasks,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        request_model: DomainNetworkChange = None
    ):
    # タスクを追加
    post_task = PostTask(db=db, user=current_user, model=request_model)
    task_model = post_task.commit("vm","network","patch", bg)
   
    return task_model


@app.get("/vnc/{token}")
def get_api_domain(
        token: str,
        db: Session = Depends(get_db),
    ):

    domain_model = db.query(DomainModel).filter(DomainModel.uuid==token).one()

    return { "host": domain_model.node.domain, "port": domain_model.vnc_port }