from fastapi import APIRouter, Depends, BackgroundTasks, Request
from sqlalchemy.orm import Session

from .models import *
from .schemas import *

from auth.router import CurrentUser, get_current_user
from task.models import TaskModel
from task.function import add_background_task
from mixin.database import get_db
from mixin.log import setup_logger

# 非共通モジュール
from node.models import NodeModel
from module import virty


app = APIRouter()
logger = setup_logger(__name__)


@add_background_task(resource="node", object="base", method="post")
def post_node_base(db: Session, cu: CurrentUser, model: TaskModel):
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

@app.post("/api/nodes", tags=["node"])
async def post_api_nodes(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        node: NodeInsert = None,
        background_tasks: BackgroundTasks = None
    ):
    # タスクを追加
    task_model = post_node_base(bg=background_tasks, db=db, cu=current_user, model=node)
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