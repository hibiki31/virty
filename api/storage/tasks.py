from time import time

from sqlalchemy.orm import Session

from mixin.log import setup_logger
from module import virtlib
from node.models import NodeModel
from storage.create import create_storage
from task.functions import TaskBase, TaskRequest
from task.models import TaskModel

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

    create_storage(
        storage_name=body.name,
        storage_path=body.path,
        node=node
    )
    

    model.message = "Storage append has been successfull"


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