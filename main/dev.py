from storage.tasks import update_storage_list
from network.tasks import update_network_list
from domain.tasks import *
from domain.schemas import *
from mixin.database import SessionLocal
from task.models import TaskModel

from module import sshlib


def dev_update_storage_list():
    db = SessionLocal()
    update_storage_list(db=db, model=TaskModel())

def dev_update_network_list():
    db = SessionLocal()
    update_network_list(db=db, model=TaskModel())

def dev_domain_define():
    db = SessionLocal()
    update_network_list(db=db, model=TaskModel())

def dev_ssh_copy():
    ssh_manager = sshlib.SSHManager(user="user", domain="192.168.0.1")
    ssh_manager.file_copy(from_path="",to_path="")
    

if __name__ == "__main__":
    dev_ssh_copy()