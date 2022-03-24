from fastapi import BackgroundTasks

from sqlalchemy.orm import Session

from .models import *
from .schemas import *

from task.models import TaskModel
from node.models import NodeModel
from mixin.log import setup_logger

from module import virtlib
from module import xmllib

from time import time


logger = setup_logger(__name__)


def put_storage_list(db:Session, bg: BackgroundTasks, task: TaskModel):
    nodes = db.query(NodeModel).all()

    token = time()

    for node in nodes:
        if node.status != 10:
            continue

        manager = virtlib.VirtManager(node_model=node)

        storages = manager.storage_data(token=token)
        for storage in storages:
            storage_model = StorageModel(
                uuid=storage.uuid,
                name=storage.name,
                node_name=storage.node_name,
                capacity=storage.capacity,
                available=storage.available,
                path=storage.path,
                active=storage.active,
                auto_start=storage.auto_start,
                status=storage.status,
                update_token=storage.update_token
            )
            for image in storage.images:
                image_model = ImageModel(
                    name=image.name,
                    storage_uuid=image.storage_uuid,
                    capacity=image.capacity,
                    allocation=image.allocation,
                    path=image.path,
                    update_token=image.update_token
                )
                db.merge(image_model)
            # ストレージを登録
            db.merge(storage_model)
    db.commit()
    # トークンで除外
    db.query(StorageModel).filter(StorageModel.update_token!=str(token)).delete()
    db.query(ImageModel).filter(ImageModel.update_token!=str(token)).delete()
    db.commit()
    task.message = "Storage list updated has been successfull"

def add_storage_base(db:Session, bg: BackgroundTasks, task: TaskModel):
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

def delete_storage_base(db:Session, bg: BackgroundTasks, task: TaskModel):
    request: StorageDelete = StorageDelete(**model.request)

    try:
        node: NodeModel = db.query(NodeModel).filter(NodeModel.name == request.node_name).one()
    except:
        raise Exception("node not found")

    manager = virtlib.VirtManager(node_model=node)
    manager.storage_undefine(request.uuid)

    # update_storage_list(db=db, model=TaskModel())

    db.query(StorageModel).filter(StorageModel.uuid==request.uuid).delete()
    db.commit()

    return model