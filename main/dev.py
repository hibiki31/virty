from storage.tasks import update_storage_list
from network.tasks import update_network_list
from domain.tasks import *
from domain.schemas import *
from mixin.database import SessionLocal
from task.models import TaskModel
from module.ansiblelib import ansible_runner

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


import json
def ansible_test():
    play_source =  dict(
        name = "Ansible Play",
        hosts = 'all',
        gather_facts = 'no',
        tasks = [
            dict(action=dict(module='shell', args='lssss -l'), register='shell_out')
        ]
    )

    play_source = dict(
        name = "Ansible Play",
        hosts = 'all',
        gather_facts = 'no',
        tasks = [
            dict(
                apt = dict(
                    update_cache = "yes"
                ),
                become = "yes"
            )
        ]
    )

    result = ansible_runner(play_dict=play_source, host="akane@192.168.144.31")
    print(json.dumps(result, indent=4))
    

if __name__ == "__main__":
    ansible_test()