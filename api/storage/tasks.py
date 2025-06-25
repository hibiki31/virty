from time import time

from sqlalchemy.orm import Session

from mixin.log import setup_logger
from module import virtlib, xmllib
from module.ansiblelib import AnsibleManager
from node.models import NodeModel
from task.functions import TaskBase, TaskRequest
from task.models import TaskModel

from .function import is_safe_fullpath
from .models import StorageModel
from .rescan import storage_rescan
from .schemas import StorageForCreate

worker_task = TaskBase()
logger = setup_logger(__name__)


@worker_task(key="put.storage.list")
def put_storage_list(db: Session, model: TaskModel, req: TaskRequest):
    nodes = db.query(NodeModel).all()
    token = str(time())

    for node in nodes:
        storage_rescan(token=token, node=node, db=db)
       
    model.message = "Storage list updated has been successfull"


@worker_task(key="post.storage.root")
def post_storage_root(db: Session, model: TaskModel, req: TaskRequest):
    body = StorageForCreate.model_validate(req.body)

    try:
        node: NodeModel = db.query(NodeModel).filter(
            NodeModel.name == body.node_name
        ).one()
    except Exception:
        raise Exception("node not found")

    # XMLを定義、設定
    editor = xmllib.XmlEditor("static","storage_dir")
    editor.storage_base_edit(name=body.name, path=body.path)

    am = AnsibleManager(user=node.user_name, domain=node.domain)
    
    db.close_all()
    if not is_safe_fullpath(body.path):
        raise Exception(f"The specified path is not a safe full path. {body.path}")
    am.run(
        playbook_name="commom/make_dir_recurse",
        extravars={"path": body.path}
    )

    # ソイや！
    manager = virtlib.VirtManager(node_model=node)
    manager.storage_define(xml_str=editor.dump_str())

    # model.message = "Storage append has been successfull"


@worker_task(key="delete.storage.root")
def delete_storage_root(db: Session, model: TaskModel, req: TaskRequest):
    uuid = req.path_param["uuid"]

    storage:StorageModel = db.query(StorageModel).filter(
        StorageModel.uuid == uuid
    ).one()
    node: NodeModel = db.query(NodeModel).filter(
        NodeModel.name == storage.node_name
    ).one()

    manager = virtlib.VirtManager(node_model=node)
    manager.storage_undefine(uuid)

    db.query(StorageModel).filter(StorageModel.uuid==uuid).delete()
    db.commit()

    model.message = "Storage delete has been successfull"