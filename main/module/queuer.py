import setting
import virty
import json
import model
from time import sleep



que = model.raw_fetchall("select * from queue where status =?",["running"])
if que == None or que == []:
    exit
que = que[0]
post_json = json.loads(que['json'])
print("QueGET "+que['object']+" "+que['method'])

result = None

if que['resource'] == "network" and que['method'] == "2l-define":  
    NODE_IP = virty.vsql.SqlGetData("NODE_NAME","NODE_IP",post_json['node-list'])
    XML_PATH = setting.scriptPath + '/xml/net_2less.xml'
    NAME = "2l-" + post_json['net-gw']
    GW = post_json['net-gw']
    virty.Network2lDefine(NODE_IP,XML_PATH,NAME,GW)
    virty.vsql.SqlAddNetwork([("l2l",NAME,post_json['node-list'])])
    



elif que['resource'] == "storage" and que['method'] == "create":
    virty.StorageMake(post_json['node-list'],post_json['name'],post_json['path'])
    

elif que['resource'] == "storage" and que['method'] == "delete":
    result = virty.StorageUndefine(post_json['node'],post_json['storagename'])
    virty.DomainListInit()

elif que['resource'] == "network" and que['method'] == "delete":
    virty.NetworkUndefine(post_json['uuid'])
    

elif que['resource'] == "network" and que['method'] == "internal-define":
    virty.NetworkInternalDefine(post_json['node'],post_json['net-name'])
    virty.DomainListInit()
    

elif que['resource'] == "network" and que['method'] == "bridge-define":
    virty.NetworkBridgeDefine(post_json['node'],post_json['name'],post_json['source'])
    virty.DomainListInit()
    

elif que['resource'] == "node" and que['method'] == "status-update":
    if post_json['status'] == "10" or post_json['status'] == "20":
        virty.vsql.NodeStatusUpdate([post_json['name']],post_json['status'])
        virty.DomainListInit()
        
    else:
        result = ["success","","","Receive error code"]
    
elif que['resource'] == "image" and que['method'] == "resize":
    result = virty.ImageResize(post_json['node'],post_json['pool'],post_json['target'],post_json['size'])

elif que['resource'] == "image" and que['method'] == "delete":
    virty.ImageDelete(post_json['node'],post_json['pool'],post_json['name'])
    virty.DomainListInit()
    



### ノード
elif que['resource'] == "node":
    if que['method'] == "post":
        if que['object'] == "base":
            result = virty.NodeAdd(post_json['name'],post_json['user'] +'@'+ post_json['ip'])



### 仮想マシン
elif que['resource'] == "vm":
    if que['method'] == "post":
        if que['object'] == "base":
            virty.DomainDefineStatic(post_json)
            virty.DomainListInit()
            
    
    elif que['method'] == "delete":
        if que['object'] == "base":
            result = virty.DomainUndefine(post_json['uuid'])
            virty.DomainListInit()

    elif que['method'] == "put":
        if que['object'] == "cpu":
            virty.DomainEditCpu(post_json['uuid'],post_json['cpu'])
            virty.DomainListInit()
            
        elif que['object'] == "memory":
            virty.DomainEditMemory(post_json['uuid'],post_json['memory'])
            virty.DomainListInit()
        
        elif que['object'] == "power":
            if post_json['status'] == "poweron":
                result = virty.DomainStart(post_json['uuid'])
            elif post_json['status'] == "poweroff":
                result = virty.DomainDestroy(post_json['uuid'])
            virty.DomainListInit()
            
        elif que['object'] == "name":
            result = virty.DomNameEdit(post_json['uuid'],post_json['newname'])
            virty.DomainListInit()
        elif que['object'] == "network":
            virty.DomainEditNicNetwork(post_json['uuid'],post_json['mac'],post_json['network'])
            
            virty.DomainListInit()
        elif que['object'] == "list":
            virty.vsql.RawCommit("delete from domain where status=?",["10"])
            virty.DomainListInit()
            
            print("List-reload")

elif que['resource'] == "domain" and que['method'] == "power":
    if post_json['status'] == "poweron":
        result = virty.DomainStart(post_json['uuid'])
    elif post_json['status'] == "poweroff":
        result = virty.DomainDestroy(post_json['uuid'])
    
elif que['resource'] == "domain" and que['method'] == "selinux":
    if post_json['state'] == "disable":
        result = virty.DomSelinuxDisable(post_json['uuid'])
    
elif que['resource'] == "domain" and que['method'] == "reload":
    virty.vsql.RawCommit("delete from domain where status=?",["10"])
    virty.DomainListInit()
    
    print("List-reload")

else:
    print("Found unkown Que")
    result = ["error","que","unkown","Found unkown Que"]
if result == None:
    result = ["success","","","Succes"]
    
virty.vsql.Dequeuing(que['id'],result[0],result[3])