from sqlalchemy.orm import Session

from .models import *
from .schemas import *

from task.models import TaskModel
from mixin.log import setup_logger

from node.models import NodeModel
from module import virty
from module import virtlib
from module import xmllib


logger = setup_logger(__name__)


def post_node_base(db: Session, model: TaskModel):
    user = model.request.user_name
    domain = model.request.domain
    port = model.request.port
    try:
        memory = virty.SshInfoMem(user, domain, port)
        core = virty.SshInfocpu(user, domain, port)
        cpu = virty.SshInfocpuname(user, domain, port)
        os = virty.SshOsinfo(user, domain, port)
        qemu = virty.SshInfoQemu(user, domain, port)
        libvirt = virty.SshInfoLibvirt(user, domain, port)
    except Exception as e:
        return None

    row = NodeModel(
        name = model.request.name,
        domain = domain,
        description = model.request.description,
        user_name = user,
        port = port,
        core = core,
        memory = memory,
        cpu_gen = cpu,
        os_like = os["ID_LIKE"],
        os_name = os["NAME"],
        os_version = os["VERSION"],
        status = 10,
        qemu_version = qemu,
        libvirt_version = libvirt,
    )
    db.add(row)
    db.commit()
    return model