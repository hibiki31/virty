from sqlalchemy.orm import Session

from .models import *
from .schemas import *

from task.models import TaskModel
from node.models import NodeModel
from mixin.log import setup_logger

from module import virty
from module import virtlib
from module import xmllib


logger = setup_logger(__name__)


def update_domain_list(db: Session, model: TaskModel):
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
                update_token = ""
            )
            db.merge(row)
    db.commit()
    return model