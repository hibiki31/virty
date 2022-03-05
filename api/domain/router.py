import string, random
import uu
import uuid
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .models import *
from .schemas import *

from auth.router import CurrentUser, get_current_user
from task.models import TaskModel
from task.schemas import TaskSelect
from task.function import PostTask
from user.models import GroupModel, UserModel
from node.models import NodeModel
from mixin.database import get_db
from mixin.log import setup_logger
from mixin.exception import notfound_exception

from module.virtlib import VirtManager, XmlEditor


app = APIRouter(
    prefix="/api/vms",
    tags=["vms"]
)

logger = setup_logger(__name__)


@app.get("",response_model=List[DomainSelect])
def get_api_domain(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        admin: bool = False
    ):

    if not admin:
        vms = db.query(DomainModel)\
            .order_by(DomainModel.node_name,DomainModel.name)\
            .filter(or_(
                DomainModel.owner_user_id==current_user.id,
                DomainModel.owner_group.has(GroupModel.users.any(id=current_user.id))
            )).all()
    else:
        vms = db.query(DomainModel)\
            .order_by(DomainModel.node_name,DomainModel.name).all()

    return vms


@app.get("/{uuid}",response_model=DomainDetailSelect)
def get_api_domain(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        uuid:str = None
    ):
    try:
        domain:DomainModel = db.query(DomainModel).filter(DomainModel.uuid==uuid).one()
        node:NodeModel = db.query(NodeModel).filter(NodeModel.name==domain.node_name).one()
    except:
        raise notfound_exception(msg="not found domain or node")

    editor = XmlEditor("domain",domain.uuid)
    domain_xml_pase = editor.domain_parse()

    token = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(9))
    vnc_node = node.domain
    vnc_port = domain_xml_pase.vnc_port
    if vnc_port != -1:
        db.merge(DomainVNCTokenModel(token=token, node_port=vnc_port, node_domain=vnc_node, domain_uuid=uuid))
        db.commit()

    return {'db':domain, 'node': node, 'xml': domain_xml_pase, 'token': token}


@app.put("", response_model=TaskSelect)
def publish_task_to_update_vm_list(
        bg: BackgroundTasks,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    
    # タスクを追加
    post_task = PostTask(db=db, user=current_user, model=None)
    task_model = post_task.commit("vm","list","update", bg)
    return task_model


@app.delete("", response_model=TaskSelect)
def delete_api_domains(
        bg: BackgroundTasks,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        request_model: DomainDelete = None
    ):
    # タスクを追加
    post_task = PostTask(db=db, user=current_user, model=request_model)
    task_model = post_task.commit("vm","base","delete", bg)

    return task_model


@app.post("", response_model=TaskSelect)
def post_api_vms(
        bg: BackgroundTasks,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        request_model: DomainInsert = None
    ):
    # タスクを追加
    post_task = PostTask(db=db, user=current_user, model=request_model)
    task_model = post_task.commit("vm","base","add", bg)

    # ストレージ更新タスク
    post_task = PostTask(db=db, user=current_user, model=None)
    task_model = post_task.commit("storage","list","update", bg, status="wait",dependence_uuid=task_model.uuid)


    return task_model


@app.patch("", response_model=TaskSelect)
def patch_api_domains(
        bg: BackgroundTasks,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        request_model: DomainPatch = None
    ):
    # タスクを追加
    post_task = PostTask(db=db, user=current_user, model=request_model)
    task_model = post_task.commit("vm","base","change", bg)
   
    return task_model


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


@app.patch("/group")
def path_vms_group(
        model: DomainGroupPatch,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
    try:
        vm = db.query(DomainModel).filter(DomainModel.uuid==model.uuid).one()
        db.query(GroupModel).filter(GroupModel.id==model.group_id).one()
    except:
        raise notfound_exception(msg="not found vm or group")
    
    vm.owner_group_id = model.group_id
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
    task_model = post_task.commit("vm","network","change", bg)
   
    return task_model


@app.get("/vnc/{token}")
def get_api_domain(
        token: str,
        db: Session = Depends(get_db),
    ):

    token_model = db.query(DomainVNCTokenModel).filter(DomainVNCTokenModel.token==token).one()

    return { "host": token_model.node_domain, "port": token_model.node_port }