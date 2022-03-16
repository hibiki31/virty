from lib2to3.pytree import NodePattern
from os import name
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from settings import APP_ROOT

from .models import *
from .schemas import *

from task.schemas import TaskSelect
from mixin.log import setup_logger

from node.models import NodeModel, NodeRoleModel
from module import virtlib
from module import xmllib
from module import sshlib
from module.ansiblelib import AnsibleManager

from domain.tasks import update_domain_list


logger = setup_logger(__name__)


def post_node_base(db: Session, model: TaskSelect):
    request = NodeInsert(**model.request)
    user = request.user_name
    domain = request.domain
    port = request.port

    ssh_manager = sshlib.SSHManager(user=user, domain=domain, port=port)
    ssh_manager.add_known_hosts()
    
    ansible_manager = AnsibleManager(user=user, domain=domain)
    
    node_infomation = ansible_manager.node_infomation()

    memory = ssh_manager.get_node_mem()
    core = ssh_manager.get_node_cpu_core()
    cpu = ssh_manager.get_node_cpu_name()
    os = ssh_manager.get_node_os_release()

    ssh_role = db.query(NodeRoleModel).filter(NodeRoleModel.name=="ssh").one_or_none()
    if ssh_role == None:
        ssh_role = NodeRoleModel(name="ssh")
        db.add(ssh_role)

    row = NodeModel(
        name = request.name,
        domain = domain,
        description = request.description,
        user_name = user,
        port = port,
        core = core,
        memory = memory,
        cpu_gen = node_infomation["result"]["ansible_facts"]["ansible_processor"][2],
        os_like = node_infomation["result"]["ansible_facts"]["ansible_os_family"],
        os_name = node_infomation["result"]["ansible_facts"]["ansible_lsb"]["id"],
        os_version = node_infomation["result"]["ansible_facts"]["ansible_lsb"]["release"],
        status = 10,
        qemu_version = None,
        libvirt_version = None,
    )
    a = AssociationNodeToRole(extra_json={})
    a.role = ssh_role
    row.roles.append(a)
    db.add(row)
    db.commit()

    return model


def patch_node_role(db: Session, model: TaskSelect):
    request = NodeRolePatch(**model.request)
    node_name = request.node_name
    add_role_name = request.role_name
    
    node:NodeModel = db.query(NodeModel).filter(NodeModel.name==node_name).one()

    if add_role_name == "libvirt":
        patch_node_role_libvirt(db=db, model=model, node=node)
    elif add_role_name == "ovs":
        patch_node_role_ovs(db=db, model=model, node=node, request=request)

    return model

def patch_node_role_libvirt(db: Session, model: TaskSelect, node: NodeModel):
    
    ansible_manager = AnsibleManager(user=node.user_name, domain=node.domain)

    res = ansible_manager.run_playbook_file("pb_init_libvirt")
    model.message = "ansible run successfull " + str(res["summary"])
    
    role_model = db.query(NodeRoleModel).filter(NodeRoleModel.name=="libvirt").one_or_none()
    
    if role_model == None:
        role_model = NodeRoleModel(name="libvirt")
        db.add(role_model)
    
    ssh_manager = sshlib.SSHManager(user=node.user_name, domain=node.domain, port=node.port)
    ssh_manager.add_known_hosts()

    node.qemu_version = ssh_manager.get_node_qemu_version()
    node.libvirt_version = ssh_manager.get_node_libvirt_version()

    if not db.query(AssociationNodeToRole).filter(
            AssociationNodeToRole.node_name==node.name, 
            AssociationNodeToRole.role_name=="libvirt"
        ).one_or_none():
        a = AssociationNodeToRole(extra_json={})
        a.role = role_model
        node.roles.append(a)

    db.commit()


def patch_node_role_ovs(db: Session, model: TaskSelect, node: NodeModel, request: NodeRolePatch):
    
    ansible_manager = AnsibleManager(user=node.user_name, domain=node.domain)

    res = ansible_manager.run_playbook_file("pb_init_ovs")
    model.message = "ansible run successfull " + str(res["summary"])
    
    role_model = db.query(NodeRoleModel).filter(NodeRoleModel.name=="ovs").one_or_none()
    
    if role_model == None:
        role_model = NodeRoleModel(name="ovs")
        db.add(role_model)

    if not db.query(AssociationNodeToRole).filter(
            AssociationNodeToRole.node_name==node.name, 
            AssociationNodeToRole.role_name=="ovs"
        ).one_or_none():
        a = AssociationNodeToRole(extra_json=request.extra_json)
        a.role = role_model
        node.roles.append(a)

    db.commit()

    return node
    