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
from storage.tasks import worker_task as storage_tasks
from task.functions import TaskBase

logger = setup_logger(__name__)


def main():
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
        sleep(3)


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
    with SessionLocal() as db:
        tasks = db.query(
            TaskModel
        ).filter(or_(
            TaskModel.status=="init",
            TaskModel.status=="wait"
        )).order_by(TaskModel.post_time).with_for_update(skip_locked=True).all()

        for task in tasks:
            # initだったら実行
            if task.status == "init":
                exec_task(task=task, task_manager=task_manager, db=db)
                break
            
            # 以下はWaitタスクの処理
            depends_task:TaskModel = db.query(TaskModel).filter(
                TaskModel.uuid==task.dependence_uuid
                ).with_for_update().one()

            if depends_task.status == "error" or depends_task.status == "lost":
                task.status = "error"
                task.message = "depended task faile"
                db.commit()
                logger.error(f"depended task faile {task.uuid} => {task.dependence_uuid}")
                break
            

            # 親タスクが実行中の場合待機
            elif depends_task.status != "finish":
                logger.info(f"wait depended task. {task.uuid} => {task.dependence_uuid}")
                break
            
            # 実行可能なタスクは初期化
            elif depends_task.status == "finish" and task.status == "wait":
                task.status = "init"
                db.commit()
                logger.info(f"init depended task {task.uuid} => {task.dependence_uuid}")
                break
        




def exec_task(task, task_manager:TaskBase,db):

    logger.info(f'start {task.uuid} {task.method}.{task.resource}.{task.object}')
    task.status = "start"
    task.start_time = datetime.now().astimezone()

    db.commit()
    start_time = time()

    try:
        task_manager.run(key=f"{task.method}.{task.resource}.{task.object}", task_model=task, db=db)
        task.status = "finish"
    except Exception as e:
        task.status = "error"
        task.message = str(e)
        logger.error(e, exc_info=True)
        task.write_log(traceback.format_exc())
    
    task.update_time = datetime.now().astimezone()
    task.run_time = time() - start_time
    db.commit()

        

    

if __name__ == "__main__":
    main()