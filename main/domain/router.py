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
from module import virtlib
from module import xmllib


app = APIRouter()
logger = setup_logger(__name__)


@add_background_task(resource="domain", object="list", method="update")
async def put_domain_base(db: Session, cu: CurrentUser, model: TaskModel):
    nodes:NodeModel = db.query(NodeModel).all()
    for node in nodes:
        if node.status != 10:
            continue
        try:
            logger.info(f'ノードへ接続します: {node.user_name + "@" + node.domain}')
            manager = await virtlib.VirtEditor(node.user_name + "@" + node.domain)
        except:
            logger.error(f'ノードへの接続に失敗しました: {node.name}')
            continue

        domains = await manager.DomainAllData()

        logger.info("ドメイン数：" + str(len(domains)))

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


@app.post("/api/vms", tags=["vm"])
async def post_api_domains(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        node: DomainInsert = None,
        background_tasks: BackgroundTasks = None
    ):

    background_tasks.add_task(post_node_base, db=db, node=node)
    task_model = post_task(db=db, current_user=current_user, request_model=node, resource="node", object="base", method="post")
    
    return task_model

@app.put("/api/vms", tags=["vm"])
async def put_api_domains(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        background_tasks: BackgroundTasks = None
    ):

    task_model = put_domain_base(bg=background_tasks, db=db, cu=current_user, model=None)
    
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