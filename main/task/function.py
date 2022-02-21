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


logger = setup_logger(__name__)


class PostTask():
    def __init__(self, db:Session, user:CurrentUser, model: BaseModel):
        self.db = db
        self.user = user
        self.model = model
    
    def commit(self, resource, object, method, status="init", dependence_uuid=None):
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

        # worker_pool.append(subprocess.Popen(["python3", APP_ROOT + "/worker.py", uuid_str]))
        
        return res

worker_pool = []

def worker_up():
    worker_pool.append(subprocess.Popen(["python3", APP_ROOT + "/worker.py"]))

def worker_down():
    for w in worker_pool:
        w.terminate()
