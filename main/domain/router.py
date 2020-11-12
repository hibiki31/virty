from fastapi import APIRouter, Depends, BackgroundTasks, Request
from sqlalchemy.orm import Session

from .models import *
from .schemas import *

from auth.router import get_current_user, CurrentUser
from task.models import TaskModel
from task.function import post_task

# 任意
from node.models import NodeModel

from module import virty
from module import virtlib
from module import xmllib
from mixin.database import get_db
from mixin.log import setup_logger

logger = setup_logger(__name__)


app = APIRouter()


def put_domain_base(db: Session):
    nodes:NodeModel = db.query(NodeModel).all()
    for node in nodes:
        if node.status != 10:
            continue
        try:
            logger.info(f'ノードへ接続します: {node.user_name + "@" + node.domain}')
            manager = virtlib.VirtEditor(node.user_name + "@" + node.domain)
        except:
            logger.error(f'ノードへの接続に失敗しました: {node.name}')
            continue

        domains = manager.DomainAllData()

        for domain in domains:
            editor = xmllib.XmlEditor("str",domain['xml'])
            editor.dump_file("domain")
            temp = editor.domain_parse()
            
            row = DomainModel(
                uuid = temp["uuid"],
                name = temp['name'],
                core = temp['vcpu'],
                memory = temp['memory'],
                status = domain['status'],
                node_name = node.name,
                is_lost = False
            )
            db.merge(row)
    db.commit()

def queue_task(
        background_tasks: BackgroundTasks,
        db: Session,
        current_user: CurrentUser,
        model,
        resource: str,
        object: str,
        method: str,
        func,
    ):
    task_model = post_task(db=db, current_user=current_user, request_model=None, resource="domain", object="base", method="put")
    background_tasks.add_task(func, db=db)
    return task_model





@app.post("/api/vms", tags=["vm"])
def post_api_domains(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        node: DomainInsert = None,
        background_tasks: BackgroundTasks = None
    ):

    background_tasks.add_task(post_node_base, db=db, node=node)
    task_model = post_task(db=db, current_user=current_user, request_model=node, resource="node", object="base", method="post")
    
    return task_model

@app.put("/api/vms", tags=["vm"])
def put_api_domains(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        background_tasks: BackgroundTasks = None
    ):

    task_model = queue_task(
        background_tasks=background_tasks,
        db=db,
        current_user=current_user,
        model=None,
        resource="domain",
        object="base",
        method="put",
        func=put_domain_base
    )
    
    
    return task_model

@app.get("/api/vms", tags=["vm"],response_model=List[DomainSelect])
async def get_api_domain(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    return db.query(DomainModel).all()

@app.delete("/api/vms", tags=["vm"], response_model=List[DomainSelect])
async def delete_api_domains(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        node: DomainDelete = None,
    ):
    model = db.query(DomainModel).filter(DomainModel.name==node.name).all()
    db.query(DomainModel).filter(DomainModel.name==node.name).delete()
    db.commit()
    return model