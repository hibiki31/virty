import uuid
from task.models import TaskModel
from datetime import datetime

from mixin.log import setup_logger

logger = setup_logger(__name__)

def post_task(db, current_user, request_model, resource, object, method):
    logger.info(resource)

    if request_model:
        json_str = request_model.json()
    else:
        json_str = ""

    task = TaskModel(
        uuid = str(uuid.uuid4()),
        post_time = datetime.now(),
        run_time = 0,
        user_id = current_user.user_id,
        status = "start",
        resource = resource,
        object = object,
        method = method,
        json_str = json_str,
        message = "queing task"
    )
    
    res = TaskModel(
        uuid = str(uuid.uuid4()),
        post_time = datetime.now(),
        run_time = 0,
        user_id = current_user.user_id,
        status = "start",
        resource = resource,
        object = object,
        method = method,
        json_str = json_str,
        message = "queing task"
    )

    db.add(task)
    db.commit()
    return res