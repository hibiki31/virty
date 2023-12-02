import subprocess
import uuid
import traceback
from time import time, sleep
from sqlalchemy import desc, or_

from settings import APP_ROOT
from mixin.log import setup_logger
from mixin.database import SessionLocal

from task.schemas import Task
from task.functions import TaskBase
from node.tasks import *
from storage.tasks import *
from network.tasks import *

from task.models import TaskModel
from user.models import UserModel
from project.models import ProjectModel

from functools import update_wrapper

from domain.tasks import worker_task as domain_tasks
from node.tasks import worker_task as node_tasks
from storage.tasks import worker_task as storage_tasks
from network.tasks import worker_task as network_tasks
from project.tasks import worker_task as project_tasks
from images.tasks import worker_task as image_tasks

logger = setup_logger(__name__)







def main():
    tasks = TaskBase()
    tasks.include_task(domain_tasks)
    tasks.include_task(node_tasks)
    tasks.include_task(storage_tasks)
    tasks.include_task(network_tasks)
    tasks.include_task(project_tasks)
    tasks.include_task(image_tasks)

    init_scheduler()

    while True:
        run_scheduler(tasks)




def init_scheduler():
    db = SessionLocal()

    lost_tasks = db.query(TaskModel).filter(TaskModel.status!="finish", TaskModel.status!="lost", TaskModel.status!="error")
    lost_tasks.update({
        TaskModel.status:"lost",
        TaskModel.message:"Worker restarted and did not run"
    })

    lost_tasks = lost_tasks.all()

    if len(lost_tasks) != 0:
        logger.error(f'{len(lost_tasks)} task was not executed')
    
    db.commit()


def run_scheduler(task_manager: TaskBase):
    db = task_manager.db

    tasks = db.query(
        TaskModel
    ).filter(or_(
        TaskModel.status=="init",
        TaskModel.status=="wait"
    )).order_by(TaskModel.post_time).with_for_update().all()

    for task in tasks:
        task:TaskModel

        # initだったら実行
        if task.status == "init":
            exec_task(db=task_manager.db, task=task, tasks=task_manager)
            continue
        
        # 以下はWaitタスクの処理
        depends_task:TaskModel = db.query(TaskModel).filter(
            TaskModel.uuid==task.dependence_uuid
            ).with_lockmode('update').one()

        if depends_task.status == "error" or depends_task.status == "lost":
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
            logger.info(f"init depended task {task.uuid} => {task.dependence_uuid}")
            exec_task(db=task_manager.db, task=task, tasks=task_manager)
    sleep(3)




def exec_task(db, task: TaskModel, tasks):
    logger.info(f'start {task.uuid} {task.method}.{task.resource}.{task.object}')
    task.status = "start"
    task.start_time = datetime.now().astimezone()
    db.commit()

    start_time = time()
    
    try:
        tasks.run(key=f"{task.method}.{task.resource}.{task.object}", task_model=task)
        task.status = "finish"
    except Exception as e:
        db.rollback()
        logger.error(e, exc_info=True)
        task.status = "error"
        task.message = str(e)
        task.write_log(traceback.format_exc())

    task.update_time = datetime.now().astimezone()
    task.run_time = time() - start_time
    db.commit()

    

if __name__ == "__main__":
    main()