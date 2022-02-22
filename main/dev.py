from urllib import request
from storage.tasks import update_storage_list
from network.tasks import update_network_list
from node.tasks import patch_node_role
from domain.tasks import *
from domain.schemas import *
from mixin.database import SessionLocal
from task.models import TaskModel
from module.ansiblelib import AnsibleManager

from module import sshlib


from module import cloudinitlib
def cloud_init_test():
    manager = cloudinitlib.CloudInitManager("aaaaa","hostnameeeeeee")
    manager.make_iso()



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

def dev_patch_node_role():
    db = SessionLocal()
    model = TaskModel(request={
        "node_name": "shiori",
        "role_name": "libvirt"
    })
    patch_node_role(db=db, model=model)

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

    play_source = dict(
        name = "Ansible Play",
        hosts = 'all',
        gather_facts = 'no',
        tasks = [
            dict(
                synchronize = dict(
                    src = "/workspaces/virty/main/data/cloud-init/aaaaa/init.iso",
                    dest = "/",
                    compress = "no"
                ),
                become = "yes"
            )
        ]
    )

    manager = AnsibleManager(user="akane", domain="192.168.144.31")
    #manager.run_playbook(play_source)
    manager.file_copy_to_node(src="/workspaces/virty/main/data/cloud-init/aaaaa/init.iso",dest="aaa.iso")
    

if __name__ == "__main__":
    dev_patch_node_role()