import virty
import ast
from time import sleep

SPATH = '/root/virty/main'
SQLFILE = SPATH + '/data.sqlite'

que = virty.vsql.SqlQueuget("running")
if que == None or que == []:
    exit
que = que[0]
POST = ast.literal_eval(que[5])
print("QueGET "+que[3]+" "+que[4])



if que[3] == "domain" and que[4] == "define":
    virty.DomainDefineStatic(POST)
    virty.DomainListInit()
    result = ["success","","","Succes"]

elif que[3] == "domain" and que[4] == "power":
    if POST['status'] == "poweron":
        result = virty.DomainStart(POST['domain-list'])
    elif POST['status'] == "poweroff":
        result = virty.DomainDestroy(POST['domain-list'])
    
elif que[3] == "domain" and que[4] == "selinux":
    if POST['state'] == "disable":
        result = virty.DomSelinuxDisable(POST['uuid'])
    
elif que[3] == "domain" and que[4] == "list-reload":
    virty.DomainListInit()
    result = ["success","","","Succes"]
    print("List-reload")

elif que[3] == "domain" and que[4] == "undefine":
    result = virty.DomainUndefine(POST['domain-list'])
    virty.vsql.SqlDeleteAll("kvm_domain")
    virty.DomainListInit()

elif que[3] == "network" and que[4] == "2l-define":  
    NODE_IP = virty.vsql.SqlGetData("NODE_NAME","NODE_IP",POST['node-list'])
    XML_PATH = SPATH + '/xml/net_2less.xml'
    NAME = "2l-" + POST['net-gw']
    GW = POST['net-gw']
    virty.Network2lDefine(NODE_IP,XML_PATH,NAME,GW)
    virty.vsql.SqlAddNetwork([("l2l",NAME,POST['node-list'])])
    result = ["success","","","Succes"]

elif que[3] == "node" and que[4] == "add":
    result = virty.NodeAdd(POST['name'],POST['user'] +'@'+ POST['ip'])

elif que[3] == "storage" and que[4] == "add":
    virty.StorageMake(POST['node-list'],POST['name'],POST['path'])
    result = ["success","","","Succes"]

elif que[3] == "storage" and que[4] == "undefine":
    result = virty.StorageUndefine(POST['node'],POST['storagename'])
    virty.DomainListInit()

elif que[3] == "domain" and que[4] == "name-edit":
    result = virty.DomNameEdit(POST['uuid'],POST['newname'])
    virty.DomainListInit()


elif que[3] == "domain" and que[4] == "nic-edit":
    virty.DomainEditNicNetwork(POST['uuid'],POST['mac'],POST['network'])
    result = ["success","","","Succes"]    
    virty.DomainListInit()

elif que[3] == "network" and que[4] == "undefine":
    virty.NetworkUndefine(POST['uuid'])
    result = ["success","","","Succes"]

elif que[3] == "network" and que[4] == "internal-define":
    virty.NetworkInternalDefine(POST['node'],POST['net-name'])
    virty.DomainListInit()
    result = ["success","","","Succes"]

elif que[3] == "domain" and que[4] == "memory-edit":
    virty.DomainEditMemory(POST['uuid'],POST['memory'])
    virty.DomainListInit()
    result = ["success","","","Succes"]

elif que[3] == "node" and que[4] == "status-update":
    if POST['status'] == "10" or POST['status'] == "20":
        virty.vsql.UpdateNodeStatus([POST['name']],POST['status'])
        virty.DomainListInit()
        result = ["success","","","Succes"]
    else:
        result = ["success","","","Receive error code"]
    
elif que[3] == "domain" and que[4] == "cpu-edit":
    virty.DomainEditCpu(POST['uuid'],POST['cpu'])
    virty.DomainListInit()
    result = ["success","","","Succes"]

elif que[3] == "image" and que[4] == "resize":
    result = virty.ImageResize(POST['node'],POST['pool'],POST['file'],POST['size'])
    
else:
    print("Found unkown Que")
    result = ["error","que","unkown","Found unkown Que"]

virty.vsql.Dequeuing(que[0],result[0],result[3])