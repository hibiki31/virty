import uuid
import json

from time import time
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks

from task.models import TaskModel
from mixin.log import setup_logger

from worker import task_error, task_success, error_handler


logger = setup_logger(__name__)


class TaskManager():
    def __init__(self, db:Session, bg: BackgroundTasks=None):
        self.db = db
        self.bg = bg
    
    def select(self, method, resource, object):
        self.method = method
        self.resource = resource
        self.object = object
    
    def commit(self, user, dependence_uuid=None, request: BaseModel= BaseModel()):
        status = "wait" if dependence_uuid else "init"
        task_uuid = str(uuid.uuid4())

        self.db.add(TaskModel(
            uuid = task_uuid,
            post_time = datetime.now(),
            run_time = 0,
            user_id = user.id,
            status = status,
            dependence_uuid = dependence_uuid,
            resource = self.resource,
            object = self.object,
            method = self.method,
            request = request.json(),
            message = "Task has been queued"
        ))
        self.db.commit()

        self.model = self.db.query(TaskModel).filter(TaskModel.uuid==task_uuid).one()

        if self.bg:
            self.bg.add_task(task_scheduler,db=self.db, bg=self.bg)
        else:
            task_runner(db=self.db, bg=self.bg, task=self.model)
    
    def folk(self, task:TaskModel, dependence_uuid=None, request: BaseModel= BaseModel()):
        status = "wait" if dependence_uuid else "init"
        status = status if self.bg else "start"
        task_uuid = str(uuid.uuid4())

        self.db.add(TaskModel(
            uuid = task_uuid,
            post_time = datetime.now(),
            run_time = 0,
            user_id = task.user_id,
            status = status,
            dependence_uuid = dependence_uuid,
            resource = self.resource,
            object = self.object,
            method = self.method,
            request = request.json(),
            message = "Task has been queued"
        ))
        self.db.commit()

        self.model = self.db.query(TaskModel).filter(TaskModel.uuid==task_uuid).one()

        if self.bg:
            self.bg.add_task(task_scheduler,db=self.db, bg=self.bg)
        else:
            task_runner(db=self.db, bg=self.bg, task=self.model)


class TaskManager():
    def __init__(self, db:Session):
        self.db = db


    def select(self, method, resource, object, celery_task):
        self.method = method
        self.resource = resource
        self.object = object
        self.celery_task = celery_task
    
    def commit(self, user, dependence_uuid=None, request: BaseModel= BaseModel()):
        status = "wait" if dependence_uuid else "init"
        task_uuid = str(uuid.uuid4())

        self.db.add(TaskModel(
            uuid = task_uuid,
            post_time = datetime.now(),
            run_time = 0,
            user_id = user.id,
            status = status,
            dependence_uuid = dependence_uuid,
            resource = self.resource,
            object = self.object,
            method = self.method,
            request = request.json(),
            message = "Task has been queued"
        ))
        self.db.commit()

        self.model = self.db.query(TaskModel).filter(TaskModel.uuid==task_uuid).one()

        # if self.bg:
        #     self.bg.add_task(task_scheduler,db=self.db, bg=self.bg)
        # else:
        #     task_runner(db=self.db, bg=self.bg, task=self.model)
        self.celery_task.apply_async(
            link_error=error_handler.s(virty_task_uuid=task_uuid),
            # link_error=task_error.s(virty_task_uuid=task_uuid),
            link=task_success.s(virty_task_uuid=task_uuid)
        )
    
    def folk(self, task:TaskModel, dependence_uuid=None, request: BaseModel= BaseModel()):
        status = "wait" if dependence_uuid else "init"
        status = status if self.bg else "start"
        task_uuid = str(uuid.uuid4())

        self.db.add(TaskModel(
            uuid = task_uuid,
            post_time = datetime.now(),
            run_time = 0,
            user_id = task.user_id,
            status = status,
            dependence_uuid = dependence_uuid,
            resource = self.resource,
            object = self.object,
            method = self.method,
            request = request.json(),
            message = "Task has been queued"
        ))
        self.db.commit()

        self.model = self.db.query(TaskModel).filter(TaskModel.uuid==task_uuid).one()

        if self.bg:
            self.bg.add_task(task_scheduler,db=self.db, bg=self.bg)
        else:
            task_runner(db=self.db, bg=self.bg, task=self.model)

def task_scheduler(db:Session, bg: BackgroundTasks, mode="init"):
    tasks = db.query(
        TaskModel
    ).filter(
        TaskModel.status==mode
    ).order_by(TaskModel.post_time).with_for_update().all()
    
    if tasks == [] and mode == "init":
        logger.info("init task not found")
        task_scheduler(db=db, bg=bg, mode="wait")
        return
    
    if tasks == [] and mode == "wait":
        logger.info("wait task not found")
        return

    # タスク処理
    if mode == "init":
        task:TaskModel = tasks[0]
        task.status = 'start'
        db.commit()
        task_runner(db=db, bg=bg, task=task)
        task_scheduler(db=db, bg=bg)
        return
    
    for task in tasks:
        # 依存先のuuidが実在するかチェック
        try:
            if task.dependence_uuid == None:
                raise Exception()
            depends_task:TaskModel = db.query(TaskModel)\
                .filter(TaskModel.uuid==task.dependence_uuid)\
                .with_lockmode('update').one()
        except:
            task.status = "error"
            task.message = "not found depended task"
            db.merge(task)
            db.commit()
            logger.error(f"not found depended task {task.uuid} => {task.dependence_uuid}")
            continue
  
        # 親タスクが死んだ場合エラーで停止
        if depends_task.status == "error":
            task.status = "error"
            task.message = "depended task faile"
            db.merge(task)
            db.commit()
            logger.error(f"depended task faile {task.uuid} => {task.dependence_uuid}")
            continue
        
        # 親タスクが実行中の場合待機
        elif depends_task.status != "finish":
            logger.info(f"wait depended task. {task.uuid} => {task.dependence_uuid}")
            continue
        
        # 実行可能なタスクは初期化
        elif depends_task.status == "finish" and task.status == "wait":
            task.status = "init"
            db.merge(task)
            db.commit()
            logger.error(f"init depended task {task.uuid} => {task.dependence_uuid}")
            task_scheduler(db=db, bg=bg)
    task_scheduler(db=db, bg=bg)

def task_runner(db:Session, bg: BackgroundTasks, task: TaskModel):
    logger.info(f'find tasks: {task.resource}.{task.object}.{task.method} {task.uuid}')
    start_time = time()
    
    try:
        exec(f"{task.method}_{task.resource}_{task.object}(db=db, bg=bg, task=task)")
        task.status = "finish"
    except Exception as e:
        db.rollback()
        logger.error(e, exc_info=True)
        task.status = "error"
        task.message = str(e)

    task.run_time = time() - start_time
    db.commit()



from project.tasks import *
from domain.tasks import *
from node.tasks import *
from network.tasks import *
from storage.tasks import *