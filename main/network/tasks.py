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
        # ノードが変わる前に一度コミット
        db.commit()

    db.commit()
    # トークンで削除
    db.query(NetworkModel).filter(NetworkModel.update_token!=token).delete()
    db.commit()
    return model

def add_network_base(db: Session, model: TaskModel):
    request: NetworkInsert = NetworkInsert(**model.request)

    try:
        node: NodeModel = db.query(NodeModel).filter(NodeModel.name == request.node_name).one()
    except:
        raise Exception("node not found")

    # XMLを定義、設定
    editor = xmllib.XmlEditor("static","net_bridge")
    editor.network_bridge_edit(name=request.name, bridge=request.bridge_device)

    # ソイや！
    manager = virtlib.VirtManager(node_model=node)
    manager.network_define(xml_str=editor.dump_str())

    update_network_list(db=db, model=TaskModel())

    return model

def delete_network_base(db: Session, model: TaskModel):
    request: NetworkDelete = NetworkDelete(**model.request)

    try:
        network: NetworkModel = db.query(NetworkModel).filter(NetworkModel.uuid == request.uuid).one()
    except:
        raise Exception("network not found")

    try:
        node: NodeModel = db.query(NodeModel).filter(NodeModel.name == network.node_name).one()
    except:
        raise Exception("node not found")

    manager = virtlib.VirtManager(node_model=node)
    manager.network_undefine(request.uuid)

    update_network_list(db=db, model=TaskModel())

    return model