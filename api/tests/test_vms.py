import httpx
import json
from pprint import pprint
import time
import datetime
import sys

from common import BASE_URL, env, HEADERS, print_resp, wait_tasks, tester


@tester
def delete_vm():
    resp = httpx.request(method="get", url=f'{BASE_URL}/api/vms', params={"admin":True}, headers=HEADERS)
    print_resp(resp=resp)

    for vm in resp.json()["data"]:
        if vm["name"] == "testcode-vm":
            resp = httpx.request(method="delete",url=f'{BASE_URL}/api/tasks/vms/{vm["uuid"]}', headers=HEADERS)
            print_resp(resp=resp)
            wait_tasks(resp)


@tester
def poweron_vm():
    resp = httpx.request(method="get", url=f'{BASE_URL}/api/vms', params={"admin":True},headers=HEADERS)
    print_resp(resp=resp)

    for vm in resp.json()["data"]:
        if vm["name"] == "testcode-vm":
            request_data = {"status": "on"}
            resp = httpx.request(method="patch",url=f'{BASE_URL}/api/tasks/vms/{vm["uuid"]}/power', headers=HEADERS, json=request_data)
            print_resp(resp=resp)
            wait_tasks(resp)


@tester
def poweroff_vm():
    resp = httpx.request(method="get", url=f'{BASE_URL}/api/vms', params={"admin":True},headers=HEADERS)
    print_resp(resp=resp)

    for vm in resp.json()["data"]:
        if vm["name"] == "testcode-vm":
            request_data = {"status": "off"}
            resp = httpx.request(method="patch",url=f'{BASE_URL}/api/tasks/vms/{vm["uuid"]}/power', headers=HEADERS, json=request_data)
            print_resp(resp=resp)
            wait_tasks(resp)


@tester
def post_vm():
    for node in httpx.get(url=f'{BASE_URL}/api/nodes', headers=HEADERS).json()["data"]:
        resp = httpx.request(method="get", url=f'{BASE_URL}/api/storages', headers=HEADERS, params={"name": "test-img", "nodeName": node["name"]})
        print_resp(resp=resp)

        savePoolUuid = resp.json()["data"][0]["uuid"]

        request_data = {
            "type":"manual",
            "name":"testcode-vm",
            "nodeName": node["name"],
            "memoryMegaByte":"8192",
            "cpu":"4",
            "disks":[
                {
                    "id":1,
                    "type":"empty",
                    "savePoolUuid": savePoolUuid,
                    "sizeGigaByte":64
                }
            ],
            "interface":[
                # {
                #     "type":"network",
                #     "networkUuid":env["network_uuid"],
                #     "port": env["port_1"]
                # }
            ]
        }
        resp = httpx.request(method="post",url=f'{BASE_URL}/api/tasks/vms', headers=HEADERS, json=request_data)
        print_resp(resp=resp)
        wait_tasks(resp)


@tester
def post_vm_copy():
    resp = httpx.request(method="get", url=f'{BASE_URL}/api/storages', headers=HEADERS, params={"name": "test-img", "nodeName": "test-node"})
    print_resp(resp=resp)
    savePoolUuid = resp.json()["data"][0]["uuid"]

    resp = httpx.request(method="get", url=f'{BASE_URL}/api/storages', headers=HEADERS, params={"name": "test-cloud", "nodeName": "test-node"})
    print_resp(resp=resp)
    sourcePoolUuid = resp.json()["data"][0]["uuid"]
    
    resp = httpx.request(method="get", url=f'{BASE_URL}/api/networks', headers=HEADERS, params={"name_like": "default", "node_name_like": "test-node"})
    print_resp(resp=resp)
    network_uuid = resp.json()["data"][0]["uuid"]
    
    userdata = f"""
#cloud-config
password: password
chpasswd: 
  expire: False
ssh_pwauth: True
ssh_authorized_keys:
  - { env["pub"] }
    """

    request_data = {
        "type":"manual",
        "name":"testcode-vm",
        "nodeName":"test-node",
        "memoryMegaByte":"8192",
        "cpu":"4",
        "disks":[
            {
                "id":1,
                "type":"copy",
                "savePoolUuid":savePoolUuid,
                "originalPoolUuid": sourcePoolUuid,
                "originalName": env["image_name"],
                "sizeGigaByte":64
            }
        ],
        "interface":[
            {
                "type":"network",
                "networkUuid":network_uuid
            }
        ],
        "cloudInit": {
            "hostname": "testcode-vm",
            "userData": userdata
        }
    }
    resp = httpx.request(method="post",url=f'{BASE_URL}/api/tasks/vms', headers=HEADERS, json=request_data)
    print_resp(resp=resp)
    wait_tasks(resp)


@tester
def patch_vm_cdrom():
    resp = httpx.request(method="get", url=f'{BASE_URL}/api/vms', params={"admin":True},headers=HEADERS)
    print_resp(resp=resp)

    for vm in resp.json()["data"]:
        if vm["name"] == "testcode-vm":
            resp = httpx.request(method="get", url=f'{BASE_URL}/api/images', headers=HEADERS, params={"name": env["iso_name"], "node_name": "test-node"})
            print_resp(resp=resp)
            image_path = resp.json()["data"][0]["path"]
            
            request_data = { "path": image_path, "target": "hda"}
            resp = httpx.request(method="patch",url=f'{BASE_URL}/api/tasks/vms/{vm["uuid"]}/cdrom', headers=HEADERS, json=request_data)
            print_resp(resp=resp)
            wait_tasks(resp)

    resp = httpx.request(method="get", url=f'{BASE_URL}/api/vms', params={"admin":True},headers=HEADERS)
    print_resp(resp=resp)

    for vm in resp.json()["data"]:
        if vm["name"] == "testcode-vm":
            request_data = { "path": None, "target": "hda"}
            resp = httpx.request(method="patch",url=f'{BASE_URL}/api/tasks/vms/{vm["uuid"]}/cdrom', headers=HEADERS, json=request_data)
            print_resp(resp=resp)
            wait_tasks(resp)
    
    resp = httpx.request(method="get", url=f'{BASE_URL}/api/vms', params={"admin":True},headers=HEADERS)
    print_resp(resp=resp)

    for vm in resp.json()["data"]:
        if vm["name"] == "testcode-vm":
            resp = httpx.request(method="get", url=f'{BASE_URL}/api/images', headers=HEADERS, params={"name": env["iso_name"], "node_name": "test-node"})
            print_resp(resp=resp)
            image_path = resp.json()["data"][0]["path"]
            
            request_data = { "path": image_path, "target": "hda"}
            resp = httpx.request(method="patch",url=f'{BASE_URL}/api/tasks/vms/{vm["uuid"]}/cdrom', headers=HEADERS, json=request_data)
            print_resp(resp=resp)
            wait_tasks(resp)


@tester
def patch_vm_network():
    resp = httpx.request(method="get", url=f'{BASE_URL}/api/vms', params={"admin":True},headers=HEADERS)
    print_resp(resp=resp)

    for vm in resp.json()["data"]:
        if not vm["name"] == "testcode-vm":
            continue
        resp = httpx.request(method="get", url=f'{BASE_URL}/api/networks', headers=HEADERS, params={"name_like": "test", "node_name_like": "test-node"})
        print_resp(resp=resp, debug=True)
        network_uuid = resp.json()["data"][0]["uuid"]
        request_data = { "mac": vm["interfaces"][0]["mac"], "networkUuid": network_uuid}
        resp = httpx.request(method="patch",url=f'{BASE_URL}/api/tasks/vms/{vm["uuid"]}/network', headers=HEADERS, json=request_data)
        print_resp(resp=resp)
        wait_tasks(resp)


@tester
def vms_project():
    resp = httpx.request(method="get", url=f'{BASE_URL}/api/vms', params={"admin":True},headers=HEADERS)
    print_resp(resp=resp)

    for vm in resp.json()["data"]:
        if vm["name"] == "testcode-vm":
            get_resp = httpx.get(url=f'{BASE_URL}/api/projects', params={"name": "test"},headers=HEADERS)
            print_resp(resp=get_resp)
            
            request_data = {"uuid": vm["uuid"], "projectId": get_resp.json()["data"][0]["id"]}
            resp = httpx.request(method="patch",url=f'{BASE_URL}/api/tasks/vms/project', headers=HEADERS, json=request_data)
            print_resp(resp=resp)
            wait_tasks(resp)