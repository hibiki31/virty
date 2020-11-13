import subprocess
from time import time, sleep
from sqlalchemy import desc

from mixin.settings import virty_root
from mixin.log import setup_logger
from mixin.database import SessionLocal

from task.models import TaskModel
from domain.tasks import update_domain_list


logger = setup_logger(__name__)


def lost_task_cheack():
    db = SessionLocal()

    lost_tasks = db.query(TaskModel).filter(TaskModel.status!="finish")
    lost_tasks.update({
        TaskModel.status:"lost",
        TaskModel.message:"Workerが再起動したので実行されませんでした"
    }, synchronize_session=False)

    lost_tasks = lost_tasks.all()

    if len(lost_tasks) != 0:
        logger.error(f'{len(lost_tasks)}件のタスクが実行されませんでした')
    
    db.commit()


def task_swicher(m:TaskModel, db:SessionLocal) -> TaskModel:
    res = None
    if m.resource == "vm":
        if m.object == "list":
            if m.method == "update":
                res = update_domain_list(db=db, model=m)
    if res == None:
        raise Exception("タスクが見つかりませんでした")
    return res


def endless_eight():
    logger.info("Worker起動")
    while True:
        db = SessionLocal()
        query = db.query(TaskModel)
        query = query.filter(TaskModel.status=="start")
        query = query.order_by(desc(TaskModel.post_time))
        task = query.all()
        if task == []:
            sleep(3)
            continue

        task:TaskModel = task[0]
        logger.info(f'タスク開始: {task.resource}.{task.object}.{task.method} {task.uuid}')
        
        start_time = time.time()

        try:
            task = task_swicher(task, db)
        except Exception as e:
            logger.error(e)
            task.status = "error"
            task.message = str(e)
        else:
            task.status = "finish"

        end_time = time.time()
        task.run_time = end_time - start_time

        logger.info(f'タスク終了: {task.resource}.{task.object}.{task.method} {task.uuid} {task.run_time}s')

        db.merge(task)
        db.commit()
        db.close()


if __name__ == "__main__":
    endless_eight()