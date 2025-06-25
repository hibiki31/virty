import os

from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from mixin.log import setup_logger
from module.ansiblelib import AnsibleManager
from module.paramikolib import ParamikoManager
from module.virtlib import NetworkAlreadyExistsError, StoragePoolAlreadyExistsError
from network.create import create_network
from network.schemas import NetworkDHCPForCreate, NetworkForCreate, NetworkIPForCreate
from storage.create import create_storage
from task.functions import TaskBase, TaskRequest
from task.models import TaskModel

from .models import AssociationNodeToRoleModel, NodeModel, NodeRoleModel
from .schemas import NodeForCreate, NodeRoleForUpdate

worker_task = TaskBase()
logger = setup_logger(__name__)


@worker_task(key="post.node.root")
def post_node_root(db: Session, model: TaskModel, req: TaskRequest):
    body = NodeForCreate.model_validate(req.body)
    

    user = body.user_name
    domain = body.domain
    port = body.port

    ssh_manager = ParamikoManager(user=user, domain=domain, port=port)
    ansible_manager = AnsibleManager(user=user, domain=domain)
    node_infomation = ansible_manager.node_infomation()

    ssh_role = db.query(NodeRoleModel).filter(NodeRoleModel.name=="ssh").one_or_none()
    if ssh_role is None:
        ssh_role = NodeRoleModel(name="ssh")
        db.add(ssh_role)

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
        ansible_facts = node_infomation,
        qemu_version = None,
        libvirt_version = None,
    )
    a = AssociationNodeToRoleModel(extra_json={})
    a.role = ssh_role
    row.roles.append(a)
    db.add(row)
    db.commit()

    model.message = "Node added has been successfull"


@worker_task(key="delete.node.root")
def delete_node_root(db: Session, model: TaskModel, req: TaskRequest):
    node_name = req.path_param["name"]

    try:
        db.query(NodeModel).filter(NodeModel.name==node_name).one()
    except NoResultFound:
        raise Exception("Node not found")
    
    db.query(AssociationNodeToRoleModel).filter(AssociationNodeToRoleModel.node_name==node_name).delete()
    db.commit()
    db.query(NodeModel).filter(NodeModel.name==node_name).delete()
    db.commit()

    model.message = "Node delete has been successfull"

@worker_task(key="patch.node.role")
def patch_node_role(db: Session, model: TaskModel, req: TaskRequest):
    body = NodeRoleForUpdate.model_validate(req.body)

    node_name = body.node_name
    add_role_name = body.role_name
    
    node = db.query(NodeModel).filter(NodeModel.name==node_name).one()

    if add_role_name == "libvirt":
        patch_node_role_libvirt(db=db, task=model, node=node)
    elif add_role_name == "ovs":
        patch_node_role_ovs(db=db, task=model, node=node, request=body)
    # elif add_role_name == "vxlan_overlay":
    #     patch_node_role_vxlan_overlay(db=db, task=model, node=node, request=body)
    
    for i in ["virty-vm-image", "virty-installer-iso", "virty-template-image"]:
        try:
            create_storage(
                storage_name=i,
                storage_path=os.path.join("/var/virty/", i),
                node=node
            )
        except StoragePoolAlreadyExistsError:
            logger.info(f'Skip {node.name} {os.path.join("/var/virty/", i)}')
    
    network_body = NetworkForCreate(
        name="virty-nat",
        node_name=node.name,
        forward_mode='nat',
        dhcp=NetworkDHCPForCreate(start="192.168.177.1", end="192.168.177.200"),
        ip=NetworkIPForCreate(address="192.168.177.254", netmask="255.255.255.0")
    )
    
    try:
        create_network(body=network_body, node=node)
    except NetworkAlreadyExistsError:
        logger.info(f'Skip {node.name} "virty-net')
    
    model.message = "Node patch has been successfull"


# def patch_node_role_vxlan_overlay(db:Session, task: TaskModel, node:NodeModel, request:NodeRolePatch):
#     ansible_manager = AnsibleManager(user=node.user_name, domain=node.domain)
    
#     role_model = db.query(NodeRoleModel).filter(NodeRoleModel.name=="vxlan_overlay").one_or_none()
    
#     if role_model == None:
#         role_model = NodeRoleModel(name="vxlan_overlay")
#         db.add(role_model)

#     if not db.query(AssociationNodeToRole).filter(
#             AssociationNodeToRole.node_name==node.name, 
#             AssociationNodeToRole.role_name=="vxlan_overlay"
#         ).one_or_none():
#         a = AssociationNodeToRole(extra_json=request.extra_json)
#         a.role = role_model
#         node.roles.append(a)

#     db.commit()

#     return node

def patch_node_role_libvirt(db:Session, task: TaskModel, node:NodeModel):
    
    ansible_manager = AnsibleManager(user=node.user_name, domain=node.domain)

    res = ansible_manager.run(playbook_name="pb_init_libvirt")
    task.message = "ansible run successfull " + str(res.status)
    
    role_model = db.query(NodeRoleModel).filter(NodeRoleModel.name=="libvirt").one_or_none()
    
    if role_model is None:
        role_model = NodeRoleModel(name="libvirt")
        db.add(role_model)
    
    ssh_manager = ParamikoManager(user=node.user_name, domain=node.domain, port=node.port)

    node.qemu_version = ssh_manager.get_node_qemu_version()
    node.libvirt_version = ssh_manager.get_node_libvirt_version()

    if not db.query(AssociationNodeToRoleModel).filter(
            AssociationNodeToRoleModel.node_name==node.name, 
            AssociationNodeToRoleModel.role_name=="libvirt"
        ).one_or_none():
        a = AssociationNodeToRoleModel(extra_json={})
        a.role = role_model
        node.roles.append(a)

    db.commit()


def patch_node_role_ovs(db:Session, task: TaskModel, node:NodeModel, request:NodeRoleForUpdate):
    
    ansible_manager = AnsibleManager(user=node.user_name, domain=node.domain)

    res = ansible_manager.run_playbook_file("pb_init_ovs")
    task.message = "ansible run successfull " + str(res["summary"])
    
    role_model = db.query(NodeRoleModel).filter(NodeRoleModel.name=="ovs").one_or_none()
    
    if role_model == None:
        role_model = NodeRoleModel(name="ovs")
        db.add(role_model)

    if not db.query(AssociationNodeToRoleModel).filter(
            AssociationNodeToRoleModel.node_name==node.name, 
            AssociationNodeToRoleModel.role_name=="ovs"
        ).one_or_none():
        a = AssociationNodeToRoleModel(extra_json=request.extra_json)
        a.role = role_model
        node.roles.append(a)

    db.commit()

    return node
    