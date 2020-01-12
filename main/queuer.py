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

def ExitQueue(RESULT):
    if RESULT[0] == 0:
        virty.vsql.Dequeuing(que[0],"finish",RESULT[3])
    elif RESULT[0] == 1:
        virty.vsql.Dequeuing(que[0],"skip",RESULT[3])
    elif RESULT[0] == 2:
        virty.vsql.Dequeuing(que[0],"error",RESULT[3])
    return

if que[3] == "domain" and que[4] == "define":
    virty.DomainDefineStatic(POST)
    virty.DomainListInit()
    virty.vsql.Dequeuing(que[0],"finish","Succses")

elif que[3] == "domain" and que[4] == "power":
    if POST['status'] == "poweron":
        result = virty.DomainStart(POST['domain-list'])
    elif POST['status'] == "poweroff":
        result = virty.DomainDestroy(POST['domain-list'])
    ExitQueue(result)
    
elif que[3] == "domain" and que[4] == "selinux":
    if POST['state'] == "disable":
        result = virty.DomSelinuxDisable(POST['uuid'])
        virty.vsql.Dequeuing(que[0],"finish",result[3])
    
elif que[3] == "domain" and que[4] == "list-reload":
    virty.DomainListInit()
    virty.vsql.Dequeuing(que[0],"finish","Succses")
    sleep(10)
    print("List-reload")

elif que[3] == "domain" and que[4] == "undefine":
    result = virty.DomainUndefine(POST['domain-list'])
    virty.vsql.SqlDeleteAll("kvm_domain")
    virty.DomainListInit()
    ExitQueue(result)

elif que[3] == "network" and que[4] == "2l-define":  
    NODE_IP = virty.vsql.SqlGetData("NODE_NAME","NODE_IP",POST['node-list'])
    XML_PATH = SPATH + '/xml/net_2less.xml'
    NAME = "2l-" + POST['net-gw']
    GW = POST['net-gw']
    virty.Network2lDefine(NODE_IP,XML_PATH,NAME,GW)
    virty.vsql.SqlAddNetwork([("l2l",NAME,POST['node-list'])])
    virty.vsql.Dequeuing(que[0],"finish","Succses")

elif que[3] == "node" and que[4] == "add":
    virty.NodeAdd(POST['name'],POST['user'] +'@'+ POST['ip'])
    virty.vsql.Dequeuing(que[0],"finish","Succses")

elif que[3] == "storage" and que[4] == "add":
    virty.StorageMake(POST['node-list'],POST['name'],POST['path'])
    virty.vsql.Dequeuing(que[0],"finish","Succses")

elif que[3] == "storage" and que[4] == "undefine":
    result = virty.StorageUndefine(POST['node'],POST['storagename'])
    virty.DomainListInit()
    ExitQueue(result)

elif que[3] == "domain" and que[4] == "name-edit":
    result = virty.DomNameEdit(POST['uuid'],POST['newname'])
    virty.DomainListInit()
    ExitQueue(result)

elif que[3] == "domain" and que[4] == "nic-edit":
    virty.DomainEditNicNetwork(POST['uuid'],POST['mac'],POST['network'])
    virty.vsql.Dequeuing(que[0],"finish","Succses")    
    virty.DomainListInit()

elif que[3] == "network" and que[4] == "undefine":
    virty.NetworkUndefine(POST['uuid'])
    virty.vsql.Dequeuing(que[0],"finish","Succses")

elif que[3] == "network" and que[4] == "internal-define":
    virty.NetworkInternalDefine(POST['node'],POST['net-name'])
    virty.NetworkListinit()
    virty.vsql.Dequeuing(que[0],"finish","Succses")

elif que[3] == "domain" and que[4] == "memory-edit":
    virty.DomainEditMemory(POST['uuid'],POST['memory'])
    virty.DomainListInit()
    virty.vsql.Dequeuing(que[0],"finish","Succses")
    
elif que[3] == "domain" and que[4] == "cpu-edit":
    virty.DomainEditCpu(POST['uuid'],POST['cpu'])
    virty.DomainListInit()
    virty.vsql.Dequeuing(que[0],"finish","Succses")
else:
    print("Found unkown Que")
    virty.vsql.Dequeuing(que[0],"error","Found unkown Que")
