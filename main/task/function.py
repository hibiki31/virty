import uuid
from datetime import datetime

from fastapi import BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from task.models import TaskModel
from auth.router import CurrentUser, get_current_user
from mixin.log import setup_logger

import time

logger = setup_logger(__name__)


def post_task(db, current_user, request_model, resource, object, method):
    logger.info(resource)

    uuid_str = str(uuid.uuid4())
    time = datetime.now()
    user_id = current_user.user_id

    if request_model:
        model = request_model
    else:
        model = BaseModel()

    row = TaskModel(
        uuid = uuid_str,
        post_time = time,
        run_time = 0,
        user_id = user_id,
        status = "start",
        resource = resource,
        object = object,
        method = method,
        request = model.json(),
        message = "queing task"
    )

    res = TaskModel(
        uuid = uuid_str,
        post_time = time,
        run_time = 0,
        user_id = user_id,
        status = "start",
        resource = resource,
        object = object,
        method = method,
        request = model,
        message = "queing task"
    )

    db.add(row)
    db.commit()
    return res


def run_background_task(base_func, db: Session, cu: CurrentUser, model: TaskModel):
    try:
        base_func(db=db, cu=cu ,model=model)
    except Exception as e:
        print(e)
    
    logger.info("タスク"+model.uuid+"が終了しました")

    # query = db.query(Staff).filter(Staff.staff_name == "Yamada Taro")
    # staff_update = query
    # staff_update.staff_age = staff_update.staff_age + 100
    # session.commit()


def add_background_task(resource: str, object: str, method: str):
    def deco(func):
        def wrapper(bg: BackgroundTasks, db: Session, cu: CurrentUser, model: BaseModel):
            # タスクの詳細をデータベースに登録
            task_model = post_task(db=db, current_user=cu, request_model=model, resource=resource, object=object, method=method)
            # 例外処理を挟んでバックグラウンドで実行
            bg.add_task(func=run_background_task,base_func=func, db=db, cu=cu ,model=task_model)
            return task_model
        return wrapper
    return deco