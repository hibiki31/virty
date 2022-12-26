import os
import uuid
import logging
from datetime import datetime

from celery import Celery, Task
from celery.signals import after_setup_logger, after_setup_task_logger
from celery.utils.log import get_task_logger

from pydantic import BaseModel
from task.models import TaskModel

from sqlalchemy.orm import Session
from mixin.database import SessionLocal


celery = Celery(__name__,include=[
    'domain.tasks'
    ])

celery.conf.broker_url = os.environ.get(
    'CELERY_BROKER_URL',
    'redis://redis:6379'
)
celery.conf.result_backend = os.environ.get(
    'CELERY_BACKEND_URL',
    'redis://redis:6379'
)

logger = get_task_logger(__name__)


class BaseTask(Task):
    def __init__(self):
        self.db = SessionLocal()


@after_setup_logger.connect
def setup_root_logger(logger, *args, **kwargs):
    logger.handlers = []
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


@after_setup_task_logger.connect
def setup_task_logger(logger, *args, **kwargs):
    logger.handlers = []
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)



@celery.task(bind=True, base=BaseTask)
def task_error(self, *args, virty_task_uuid):
    print(self.request.id)
    # model = self.db.query(TaskModel).filter(TaskModel.uuid==virty_task_uuid).one()
    # model.status = "error"
    # model.message = exc
    # self.db.merge(model)
    # self.db.commit()

@celery.task
def error_handler(request, exc, traceback, virty_task_uuid):
    db = SessionLocal()
    model = db.query(TaskModel).filter(TaskModel.uuid==virty_task_uuid).one()
    model.status = "error"
    model.message = str(exc)
    db.commit()


@celery.task(bind=True, base=BaseTask)
def task_success(self) -> float:
    logger.info("iiiiiiiiiiiiiiiiiiiii")