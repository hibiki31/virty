import os
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from mixin.log import setup_logger
from module.ansiblelib import AnsibleManager
from node.models import NodeModel
from storage.models import StorageModel
from task.functions import TaskBase, TaskRequest
from task.models import TaskModel

from .schemas import ImageDownloadForCreate

worker_task = TaskBase()
logger = setup_logger(__name__)


@worker_task(key="post.image.download")
def post_image_download(db: Session, model: TaskModel, req: TaskRequest):

    body = ImageDownloadForCreate.model_validate(req.body)
    
    storage_model = db.query(StorageModel).filter(StorageModel.uuid==body.storage_uuid).one()
    node_model = db.query(NodeModel).filter(NodeModel.name==storage_model.node_name).one()
    
    # フォルダ指定のみだとAnsible get_urlの都合で常にダウンロードされてしまうため
    url_parse = urlparse(body.image_url)
    url_filename = os.path.basename(url_parse.path)
    save_file_path = os.path.join(storage_model.path, url_filename)
    
    
    
    am = AnsibleManager(user=node_model.user_name, domain=node_model.domain)
    db.close_all()
    
    am.run(
        playbook_name="pb_wget",
        extravars={"url": body.image_url, "dest": save_file_path}
    )
    
    return f"save {body.image_url}"