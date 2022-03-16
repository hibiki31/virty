import random
import string

from ast import Raise
from distutils import core
from doctest import FAIL_FAST
import re
from urllib import request
from pydantic import create_model_from_namedtuple
from sqlalchemy import func, nullsfirst
from sqlalchemy.orm import Session
from time import time
from network.models import NetworkModel, NetworkPoolModel, NetworkPortgroupModel, associations_networks, associations_networks_pools

from ticket.models import IssuanceModel, TicketModel

from .models import *
from .schemas import *

from task.models import TaskModel
from node.models import NodeModel
from user.models import UserModel
from storage.models import AssociationStoragePool, StorageModel, ImageModel, StorageMetadataModel, StoragePoolModel
from mixin.log import setup_logger

from module import virtlib
from module import xmllib
from module import sshlib
from module import cloudinitlib
from module.ansiblelib import AnsibleManager


logger = setup_logger(__name__)


def post_project(db: Session, model: TaskModel):
    request = PostProject(**model.request)
    letters = string.ascii_lowercase + "0123456789"
    result_str = ''.join(random.choice(letters) for i in range(8))

    project = ProjectModel(
        id=result_str,
        name=request.project_name
    )

    for user in request.user_ids:
        project.users.append(db.query(UserModel).filter(UserModel.id==user).one())

    
    

    db.add(project)
    db.commit()

    return model