import subprocess
import uuid
from time import time, sleep
from sqlalchemy import desc

from settings import APP_ROOT
from mixin.log import setup_logger
from mixin.database import SessionLocal

from task.models import TaskModel
from task.schemas import TaskSelect
from domain.tasks import *
from node.tasks import *
from storage.tasks import *
from network.tasks import *


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


def task_swicher(model:TaskSelect, db:SessionLocal):
    if model.resource == "vm":
        if model.object == "list":
            if model.method == "update":
                res = update_domain_list(db=db, model=model)
        elif model.object == "base":
            if model.method == "add":
                res = add_domain_base(db=db, model=model)
            elif model.method == "delete":
                res = delete_domain_base(db=db, model=model)
            elif model.method == "change":
                res = change_domain_base(db=db, model=model)
        elif model.object == "network":
            if model.method == "change":
                res = change_domain_network(db=db, model=model)

    elif model.resource == "node":
        if model.object == "base":
            if model.method == "add":
                res = post_node_base(db=db, model=model)

    elif model.resource == "storage":
        if model.object == "list":
            if model.method == "update":
                res = update_storage_list(db=db, model=model)
        elif model.object == "base":
            if model.method == "add":
                res = add_storage_base(db=db, model=model)
            elif model.method == "delete":
                res = delete_storage_base(db=db, model=model)
    
    elif model.resource == "network":
        if model.object == "list":
            if model.method == "update":
                res = update_network_list(db=db, model=model)
        elif model.object == "base":
            if model.method == "add":
                res = add_network_base(db=db, model=model)
            elif model.method == "delete":
                res = delete_network_base(db=db, model=model)
        elif model.object == "ovs":
            if model.method == "add":
                res = add_network_ovs(db=db, model=model)
            elif model.method == "delete":
                res = delete_network_ovs(db=db, model=model)

    try:
        res
    except:
        raise Exception("タスクが見つかりませんでした")

    return res


def endless_eight():
    
    
    db = SessionLocal()
    while True:
        query = db.query(TaskModel)
        query = query.filter(TaskModel.status=="init")
        query = query.order_by(desc(TaskModel.post_time))
        tasks = query.all()
        if tasks == []:
            sleep(3)
            continue

        # 開始処理
        for task in tasks:
            task:TaskModel
            logger.info(f'タスク開始: {task.resource}.{task.object}.{task.method} {task.uuid}')
            task.status = "start"
            db.merge(task)
            db.commit()

            # Model to Schemas
            task:TaskSelect = TaskSelect().from_orm(task)

            
            start_time = time()

            try:
                task_swicher(model=task, db=db)
            except Exception as e:
                logger.error(e, exc_info=True)
                task.status = "error"
                task.message = str(e)
            else:
                task.status = "finish"
                task.message = "finish"

            end_time = time()
            task.run_time = end_time - start_time

            logger.info(f'タスク終了: {task.resource}.{task.object}.{task.method} {task.uuid} {task.run_time}s')

            # Schemas to Model
            db.merge(TaskModel(**task.dict()))
            db.commit()

def do_task(mode="init"):
    logger.info(f"looking for a {mode} task")

    db = SessionLocal()
    tasks = db.query(TaskModel)\
        .filter(TaskModel.status==mode)\
        .order_by(desc(TaskModel.post_time))\
        .with_lockmode('update').all()
    
    if tasks == [] and mode == "wait":
        logger.info("worker exit")
        return
    elif tasks == [] and mode == "init":
        do_task(mode="wait")
        return

    # 開始処理
    task:TaskModel = tasks[0]

    # 依存関係処理
    depends_tasks = db.query(TaskModel)\
        .filter(TaskModel.status!="finish")\
        .filter(TaskModel.uuid==task.dependence_uuid)\
        .with_lockmode('update').all()
    if depends_tasks != []:
        logger.info("find depend task, change wait task and exit")
        task.status = "wait"
        db.merge(task)
        db.commit()
        return

    logger.info(f'start tasks: {task.resource}.{task.object}.{task.method} {task.uuid}')
    task.status = "start"
    db.merge(task)
    db.commit()


    # Model to Schemas
    task:TaskSelect = TaskSelect().from_orm(task)

    
    start_time = time()

    try:
        task_swicher(model=task, db=db)
    except Exception as e:
        logger.error(e, exc_info=True)
        task.status = "error"
        task.message = str(e)
    else:
        task.status = "finish"
        task.message = "finish"

    end_time = time()
    task.run_time = end_time - start_time

    logger.info(f'task finished: {task.resource}.{task.object}.{task.method} {task.uuid} {task.run_time}s')

    # Schemas to Model
    db.merge(TaskModel(**task.dict()))
    db.commit()

    do_task()
    


if __name__ == "__main__":
    do_task()