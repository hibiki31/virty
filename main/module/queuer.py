import setting
import virty
import json
import model
from time import sleep



que = model.raw_fetchall("select * from queue where status =?",["running"])
if que == None or que == []:
    exit
que = que[0]
POST = json.loads(que['json'])
print("QueGET "+que['object']+" "+que['method'])



if que['object'] == "domain" and que['method'] == "define":
    virty.DomainDefineStatic(POST)
    virty.DomainListInit()
    result = ["success","","","Succes"]

elif que['object'] == "domain" and que['method'] == "power":
    if POST['status'] == "poweron":
        result = virty.DomainStart(POST['domain-list'])
    elif POST['status'] == "poweroff":
        result = virty.DomainDestroy(POST['domain-list'])
    
elif que['object'] == "domain" and que['method'] == "selinux":
    if POST['state'] == "disable":
        result = virty.DomSelinuxDisable(POST['uuid'])
    
elif que['object'] == "domain" and que['method'] == "list-reload":
    virty.vsql.RawCommit("delete from domain where status=?",["10"])
    virty.DomainListInit()
    result = ["success","","","Succes"]
    print("List-reload")

elif que['object'] == "domain" and que['method'] == "undefine":
    result = virty.DomainUndefine(POST['uuid'])
    virty.DomainListInit()

elif que['object'] == "network" and que['method'] == "2l-define":  
    NODE_IP = virty.vsql.SqlGetData("NODE_NAME","NODE_IP",POST['node-list'])
    XML_PATH = setting.scriptPath + '/xml/net_2less.xml'
    NAME = "2l-" + POST['net-gw']
    GW = POST['net-gw']
    virty.Network2lDefine(NODE_IP,XML_PATH,NAME,GW)
    virty.vsql.SqlAddNetwork([("l2l",NAME,POST['node-list'])])
    result = ["success","","","Succes"]

elif que['object'] == "node" and que['method'] == "add":
    result = virty.NodeAdd(POST['name'],POST['user'] +'@'+ POST['ip'])

elif que['object'] == "storage" and que['method'] == "add":
    virty.StorageMake(POST['node-list'],POST['name'],POST['path'])
    result = ["success","","","Succes"]

elif que['object'] == "storage" and que['method'] == "undefine":
    result = virty.StorageUndefine(POST['node'],POST['storagename'])
    virty.DomainListInit()

elif que['object'] == "domain" and que['method'] == "name-edit":
    result = virty.DomNameEdit(POST['uuid'],POST['newname'])
    virty.DomainListInit()


elif que['object'] == "domain" and que['method'] == "nic-edit":
    virty.DomainEditNicNetwork(POST['uuid'],POST['mac'],POST['network'])
    result = ["success","","","Succes"]    
    virty.DomainListInit()

elif que['object'] == "network" and que['method'] == "undefine":
    virty.NetworkUndefine(POST['uuid'])
    result = ["success","","","Succes"]

elif que['object'] == "network" and que['method'] == "internal-define":
    virty.NetworkInternalDefine(POST['node'],POST['net-name'])
    virty.DomainListInit()
    result = ["success","","","Succes"]

elif que['object'] == "network" and que['method'] == "bridge-define":
    virty.NetworkBridgeDefine(POST['node'],POST['name'],POST['source'])
    virty.DomainListInit()
    result = ["success","","","Succes"]

elif que['object'] == "domain" and que['method'] == "memory-edit":
    virty.DomainEditMemory(POST['uuid'],POST['memory'])
    virty.DomainListInit()
    result = ["success","","","Succes"]

elif que['object'] == "node" and que['method'] == "status-update":
    if POST['status'] == "10" or POST['status'] == "20":
        virty.vsql.NodeStatusUpdate([POST['name']],POST['status'])
        virty.DomainListInit()
        result = ["success","","","Succes"]
    else:
        result = ["success","","","Receive error code"]
    
elif que['object'] == "domain" and que['method'] == "cpu-edit":
    virty.DomainEditCpu(POST['uuid'],POST['cpu'])
    virty.DomainListInit()
    result = ["success","","","Succes"]

elif que['object'] == "image" and que['method'] == "resize":
    result = virty.ImageResize(POST['node'],POST['pool'],POST['target'],POST['size'])

elif que['object'] == "image" and que['method'] == "delete":
    virty.ImageDelete(POST['node'],POST['pool'],POST['name'])
    virty.DomainListInit()
    result = ["success","","","Succes"]
    
else:
    print("Found unkown Que")
    result = ["error","que","unkown","Found unkown Que"]

virty.vsql.Dequeuing(que['id'],result[0],result[3])