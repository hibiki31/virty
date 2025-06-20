

from tests.conftest import wait_tasks
from tests.fixtures.vm import create_vm, delete_vm


def test_delete_vm(env, client, created_vm):
    delete_vm(env, client)


def test_create_vm(env, client, deleted_vm):
    create_vm(env, client)

def test_change_poewr_vm(env, client, created_vm):
    res_vms = client.get('/api/vms', params={"admin":True})

    for vm in res_vms.json()["data"]:
        for env_vm in env.vms:
            if env_vm.name in vm["name"]:
                assert vm["status"] in [5, 1]
                if vm["status"] == 5:#off
                    res = client.patch(f'/api/tasks/vms/{vm["uuid"]}/power', json={"status": "on"})
                    assert wait_tasks(res, client) == "finish"
                    res = client.patch(f'/api/tasks/vms/{vm["uuid"]}/power', json={"status": "off"})
                    assert wait_tasks(res, client) == "finish"
                elif vm["status"] == 1:
                    res = client.patch(f'/api/tasks/vms/{vm["uuid"]}/power', json={"status": "off"})
                    assert wait_tasks(res, client) == "finish"
                    res = client.patch(f'/api/tasks/vms/{vm["uuid"]}/power', json={"status": "on"})
                    assert wait_tasks(res, client) == "finish"
                    



def test_change_vm_cdrom(env, client, created_vm):
    res_vms = client.get('/api/vms', params={"admin":True})
    
    for vm in res_vms.json()["data"]:
        for env_vm in env.vms:
            if env_vm.name in vm["name"]:
                res_cdrom = client.patch(f'/api/tasks/vms/{vm["uuid"]}/cdrom', json={"target": "hda", "path": None})
                print(res_cdrom)
                assert wait_tasks(res_cdrom, client) == "finish"
                res_cdrom = client.patch(f'/api/tasks/vms/{vm["uuid"]}/cdrom', json={"target": "hda", "path": "/var/lib/libvirt/test/test-iso/ubuntu-24.04.2-live-server-amd64.iso"})
                assert wait_tasks(res_cdrom, client) == "finish"



# @tester
# def patch_vm_network():
#     resp = httpx.request(method="get", url=f'{BASE_URL}/api/vms', params={"admin":True},headers=HEADERS)
#     print_resp(resp=resp)

#     for vm in resp.json()["data"]:
#         if not vm["name"] == "testcode-vm":
#             continue
#         resp = httpx.request(method="get", url=f'{BASE_URL}/api/networks', headers=HEADERS, params={"name_like": "test", "node_name_like": "test-node"})
#         print_resp(resp=resp, debug=True)
#         network_uuid = resp.json()["data"][0]["uuid"]
#         request_data = { "mac": vm["interfaces"][0]["mac"], "networkUuid": network_uuid}
#         resp = httpx.request(method="patch",url=f'{BASE_URL}/api/tasks/vms/{vm["uuid"]}/network', headers=HEADERS, json=request_data)
#         print_resp(resp=resp)
#         wait_tasks(resp)