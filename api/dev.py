from pprint import pprint
from random import random, randint
import libvirt

from urllib import request
from module.virtlib import VirtManager
from storage.tasks import update_storage_list
from network.tasks import update_network_list
from node.tasks import patch_node_role
from domain.tasks import *
from domain.schemas import *
from mixin.database import SessionLocal
from task.models import TaskModel
from module.ansiblelib import AnsibleManager
from module.ovslib import OVSManager
from user.models import *
from project.models import *

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

def dev_libvirt():
    db = SessionLocal()
    nodes = db.query(NodeModel).all()
    for node in nodes:
        con = VirtManager(node)
        # con: libvirt.virConnect
        pprint(dir(con.node))
        for dom in con.node.listAllDomains():
            dom: libvirt.virDomain
            # dom.getHostname()
            "https://libvirt.org/html/libvirt-libvirt-domain.html#virDomainMetadataType"
            dom.setMetadata(key="virty", metadata="<data user='akane'/>", type=2, uri="aaaa")
            # dom.virDomainGetMetadata()
            # pprint(dom.XMLDesc())
            # pprint(dom.rename)

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


def dev_ovs():
    db = SessionLocal()
    manager = OVSManager(domain=db.query(NodeModel).first().domain)
    for i in manager.ovs_list_br():
        print(i)
        print(manager.ovs_list_port(i))
    # manager.ovs_add_br("br-test")
    # manager.ovs_add_vxlan(bridge="br-test", remote="10.254.4.12", key="test")


def project():
    pass

if __name__ == "__main__":
    dev_ovs()