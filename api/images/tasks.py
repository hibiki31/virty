from json import loads
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
from mixin.log import setup_logger

from .schemas import *
from task.models import TaskModel
from node.models import NodeModel

from module import virtlib
from module import xmllib
from module.ansiblelib import AnsibleManager

from time import time

from task.functions import TaskBase, TaskRequest


worker_task = TaskBase()
logger = setup_logger(__name__)


@worker_task(key="post.images.iso")
def post_images_iso(self: TaskBase, task: TaskModel, request: TaskRequest):
    db = self.db
    body = StorageInsert(**request.body)

