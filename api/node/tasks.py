import os
from ipaddress import ip_address

from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from mixin.log import setup_logger
from module.backends import create_ansible_backend, create_ssh_backend
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

    ssh_manager = create_ssh_backend(user=user, domain=domain, port=port)
    ansible_manager = create_ansible_backend(user=user, domain=domain)
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
        core = int(ssh_manager.get_node_cpu_core()),
        memory = int(ssh_manager.get_node_mem()),
        cpu_gen = ssh_manager.get_node_cpu_name(),
        os_like = ssh_manager.get_node_os_release()["ID_LIKE"],
        os_name = ssh_manager.get_node_os_release()["PRETTY_NAME"],
        os_version = ssh_manager.get_node_os_release()["VERSION_ID"],
        status = 10,
        ansible_facts = dict(node_infomation),
    )
    row.qemu_version = None
    row.libvirt_version = None
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
    node = db.query(NodeModel).filter(NodeModel.name==node_name).one()
    patch_node_role_libvirt(db=db, task=model, node=node)
    
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
        dhcp=NetworkDHCPForCreate(
            start=ip_address("192.168.177.1"),
            end=ip_address("192.168.177.200"),
        ),
        ip=NetworkIPForCreate(
            address=ip_address("192.168.177.254"),
            netmask=ip_address("255.255.255.0"),
        )
    )
    
    try:
        create_network(body=network_body, node=node)
    except NetworkAlreadyExistsError:
        logger.info(f'Skip {node.name} "virty-net')
    
    model.message = "Node patch has been successfull"

def patch_node_role_libvirt(db:Session, task: TaskModel, node:NodeModel):
    
    ansible_manager = create_ansible_backend(user=node.user_name, domain=node.domain)

    res = ansible_manager.run(playbook_name="pb_init_libvirt")
    task.message = "ansible run successfull " + str(res.status)
    
    role_model = db.query(NodeRoleModel).filter(NodeRoleModel.name=="libvirt").one_or_none()
    
    if role_model is None:
        role_model = NodeRoleModel(name="libvirt")
        db.add(role_model)
    
    ssh_manager = create_ssh_backend(
        user=node.user_name,
        domain=node.domain,
        port=node.port,
    )

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
