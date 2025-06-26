import json
import uuid
from datetime import datetime
from time import time

from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from mixin.database import SessionLocal
from mixin.log import setup_logger
from mixin.schemas import BaseSchema
from task.models import TaskModel
from task.schemas import TaskRequest

logger = setup_logger(__name__)

class TaskBase:
    def __init__(self):
        self.task_func = {}

    def __call__(self, key):
        def receive_func(f):
            logger.info(f"Register task {key}")
            self.task_func[key] = f

            def wrapper(*args, **kwargs):
                return f(*args, **kwargs)
            return wrapper
        return receive_func
    
    def include_task(self, tb):
        self.task_func.update(tb.task_func)
    
    def run(self, key, task_uuid):
        if key not in self.task_func:
            raise Exception("Task not found")
        
        with SessionLocal() as db:
            task_model = db.query(TaskModel).filter(TaskModel.uuid == task_uuid).one()
            db.commit()
            return self.task_func[key](db=db, model=task_model, req=TaskRequest(**json.loads(task_model.request)))




class TaskManager():
    def __init__(self, db:Session):
        self.db = db

    def select(self, method, resource, object):
        self.method = method
        self.resource = resource
        self.object = object
    
    def commit(
            self, user, req=None, 
            body: BaseSchema=BaseSchema(), param={}, dep_uuid=None
        ):
        status = "wait" if dep_uuid else "init"
        task_uuid = str(uuid.uuid4())

        url = None if dep_uuid else req.url._url

        task_request = TaskRequest(url=url, path_param=param, body=body)

        self.db.add(TaskModel(
            uuid = task_uuid,
            post_time = datetime.now().astimezone(),
            run_time = None,
            user_id = user.id,
            status = status,
            dependence_uuid = dep_uuid,
            resource = self.resource,
            object = self.object,
            method = self.method,
            request = task_request.model_dump_json(),
            message = "Task has been queued"
        ))
        self.db.commit()

        self.model = self.db.query(TaskModel).filter(TaskModel.uuid==task_uuid).one()
       

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
            if task.dependence_uuid is None:
                raise Exception()
            depends_task:TaskModel = db.query(TaskModel)\
                .filter(TaskModel.uuid==task.dependence_uuid)\
                .with_lockmode('update').one()
        except FileNotFoundError:
            task.status = "error"
            task.message = "not found depended task"
            db.merge(task)
            db.commit()
            logger.error(f"depended task notfund {task.uuid} => {task.dependence_uuid}")
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