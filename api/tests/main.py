#!/usr/bin/env python3
import sys

from common import put_list
from test_flavor import create_flavors, delete_flavors
from test_image import test_image_download
from test_network import (
    delete_network,
    delete_network_ovs,
    post_network,
    post_network_ovs,
)
from test_node import delete_nodes, post_nodes, post_nodes_key
from test_project import create_project, delete_project
from test_setup import api_auth_validate, api_users_me
from test_storage import delete_storage, post_storage
from test_user import create_user, delete_user
from test_vms import (
    delete_vm,
    patch_vm_cdrom,
    patch_vm_network,
    post_vm,
    post_vm_copy,
    poweroff_vm,
    poweron_vm,
    vms_project,
)

args = sys.argv


def main():
    scenario_test()

def scenario_test():
    # Setup
    api_auth_validate()
    api_users_me()
    
    # User
    delete_user()
    create_user()
    
    # Projects
    delete_project()
    create_project()
    
    # Node
    post_nodes_key()
    delete_nodes()
    post_nodes()
    # patch_nodes_vxlan()
    # create_network_provider()
    
    # Storage
    put_list()
    delete_storage()
    post_storage()
    
    # Image
    test_image_download()

    delete_flavors()
    create_flavors()

    # Network
    put_list()
    delete_network()
    post_network()
    delete_network_ovs()
    post_network_ovs()
    
    # VM
    put_list()
    delete_vm()
    
    post_vm()
    poweron_vm()
    poweroff_vm()
    
    delete_vm()
    post_vm_copy()
    patch_vm_cdrom()
    patch_vm_network() # brが存在しなくなるのでpoweronは効かない
    vms_project()
    # poweron_vm()
    

if __name__ == "__main__":
    main()