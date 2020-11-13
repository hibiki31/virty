import time
import uuid

from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.orm import Session

from task.models import TaskModel
from auth.router import CurrentUser, get_current_user
from mixin.log import setup_logger


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