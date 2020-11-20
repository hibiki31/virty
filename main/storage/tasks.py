from sqlalchemy.orm import Session

from .models import *
from .schemas import *

from task.models import TaskModel
from node.models import NodeModel
from mixin.log import setup_logger

from module import virty
from module import virtlib
from module import xmllib

from time import time


logger = setup_logger(__name__)


def update_storage_list(db: Session, model: TaskModel):
    nodes = db.query(NodeModel).all()

    token = time()

    for node in nodes:
        if node.status != 10:
            continue
        try:
            logger.info(f'ノードへ接続します: {node.user_name + "@" + node.domain}')
            manager = virtlib.VirtManager(node_model=node)
        except:
            logger.error(f'ノードへの接続に失敗しました: {node.name}')
            continue

        storages = manager.storage_data(token=token)
        for storage in storages:
            for image in storage["image"]:
                image = ImageModel(**image.dict())
                image.storage_uuid = storage["storage"].uuid
                db.merge(image)
            db.merge(storage["storage"])
    db.commit()
    # トークンで除外
    db.query(StorageModel).filter(StorageModel.update_token!=token).delete()
    db.query(ImageModel).filter(ImageModel.update_token!=token).delete()
    db.commit()
    return model

def add_storage_base(db: Session, model: TaskModel):
    request: StorageInsert = StorageInsert(**model.request)

    try:
        node: NodeModel = db.query(NodeModel).filter(NodeModel.name == request.node_name).one()
    except:
        raise Exception("node not found")

    # XMLを定義、設定
    editor = xmllib.XmlEditor("static","storage_dir")
    editor.storage_base_edit(name=request.name, path=request.path)

    # ソイや！
    manager = virtlib.VirtManager(node_model=node)
    manager.storage_define(xml_str=editor.dump_str())

    update_storage_list(db=db, model=TaskModel())

    return model

def delete_storage_base(db: Session, model: TaskModel):
    request: StorageDelete = StorageDelete(**model.request)

    try:
        node: NodeModel = db.query(NodeModel).filter(NodeModel.name == request.node_name).one()
    except:
        raise Exception("node not found")

    manager = virtlib.VirtManager(node_model=node)
    manager.storage_undefine(request.uuid)

    update_storage_list(db=db, model=TaskModel())

    return model