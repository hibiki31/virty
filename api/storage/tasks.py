from json import loads
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
from mixin.log import setup_logger

from .models import *
from .schemas import *
from task.models import TaskModel
from node.models import NodeModel

from module import virtlib
from module import xmllib
from module.ansiblelib import AnsibleManager

from time import time

from task.functions import TaskBase


worker_task = TaskBase()
logger = setup_logger(__name__)


@worker_task(key="put.storage.list")
def put_storage_list(self: TaskBase, task: TaskModel):
    db = self.db
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


@worker_task(key="post.storage.root")
def post_storage_root(self: TaskBase, task: TaskModel):
    db = self.db
    request: StorageInsert = StorageInsert(**loads(task.request))

    try:
        node: NodeModel = db.query(NodeModel).filter(NodeModel.name == request.node_name).one()
    except:
        raise Exception("node not found")

    # XMLを定義、設定
    editor = xmllib.XmlEditor("static","storage_dir")
    editor.storage_base_edit(name=request.name, path=request.path)

    ansible_manager = AnsibleManager(user=node.user_name, domain=node.domain)
    ansible_manager.run_playbook_file(
        yaml="pb_make_dir_recurse",
        extra_vars=[{"path": request.path}]
    )

    # ソイや！
    manager = virtlib.VirtManager(node_model=node)
    manager.storage_define(xml_str=editor.dump_str())

    task.message = "Storage append has been successfull"


@worker_task(key="delete.storage.root")
def delete_storage_root(self: TaskBase, task: TaskModel):
    db = self.db

    try:
        node: NodeModel = db.query(NodeModel).filter(NodeModel.name == task.node_name).one()
    except:
        raise Exception("node not found")

    manager = virtlib.VirtManager(node_model=node)
    manager.storage_undefine(task.uuid)

    db.query(StorageModel).filter(StorageModel.uuid==task.uuid).delete()
    db.commit()

    return task