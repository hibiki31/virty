from json import loads
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
from mixin.log import setup_logger
import os
from urllib.parse import urlparse

from .schemas import *
from task.models import TaskModel
from node.models import NodeModel
from storage.models import StorageModel

from module import virtlib
from module import xmllib
from module.ansiblelib import AnsibleManager

from time import time

from task.functions import TaskBase, TaskRequest


worker_task = TaskBase()
logger = setup_logger(__name__)


@worker_task(key="post.image.download")
def post_image_download(self: TaskBase, task: TaskModel, request: TaskRequest):
    db = self.db
    body = ImageDownloadForCreate(**request.body)
    
    storage_model = db.query(StorageModel).filter(StorageModel.uuid==body.storage_uuid).one()
    node_model = db.query(NodeModel).filter(NodeModel.name==storage_model.node_name).one()
    
    # フォルダ指定のみだとAnsible get_urlの都合で常にダウンロードされてしまうため
    url_parse = urlparse(body.image_url)
    url_filename = os.path.basename(url_parse.path)
    save_file_path = os.path.join(storage_model.path, url_filename)
    
    ansible_manager = AnsibleManager(user=node_model.user_name, domain=node_model.domain)
    ansible_manager.run_playbook_file(yaml="pb_wget", extra_vars=[{"url": body.image_url, "dest": save_file_path}])
    
    return f"save {body.image_url}"