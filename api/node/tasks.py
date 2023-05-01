from json import loads
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from fastapi import BackgroundTasks
from mixin.log import setup_logger

from .models import *
from .schemas import *
from task.models import TaskModel


from module import sshlib
from module.ansiblelib import AnsibleManager
from task.functions import TaskBase, TaskRequest

worker_task = TaskBase()
logger = setup_logger(__name__)


@worker_task(key="post.node.root")
def post_node_root(self: TaskBase, task: TaskModel, request: TaskRequest):
    db = self.db
    body = NodeInsert(**request.body)
    

    user = body.user_name
    domain = body.domain
    port = body.port

    ssh_manager = sshlib.SSHManager(user=user, domain=domain, port=port)
    ssh_manager.add_known_hosts()
    
    # ansible_manager = AnsibleManager(user=user, domain=domain)
    
    # node_infomation = ansible_manager.node_infomation()

    ssh_role = db.query(NodeRoleModel).filter(NodeRoleModel.name=="ssh").one_or_none()
    if ssh_role == None:
        ssh_role = NodeRoleModel(name="ssh")
        db.add(ssh_role)

    # row = NodeModel(
    #     name = request.name,
    #     domain = domain,
    #     description = request.description,
    #     user_name = user,
    #     port = port,
    #     core = node_infomation["result"]["ansible_facts"]["ansible_processor_nproc"],
    #     memory = int(float(node_infomation["result"]["ansible_facts"]["ansible_memtotal_mb"])/1024),
    #     cpu_gen = node_infomation["result"]["ansible_facts"]["ansible_processor"][2],
    #     os_like = node_infomation["result"]["ansible_facts"]["ansible_os_family"],
    #     os_name = node_infomation["result"]["ansible_facts"]["ansible_lsb"]["id"],
    #     os_version = node_infomation["result"]["ansible_facts"]["ansible_lsb"]["release"],
    #     status = 10,
    #     ansible_facts = node_infomation,
    #     qemu_version = None,
    #     libvirt_version = None,
    # )
    row = NodeModel(
        name = body.name,
        domain = domain,
        description = body.description,
        user_name = user,
        port = port,
        core = ssh_manager.get_node_cpu_core(),
        memory = int(ssh_manager.get_node_mem()),
        cpu_gen = ssh_manager.get_node_cpu_name(),
        os_like = ssh_manager.get_node_os_release()["ID_LIKE"],
        os_name = ssh_manager.get_node_os_release()["PRETTY_NAME"],
        os_version = ssh_manager.get_node_os_release()["VERSION_ID"],
        status = 10,
        ansible_facts = {},
        qemu_version = None,
        libvirt_version = None,
    )
    a = AssociationNodeToRole(extra_json={})
    a.role = ssh_role
    row.roles.append(a)
    db.add(row)
    db.commit()

    task.message = "Node added has been successfull"


@worker_task(key="delete.node.root")
def delete_node_root(self: TaskBase, task: TaskModel, request: TaskRequest):
    db = self.db
    node_name = request.path_param["name"]

    try:
        db.query(NodeModel).filter(NodeModel.name==node_name).one()
    except NoResultFound:
        raise Exception("Node not found")
    
    db.query(AssociationNodeToRole).filter(AssociationNodeToRole.node_name==node_name).delete()
    db.query(AssociationPoolsCpu).filter(AssociationPoolsCpu.node_name==node_name).delete()
    db.commit()
    db.query(NodeModel).filter(NodeModel.name==node_name).delete()
    db.commit()

    task.message = "Node delete has been successfull"

@worker_task(key="patch.node.role")
def patch_node_role(self: TaskBase, task: TaskModel, request: TaskRequest):
    db = self.db
    body = NodeRolePatch(**request.body)

    node_name = body.node_name
    add_role_name = body.role_name
    
    node:NodeModel = db.query(NodeModel).filter(NodeModel.name==node_name).one()

    if add_role_name == "libvirt":
        patch_node_role_libvirt(db=db, task=task, node=node)
    elif add_role_name == "ovs":
        patch_node_role_ovs(db=db, task=task, node=node, request=body)
    
    task.message = "Node patch has been successfull"


def patch_node_role_libvirt(db:Session, task: TaskModel, node:NodeModel):
    
    ansible_manager = AnsibleManager(user=node.user_name, domain=node.domain)

    res = ansible_manager.run_playbook_file("pb_init_libvirt")
    task.message = "ansible run successfull " + str(res["summary"])
    
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


def patch_node_role_ovs(db:Session, task: TaskModel, node:NodeModel, request:NodeRolePatch):
    
    ansible_manager = AnsibleManager(user=node.user_name, domain=node.domain)

    res = ansible_manager.run_playbook_file("pb_init_ovs")
    task.message = "ansible run successfull " + str(res["summary"])
    
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
    