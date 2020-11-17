from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session

from .models import *
from .schemas import *

from auth.router import CurrentUser, get_current_user
from task.models import TaskModel
from task.schemas import TaskSelect
from task.function import PostTask
from node.models import NodeModel
from mixin.database import get_db
from mixin.log import setup_logger

from module import virty
from module import virtlib
from module import xmllib


app = APIRouter()
logger = setup_logger(__name__)


exception_notfund = HTTPException(
    status_code=404,
    detail="Object not fund."
)


@app.put("/api/vms", tags=["vm"], response_model=TaskSelect)
async def put_api_domains(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    # タスクを追加
    post_task = PostTask(db=db, user=current_user, model=None)
    task_model = post_task.commit("vm","list","update")
   
    return task_model


@app.get("/api/vms", tags=["vm"],response_model=List[DomainSelect])
async def get_api_domain(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):

    return db.query(DomainModel).all()


@app.get("/api/vms/{uuid}", tags=["vm"])
async def get_api_domain(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        uuid:str = None
    ):
    try:
        domain:DomainModel = db.query(DomainModel).filter(DomainModel.uuid==uuid).one()
        node:NodeModel = db.query(NodeModel).filter(NodeModel.name==domain.node_name).one()
    except:
        raise exception_notfund

    editor = virtlib.XmlEditor("dom",domain.uuid)
    domain_xml_pase = editor.domain_parse()

    return {'db':domain, 'node': node, 'xml': domain_xml_pase}


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