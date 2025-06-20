import subprocess
import uuid
from time import time, sleep
from sqlalchemy import desc

from settings import APP_ROOT
from mixin.log import setup_logger
from mixin.database import SessionLocal

from task.models import TaskModel
from task.schemas import Task
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


def task_swicher(model:Task, db:SessionLocal):
    if model.resource == "vm":
        if model.object == "list":
            if model.method == "update":
                res = update_vm_list(db=db, model=model)
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
        elif model.object == "role":
            if model.method == "change":
                res = patch_node_role(db=db, model=model)
    
    elif model.resource == "project":
        if model.object == "root":
            if model.method == "post":
                res = post_project(db=db, model=model)

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


def do_task(mode="init", db = SessionLocal()):
    logger.debug(f"looking for a {mode} task")

    # 指定された状態のタスクを取得
    tasks = db.query(TaskModel)\
        .filter(TaskModel.status==mode)\
        .order_by(TaskModel.post_time)\
        .with_lockmode('update').all()
    
    if tasks == [] and mode == "wait":
        # 待機中のタスクもないため終了
        logger.info("task not found worker exit")
        return
    elif tasks == [] and mode == "init":
        # 待機中のタスク実施へ
        do_task(db=db, mode="wait")
        return

    # 新規タスク処理
    if mode == "init":
        task:TaskModel = tasks[0]
        logger.info(f'find tasks: {task.resource}.{task.object}.{task.method} {task.uuid}')
        exec_task(db=db, task=task)
        do_task(db=db)
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
            do_task(db=db)
        
    do_task(db=db)


def exec_task(db, task):
    logger.info(f'start tasks: {task.resource}.{task.object}.{task.method} {task.uuid}')
    task.status = "start"
    db.merge(task)
    db.commit()


    # Model to Schemas
    task:Task = Task().from_orm(task)

    
    start_time = time()

    try:
        res = task_swicher(model=task, db=db)
        msg = str(res.message)
        end_time = time()
        task.run_time = end_time - start_time
    except Exception as e:
        db.rollback()
        logger.error(e, exc_info=True)
        task.status = "error"
        task.message = str(e)
    else:
        logger.info(f'task finished: {task.resource}.{task.object}.{task.method} {task.uuid} {task.run_time}s')
        task.status = "finish"
        task.message = msg    
    logger.debug(task)
    # Schemas to Model
    db.merge(TaskModel(**task.dict()))
    db.commit()
    


if __name__ == "__main__":
    do_task()