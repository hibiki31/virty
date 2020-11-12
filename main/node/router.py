from fastapi import APIRouter, Depends, BackgroundTasks, Request
from sqlalchemy.orm import Session

from .models import *
from .schemas import *

from auth.router import get_current_user, CurrentUser
from task.models import TaskModel
from task.function import post_task

from mixin.database import get_db
from module import virty
from mixin.log import setup_logger

logger = setup_logger(__name__)


app = APIRouter()


def post_node_base(node: NodeInsert, db: Session):
    user = node.user_name
    domain = node.domain
    port = node.port
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
        name = node.name,
        domain = domain,
        description = node.description,
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

@app.post("/api/nodes", tags=["node"])
def post_api_nodes(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        node: NodeInsert = None,
        background_tasks: BackgroundTasks = None
    ):

    background_tasks.add_task(post_node_base, db=db, node=node)
    task_model = post_task(db=db, current_user=current_user, request_model=node, resource="node", object="base", method="post")
    
    return task_model

@app.get("/api/nodes", tags=["node"],response_model=List[NodeSelect])
async def get_api_nodes(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    return db.query(NodeModel).all()

@app.delete("/api/nodes", tags=["node"], response_model=List[NodeSelect])
async def delete_api_nodes(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        node: NodeDelete = None,
    ):
    model = db.query(NodeModel).filter(NodeModel.name==node.name).all()
    db.query(NodeModel).filter(NodeModel.name==node.name).delete()
    db.commit()
    return model