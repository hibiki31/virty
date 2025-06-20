import multiprocessing as mp
import os
import traceback
from datetime import datetime
from time import sleep, time

from sqlalchemy import or_

from domain.tasks import worker_task as domain_tasks
from images.tasks import worker_task as image_tasks
from mixin.database import SessionLocal
from mixin.log import setup_logger
from models import TaskModel
from network.tasks import worker_task as network_tasks
from node.tasks import worker_task as node_tasks
from project.tasks import worker_task as project_tasks
from settings import DATA_ROOT
from storage.tasks import worker_task as storage_tasks
from task.functions import TaskBase

logger = setup_logger(__name__)


def main():
    # Ansible runnerがforkしてSessionを破壊しないようにする
    mp.set_start_method("spawn", force=True)
    
    ansible_private_path = os.path.join(DATA_ROOT, "ansible")
    os.makedirs(ansible_private_path, exist_ok=True)
    
    task_manager = TaskBase()
    task_manager.include_task(domain_tasks)
    task_manager.include_task(node_tasks)
    task_manager.include_task(storage_tasks)
    task_manager.include_task(network_tasks)
    task_manager.include_task(project_tasks)
    task_manager.include_task(image_tasks)

    init_scheduler()

    while True:
        run_scheduler(task_manager)
        # logger.debug("run_scheduler loop...")
        # print(Engine.pool.status())
        sleep(0.1)


def init_scheduler():
    with SessionLocal() as db:
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
    init_tasks_uuid = []
    
    with SessionLocal.begin() as db:
        tasks = db.query(
            TaskModel
        ).filter(or_(
            TaskModel.status=="init",
            TaskModel.status=="wait"
        )).order_by(TaskModel.post_time).with_for_update().all()

        for task in tasks:
            # initだったら実行
            if task.status == "init":
                init_tasks_uuid.append(task.uuid)
                continue
            
            # 以下はWaitタスクの処理 ここに入るときはwaitのタスクの場合だからoneでも大丈夫？
            depends_task:TaskModel = db.query(TaskModel).filter(
                TaskModel.uuid==task.dependence_uuid
                ).with_for_update().one()

            if depends_task.status == "error" or depends_task.status == "lost":
                task.status = "error"
                task.message = "depended task faile"
                logger.error(f"depended task faile {task.uuid} => {task.dependence_uuid}")
            

            # 親タスクが実行中の場合待機
            elif depends_task.status != "finish":
                logger.info(f"wait depended task. {task.uuid} => {task.dependence_uuid}")
            
            # 実行可能なタスクは初期化
            elif depends_task.status == "finish" and task.status == "wait":
                task.status = "init"
                logger.info(f"init depended task {task.uuid} => {task.dependence_uuid}")
        db.commit()
    
    for i in init_tasks_uuid:
        exec_task(task_manager=task_manager, task_uuid=i)


def exec_task(task_manager: TaskBase, task_uuid: str):
    with SessionLocal.begin() as db:
        task = db.query(TaskModel).filter(TaskModel.uuid==task_uuid).one()
        task.status = "start"
        task.start_time = datetime.now().astimezone()
        
        task_key = f"{task.method}.{task.resource}.{task.object}"
        
        db.commit()
    
    # 測定用は別変数にした
    start_time = time()

    try:
        logger.info(f'Task start: {task_uuid} {task_key}')
        task_manager.run(key=task_key, task_uuid=task_uuid)
        logger.info(f"Task finish: {task_uuid} {task_key}")
        
        with SessionLocal.begin() as db:
            task = db.query(TaskModel).filter(TaskModel.uuid==task_uuid).one()
            task.status = "finish"
            # 共通
            task.update_time = datetime.now().astimezone()
            task.run_time = time() - start_time
            db.commit()
            
    except Exception as e:
        with SessionLocal.begin() as db:
            task = db.query(TaskModel).filter(TaskModel.uuid==task_uuid).one()
            task.status = "error"
            task.message = str(e)
            logger.error(e, exc_info=True)
            task.write_log(traceback.format_exc())

            # 共通
            task.update_time = datetime.now().astimezone()
            task.run_time = time() - start_time
            db.commit()

    

if __name__ == "__main__":
    main()