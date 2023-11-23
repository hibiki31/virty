#!/usr/bin/env python3
import httpx
import json
from pprint import pprint
import time
import datetime
import sys

from common import BASE_URL, HEADERS, print_resp, wait_tasks, print_test_start, print_test_end
from test_node import post_nodes, post_nodes_key, delete_nodes, patch_nodes_vxlan
from test_storage import post_storage, delete_storage
from test_vms import post_vm, delete_vm, poweron_vm, poweroff_vm, post_vm_copy, patch_vm_cdrom, patch_vm_network
from test_network import post_network, delete_network, post_network_ovs, delete_network_ovs, create_network_provider


args = sys.argv


def main():
    # Setup
    api_auth_validate()
    api_users_me()
    
    # Node
    if False:
        post_nodes_key()
        delete_nodes()
        post_nodes()
        # patch_nodes_vxlan()
        # create_network_provider()
    
    # Storage
    if False:
        put_list()
        delete_storage()
        post_storage()

    if False:
    # Network
        put_list()
        delete_network()
        post_network()
        # delete_network_ovs()
        # post_network_ovs()
    
    # VM
    if True:
        put_list()
        delete_vm()
        # post_vm()
        # poweron_vm()
        # poweroff_vm()
        # delete_vm()
        # post_vm_copy()
        # patch_vm_cdrom()
        # patch_vm_network()


def put_list():
    resp = httpx.put(f'{BASE_URL}/api/tasks/images',headers=HEADERS)
    print_resp(resp=resp)
    wait_tasks(resp)
    
    resp = httpx.put(f'{BASE_URL}/api/tasks/vms',headers=HEADERS)
    print_resp(resp=resp)
    wait_tasks(resp)

    resp = httpx.put(f'{BASE_URL}/api/tasks/networks',headers=HEADERS)
    print_resp(resp=resp)
    wait_tasks(resp)


def api_auth_validate():
    resp = httpx.get(f'{BASE_URL}/api/auth/validate',headers=HEADERS)
    print_resp(resp=resp)


def api_users_me():
    resp = httpx.get(f'{BASE_URL}/api/users/me',headers=HEADERS)
    print_resp(resp=resp)


if __name__ == "__main__":
    main()