import httpx
import json
from pprint import pprint
import time
import datetime
import sys

from common import BASE_URL, TEST_ENV, HEADERS, print_resp, wait_tasks


def delete_vm():
    resp = httpx.request(method="get", url=f'{BASE_URL}/api/vms', params={"admin":True},headers=HEADERS)
    print_resp(resp=resp)

    for vm in resp.json():
        if vm["name"] == "testcode-vm":
            request_data = {"uuid": vm["uuid"]}
            resp = httpx.request(method="delete",url=f'{BASE_URL}/api/tasks/vms', headers=HEADERS, json=request_data)
            print_resp(resp=resp)
            wait_tasks(resp)


def poweron_vm():
    resp = httpx.request(method="get", url=f'{BASE_URL}/api/vms', params={"admin":True},headers=HEADERS)
    print_resp(resp=resp)

    for vm in resp.json():
        if vm["name"] == "testcode-vm":
            request_data = {"status": "on"}
            resp = httpx.request(method="patch",url=f'{BASE_URL}/api/tasks/vms/{vm["uuid"]}/power', headers=HEADERS, json=request_data)
            print_resp(resp=resp)
            wait_tasks(resp)



def poweroff_vm():
    resp = httpx.request(method="get", url=f'{BASE_URL}/api/vms', params={"admin":True},headers=HEADERS)
    print_resp(resp=resp)

    for vm in resp.json():
        if vm["name"] == "testcode-vm":
            request_data = {"status": "off"}
            resp = httpx.request(method="patch",url=f'{BASE_URL}/api/tasks/vms/{vm["uuid"]}/power', headers=HEADERS, json=request_data)
            print_resp(resp=resp)
            wait_tasks(resp)



def post_vm():
    resp = httpx.request(method="get", url=f'{BASE_URL}/api/storages', headers=HEADERS, params={"name": "test-img", "nodeName": "test-node"})
    print_resp(resp=resp)

    savePoolUuid = resp.json()[0]["uuid"]

    request_data = {
        "type":"manual",
        "name":"testcode-vm",
        "nodeName":"test-node",
        "memoryMegaByte":"8192",
        "cpu":"4",
        "disks":[
            {
                "id":1,
                "type":"empty",
                "savePoolUuid":savePoolUuid,
                "sizeGigaByte":64
            }
        ],
        "interface":[
            {
                "type":"network",
                "networkName":"ovs-network",
                "port": "ovs-vlan144"
            }
        ]
    }
    resp = httpx.request(method="post",url=f'{BASE_URL}/api/tasks/vms', headers=HEADERS, json=request_data)
    print_resp(resp=resp)
    wait_tasks(resp)