import virty

api = virty.api(endpoint="")

api.auth_login("admin","admin")

vm_order = {}
vm_order['node'] = ""
vm_order['archive'] = "ubuntu_18"
vm_order['type'] = "archive"
vm_order['pool'] = "ssd"
vm_order['cpu'] = "1"
vm_order['memory'] = "1024"
vm_order['networks'] = ["test-net"]

for i in range(1,3):
    vm_order['name'] = "ubuntu_"+str(i)
    api.domain_define(vm_order)