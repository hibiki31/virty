#!/usr/bin/env python3
import sys

from common import put_list
from test_node import post_nodes, post_nodes_key, delete_nodes, patch_nodes_vxlan
from test_storage import post_storage, delete_storage
from test_vms import post_vm, delete_vm, poweron_vm, poweroff_vm, post_vm_copy, patch_vm_cdrom, patch_vm_network
from test_network import post_network, delete_network, post_network_ovs, delete_network_ovs, create_network_provider
from test_setup import api_auth_validate, api_users_me
from test_user import create_user, delete_user
from test_project import create_project, delete_project


args = sys.argv


def main():
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
    # post_nodes_key()
    # delete_nodes()
    # post_nodes()
    # patch_nodes_vxlan()
    # create_network_provider()
    
    # Storage
    # put_list()
    # delete_storage()
    # post_storage()

    # Network
    # put_list()
    # delete_network()
    # post_network()
    # delete_network_ovs()
    # post_network_ovs()
    
    # VM
    # put_list()
    # delete_vm()
    # post_vm()
    # poweron_vm()
    # poweroff_vm()
    # delete_vm()
    # post_vm_copy()
    # patch_vm_cdrom()
    # patch_vm_network()


if __name__ == "__main__":
    main()