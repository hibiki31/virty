from sqlalchemy.orm import Session

from .models import *
from .schemas import *

from task.schemas import TaskSelect
from mixin.log import setup_logger

from node.models import NodeModel
from module import virtlib
from module import xmllib
from module import sshlib
from module.ansiblelib import AnsibleManager


logger = setup_logger(__name__)


def post_node_base(db: Session, model: TaskSelect):
    request = NodeInsert(**model.request)
    user = request.user_name
    domain = request.domain
    port = request.port

    ssh_manager = sshlib.SSHManager(user=user, domain=domain)
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
    try:
        db.commit()
    except:
        pass
    db.close()
    return model