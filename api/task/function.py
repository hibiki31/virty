import time
import uuid
import copy
import subprocess

from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.orm import Session

from task.models import TaskModel
from auth.router import CurrentUser, get_current_user
from mixin.log import setup_logger
from settings import APP_ROOT

from worker import do_task


logger = setup_logger(__name__)


class PostTask():
    def __init__(self, db:Session, user:CurrentUser, model: BaseModel):
        self.db = db
        self.user = user
        self.model = model
    
    def commit(self, resource, object, method, bg=None, status="init", dependence_uuid=None):
        uuid_str = str(uuid.uuid4())
        time = datetime.now()
        user_id = self.user.id

        if self.model == None:
            self.model = BaseModel()

        row = TaskModel(
            uuid = uuid_str,
            post_time = time,
            run_time = 0,
            user_id = user_id,
            status = status,
            dependence_uuid = dependence_uuid,
            resource = resource,
            object = object,
            method = method,
            request = self.model.json(),
            message = "queing task"
        )

        res = copy.copy(row)

        self.db.add(row)
        self.db.commit()

        if bg:
            bg.add_task(do_task,db=self.db)
        
        return res