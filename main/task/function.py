import time
import uuid

from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.orm import Session

from task.models import TaskModel
from auth.router import CurrentUser, get_current_user
from mixin.log import setup_logger


logger = setup_logger(__name__)


class PostTask():
    db = None
    user = None
    model = None
    task_model = TaskModel()

    def __init__(self, db:Session, user:CurrentUser, model: BaseModel):
        self.db = db
        self.user = user
        self.model = model
    
    def commit(self, resource, object, method):
        uuid_str = str(uuid.uuid4())
        time = datetime.now()
        user_id = self.user.user_id

        if self.model == None:
            self.model = BaseModel()

        row = TaskModel(
            uuid = uuid_str,
            post_time = time,
            run_time = 0,
            user_id = user_id,
            status = "start",
            resource = resource,
            object = object,
            method = method,
            request = self.model.json(),
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
            request = self.model,
            message = "queing task"
        )

        self.db.add(row)
        self.db.commit()
        
        return res


