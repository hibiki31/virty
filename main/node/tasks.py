import yaml

from statistics import mode
from urllib import request

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
    ansible_manager = AnsibleManager(user=user, domain=domain)
    
    node_infomation = ansible_manager.node_infomation()

    memory = ssh_manager.get_node_mem()
    core = ssh_manager.get_node_cpu_core()
    cpu = ssh_manager.get_node_cpu_name()
    os = ssh_manager.get_node_os_release()
    qemu = ssh_manager.get_node_qemu_version()
    libvirt = ssh_manager.get_node_libvirt_version()

    print(os)

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
        qemu_version = qemu,
        libvirt_version = libvirt,
    )
    db.add(row)
    db.commit()

    return model


def patch_node_role(db: Session, model: TaskSelect):
    request = NodeRolePatch(**model.request)
    node_name = request.node_name
    add_role_name = request.role_name
    
    node:NodeModel = db.query(NodeModel).filter(NodeModel.name==node_name).one()
    ansible_manager = AnsibleManager(user=node.user_name, domain=node.domain)

    # res = ansible_manager.run_playbook_file("pb_init_libvirt")

    # model.message = "ansible run successfull " + str(res["summary"])

    try:
        role_model = db.query(NodeRoleModel).filter(NodeRoleModel.name=="libvirt").one()
    except NoResultFound as e:
        role_model = NodeRoleModel(name="libvirt")
        db.add(role_model)
        db.commit()

    node.roles.append(role_model)

    db.merge(node)
    db.commit()

    return model