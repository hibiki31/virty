from json import loads
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
from mixin.log import setup_logger

from .models import *
from .schemas import *
from task.models import TaskModel
from network.models import NetworkModel
from task.models import TaskModel
from node.models import NodeModel
from user.models import UserModel

from network.schemas import NetworkInsert, NetworkDelete

from module.ovslib import OVSManager
from module.virtlib import VirtManager
from task.functions import TaskManager

from mixin.log import setup_logger


logger = setup_logger(__name__)


def post_project_root(db:Session, bg: BackgroundTasks, task: TaskModel):
    request = PostProject(**loads(task.request))

    project = ProjectModel(
        name=request.project_name
    )
    db.add(project)
    db.commit()

    for user in request.user_ids:
        project.users.append(db.query(UserModel).filter(UserModel.id==user).one())

    nodes = db.query(NodeModel).filter(NodeModel.roles.any(role_name="ovs")).all()

    node_list = []

    for node in nodes:
        for role in node.roles:
            if role.role_name == "ovs":
                node_list.append({"node": node.domain, "local": role.extra_json["localIp"]})
    
    logger.info(node_list)

    bridge_name = f"vy-{project.id}"

    for node in node_list:
        ovs_mg = OVSManager(domain=node["node"])
        # mg.ovs_crean()
        ovs_mg.ovs_add_br(f'{bridge_name}')
        for remote in node_list:
            if node["local"] == remote["local"]:
                continue
            ovs_mg.ovs_add_vxlan(bridge=bridge_name, remote=remote["local"], key=int(project.id,16))

    for node in nodes:
        request_network = NetworkInsert(name=bridge_name, node_name=node.name,type="ovs", bridge_device=bridge_name)
        net_add = TaskManager(db=db, bg=bg)
        net_add.select('post', 'network', 'root')
        net_add.folk(task=task, dependence_uuid=None, request=request_network)


def delete_project_root(db:Session, bg: BackgroundTasks, task: TaskModel):    
    request:DeleteProject = DeleteProject(**loads(task.request))
    project = db.query(ProjectModel).filter(ProjectModel.id==request.id).one()
    bridge_name = f"vy-{project.id}"

    for node in db.query(NodeModel).filter(NodeModel.roles.any(role_name="ovs")).all():
        ovs_mg = OVSManager(domain=node.domain)
        ovs_mg.ovs_del_br(bridge=bridge_name)
    
    for net in db.query(NetworkModel).filter(NetworkModel.name==bridge_name):
        net_delete_req = NetworkDelete(uuid=net.uuid)
        net_delete = TaskManager(db=db, bg=bg)
        net_delete.select('delete', 'network', 'root')
        net_delete.folk(task=task, dependence_uuid=None, request=net_delete_req)

    db.delete(project)
    task.message = "Project has been deleted successfully"