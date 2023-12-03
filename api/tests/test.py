#!/usr/bin/env python3
import sys

from common import put_list
from test_node import post_nodes, post_nodes_key, delete_nodes, patch_nodes_vxlan
from test_storage import post_storage, delete_storage
from test_vms import post_vm, delete_vm, poweron_vm, poweroff_vm, post_vm_copy, patch_vm_cdrom, patch_vm_network, vms_project
from test_network import post_network, delete_network, post_network_ovs, delete_network_ovs, create_network_provider
from test_setup import api_auth_validate, api_users_me
from test_user import create_user, delete_user
from test_project import create_project, delete_project
from test_image import test_image_download
from test_flavor import create_flavors, delete_flavors

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