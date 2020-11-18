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


def update_network_list(db: Session, model: TaskModel):
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

        for network in manager.network_data(token=token):
            network: NetworkModel
            network.node_name = node.name
            db.merge(network)
            print(network)

    db.commit()
    return model