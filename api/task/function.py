import uuid
import copy

from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
from fastapi_camelcase import CamelModel


from task.models import TaskModel
from auth.router import CurrentUser
from mixin.log import setup_logger

from worker import do_task


logger = setup_logger(__name__)


class PostTask():
    def __init__(self, db:Session, user:CurrentUser, model: BaseModel):
        self.db = db
        self.user = user
        self.model = model
    
    def commit(self, resource, object, method, bg=None, status="init", dependence_uuid=None):
        uuid_str = str(uuid.uuid4())
        time = datetime.now()
        user_id = self.user.id

        if self.model == None:
            self.model = BaseModel()

        row = TaskModel(
            uuid = uuid_str,
            post_time = time,
            run_time = 0,
            user_id = user_id,
            status = status,
            dependence_uuid = dependence_uuid,
            resource = resource,
            object = object,
            method = method,
            request = self.model.json(),
            message = "queing task"
        )

        res = copy.copy(row)

        self.db.add(row)
        self.db.commit()

        if bg:
            bg.add_task(do_task,db=self.db)
        
        return res


class TaskManager():
    def __init__(self, db:Session, user:CurrentUser, model: BaseModel, bg: BackgroundTasks):
        self.db = db
        self.user = user
        self.bg = bg
    
    def commit(self, method, resource, object, request: CamelModel=CamelModel(), dependence_uuid=None):
        status = "init" if dependence_uuid else "wait"
        uuid_str = str(uuid.uuid4())
        time = datetime.now()
        user_id = self.user.id

        self.model = TaskModel(
            uuid = uuid_str,
            post_time = time,
            run_time = 0,
            user_id = user_id,
            status = status,
            dependence_uuid = dependence_uuid,
            resource = resource,
            object = object,
            method = method,
            request = request.json(),
            message = "queing task"
        )

        self.db.add(self.model)
        self.db.commit()

        self.bg.add_task(task_runner,manager=self)
        
        return self.db.query(TaskModel).filter(TaskModel.uuid==uuid_str)

def task_runner(manager:TaskManager, mode="init"):
    tasks = manager.db.query(TaskModel)\
        .filter(TaskModel.status==mode)\
        .order_by(TaskModel.post_time)\
        .with_lockmode('update').all()
    
    # 新規タスク処理
    if mode == "init":
        task:TaskModel = tasks[0]
        logger.info(f'find tasks: {task.resource}.{task.object}.{task.method} {task.uuid}')
        exec(f"{task.method}_{task.resource}_{task.object}(manager=manager)")
        return