import os
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from mixin.log import setup_logger
from models import ImageModel
from module.ansiblelib import AnsibleManager
from module.virtlib import VirtManager
from node.models import NodeModel
from storage.models import StorageModel
from storage.rescan import storage_rescan
from task.functions import TaskBase, TaskRequest, is_agent_task
from task.models import TaskModel

from .function import url_body_size
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
    if url_filename in {"", ".", ".."}:
        raise ValueError("image download URLにはfile名が必要です")
    save_file_path = os.path.join(storage_model.path, url_filename)
    if db.query(ImageModel).filter(
        ImageModel.storage_uuid == storage_model.uuid,
        (
            (ImageModel.path == save_file_path)
            | (ImageModel.name == url_filename)
        ),
    ).first() is not None:
        raise FileExistsError("同名または同一pathのimageは既に存在します")
    
    am = AnsibleManager(user=node_model.user_name, domain=node_model.domain)
    
    agent_hardened = is_agent_task(model)
    if agent_hardened:
        # submit時だけでなくnetwork access直前にもallowlist/DNSを再検査する。
        from agent.actions import validate_image_download_url

        validate_image_download_url(body.image_url)
    image_size = None if agent_hardened else url_body_size(url=body.image_url)
    if image_size is None:
        model.message = f"Start download Size unknown {url_filename}"
    else:
        model.message = f"Start download Size {image_size / (1024 * 1024):,.2f} MB {url_filename}"
    db.commit()
    
    am.run(
        playbook_name="commom/download_file_in_node",
        extravars={
            "url": body.image_url,
            "dest": save_file_path,
            "agent_hardened": agent_hardened,
            "allowed_hosts": [
                item.strip().lower()
                for item in os.getenv(
                    "AGENT_IMAGE_DOWNLOAD_ALLOWED_HOSTS",
                    "",
                ).split(",")
                if item.strip()
            ],
        },
        sensitive_keys={"url"},
    )
    
    storage_rescan(node=node_model, db=db, storage_uuids=[storage_model.uuid])
    
    
    if image_size is None:
        model.message = f"Saved image {url_filename} (size unknown)"
    else:
        model.message = (
            f"Saved Size {image_size / (1024 * 1024):,.2f} MB {url_filename}"
        )


@worker_task(key="delete.image.root")
def delete_image_root(db: Session, model: TaskModel, req: TaskRequest):
    storage_uuid = req.path_param["uuid"]
    image_name = req.path_param["name"]
    
    storage_model = db.query(StorageModel).filter(StorageModel.uuid==storage_uuid).one()
    node_model = db.query(NodeModel).filter(NodeModel.name==storage_model.node_name).one()
    
    virt = VirtManager(node_model=node_model)
    virt.image_delete(storage_uuid=storage_uuid, image_name=image_name, secure=False)
    
    db.query(ImageModel).filter(ImageModel.storage_uuid==storage_uuid, ImageModel.name==image_name).delete()
    db.commit()
    
    model.message = f"Successfly Delete image: {node_model.name} -> {storage_model.name} -> {image_name}"
