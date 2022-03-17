from sqlalchemy.orm import Session

from .models import *
from task.models import TaskModel
from node.models import NodeModel
from user.models import UserModel

from .schemas import *
from network.schemas import NetworkInsert

from network.tasks import add_network_base
from task.function import TaskManager
from module.ovslib import OVSManager

from mixin.log import setup_logger


logger = setup_logger(__name__)


def post_project(db: Session, model: TaskModel):
    request = PostProject(**model.request)

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
        manager = OVSManager(domain=node["node"])
        # manager.ovs_crean()
        manager.ovs_add_br(f'{bridge_name}')
        for remote in node_list:
            if node["local"] == remote["local"]:
                continue
            manager.ovs_add_vxlan(bridge=bridge_name, remote=remote["local"], key=int(project.id,16))

    for node in nodes:
        add_network_base(db=db, model=TaskModel(request=NetworkInsert(name=bridge_name, node_name=node.name,type="ovs", bridge_device=bridge_name).dict()))
    

    db.commit()

    return model


def delete_project_root(manager):
    print(manager.user)

    return