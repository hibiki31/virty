import virty
import ast
from time import sleep

SPATH = '/root/virty/main'
SQLFILE = SPATH + '/data.sqlite'

while True:
    print("Checking Que")
    que = virty.vsql.SqlQueuget()
    if que == None or que == []:
        sleep(3)
        continue
    
    que = que[0]

    print("Found "+que[3]+" "+que[4])

    if que[3] == "domain" and que[4] == "define":
        dic = ast.literal_eval(que[5])

        virty.vvirt.XmlDomainBaseMake(dic['name'],dic['memory'],dic['cpu'],"auto","pass")
        for nic in dic['nic']:
            virty.vvirt.XmlBridgeNicAdd(dic['name'],nic[1])
        virty.vvirt.XmlMetaSetStorage(dic['name'],dic['storage'],dic['archive'])

        if not virty.DomainDefineStatic(dic['name'],dic['node']) == 0:
            virty.vsql.Dequeuing(que[0],"fail","Can't define")
            break
        virty.DomainListInit()
        virty.vsql.Dequeuing(que[0],"finish","Succses")



    elif que[3] == "domain" and que[4] == "power":
        dic = ast.literal_eval(que[5])
        if dic['status'] == "poweron":
            result = virty.DomainStart(dic['domain-list'])
            virty.vsql.Dequeuing(que[0],"finish",result[3])
        elif dic['status'] == "poweroff":
            result = virty.DomainDestroy(dic['domain-list'])
            virty.vsql.Dequeuing(que[0],"finish",result[3])
        

    elif que[3] == "domain" and que[4] == "selinux":
        dic = ast.literal_eval(que[5])
        if dic['state'] == "disable":
            result = virty.DomSelinuxDisable(dic['uuid'])
            virty.vsql.Dequeuing(que[0],"finish",result[3])
        

    elif que[3] == "domain" and que[4] == "list-reload":
        virty.DomainListInit()
        virty.vsql.Dequeuing(que[0],"finish","Succses")



    elif que[3] == "domain" and que[4] == "undefine":
        dic = ast.literal_eval(que[5])
        result = virty.DomainUndefine(dic['domain-list'])
        virty.vsql.SqlDeleteAll("kvm_domain")
        virty.DomainListInit()
        if result[0] == 0:
            virty.vsql.Dequeuing(que[0],"finish","Succses")
        if result[0] == 1:
            virty.vsql.Dequeuing(que[0],"skip",result[3])



    elif que[3] == "network" and que[4] == "2l-define":
        dic = ast.literal_eval(que[5])
        NODE_IP = virty.vsql.SqlGetData("NODE_NAME","NODE_IP",dic['node-list'])
        XML_PATH = SPATH + '/xml/net_2less.xml'
        NAME = "2l-" + dic['net-gw']
        GW = dic['net-gw']
        virty.Network2lDefine(NODE_IP,XML_PATH,NAME,GW)
        virty.vsql.SqlAddNetwork([("l2l",NAME,dic['node-list'])])
        virty.vsql.Dequeuing(que[0],"finish","Succses")
    


    elif que[3] == "node" and que[4] == "add":
        dic = ast.literal_eval(que[5])
        virty.NodeAdd(dic['name'],dic['user'] +'@'+ dic['ip'])
        virty.vsql.Dequeuing(que[0],"finish","Succses")



    elif que[3] == "storage" and que[4] == "add":
        dic = ast.literal_eval(que[5])
        
        virty.StorageMake(dic['node-list'],dic['name'],dic['path'])

        virty.vsql.Dequeuing(que[0],"finish","Succses")



    elif que[3] == "storage" and que[4] == "undefine":
        dic = ast.literal_eval(que[5])
        result = virty.StorageUndefine(dic['node'],dic['storagename'])
        if result[0] == 0:
            virty.vsql.Dequeuing(que[0],"finish","Succses")
        if result[0] == 1:
            virty.vsql.Dequeuing(que[0],"skip",result[3])



    elif que[3] == "domain" and que[4] == "name-edit":
        dic = ast.literal_eval(que[5])
        result = virty.DomNameEdit(dic['uuid'],dic['newname'])
        if result[0] == 0:
            virty.vsql.Dequeuing(que[0],"finish","Succses")
        if result[0] == 1:
            virty.vsql.Dequeuing(que[0],"skip",result[1])
        virty.DomainListInit()



    elif que[3] == "domain" and que[4] == "nic-edit":
        dic = ast.literal_eval(que[5])
        virty.DomNicEdit(dic['uuid'],dic['mac'],dic['network'])
        virty.vsql.Dequeuing(que[0],"finish","Succses")    
        virty.DomainListInit()


    elif que[3] == "network" and que[4] == "undefine":
        dic = ast.literal_eval(que[5])
        virty.NetworkUndefine(dic['uuid'])
        virty.vsql.Dequeuing(que[0],"finish","Succses")
        


    elif que[3] == "network" and que[4] == "internal-define":
        dic = ast.literal_eval(que[5])
        virty.NetworkInternalDefine(dic['node'],dic['net-name'])
        virty.NetworkListinit()
        virty.vsql.Dequeuing(que[0],"finish","Succses")

    else:
        print("Found unkown Que")