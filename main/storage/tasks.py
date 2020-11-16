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
    return model