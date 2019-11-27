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
<<<<<<< HEAD
    elif que == []:
        print("no job")
        sleep(3)
    else:
        print("exist task")
        que = virty.vsql.SqlQueuget()[0]
        
        if que[4] == "domain":
            print("domain")
            dic = ast.literal_eval(que[5])

            virty.vvirt.XmlDomainBaseMake(dic['domain-name'],dic['domain-memory'],dic['domain-cpu'],"auto","pass")
            for nic in dic['nic']:
                print(dic['domain-name'],nic[1])
                virty.vvirt.XmlBridgeNicAdd(dic['domain-name'],nic[1])
            virty.vvirt.XmlMetaSetStorage(dic['domain-name'],dic['storage-list'],dic['archive-list'])

            print(dic['domain-name'],dic['storage-list'],dic['archive-list'])
            print(dic['domain-name'],dic['node-list'])

            if not virty.DomainDefineStatic(dic['domain-name'],dic['node-list']) == 0:
                virty.vsql.SqlDequeuing(que[0],"fail",100)
                break

            #virty.VirtyDomainAutostart(dic['domain-name'])
            virty.DomainListInit()
            virty.vsql.SqlDequeuing(que[0],"finish",100)

            print("complete")

        elif que[4] == "power":
            print("power")
            dic = ast.literal_eval(que[5])
            if dic['status'] == "poweron":
                virty.DomainStart(dic['domain-list'])
            elif dic['status'] == "poweroff":
                virty.DomainDestroy(dic['domain-list'])   
            virty.vsql.SqlDequeuing(que[0],"finish",100)
            virty.DomainListInit()

        elif que[4] == "listinit":
            print("init")
            sleep(10)
            virty.DomainListInit()
            virty.vsql.SqlDequeuing(que[0],"finish",100)

        elif que[4] == "undefine":
            print("undefine")
            dic = ast.literal_eval(que[5])
            virty.DomainUndefine(dic['domain-list'])
            virty.vsql.SqlDeleteAll("kvm_domain")
            virty.DomainListInit()
            virty.vsql.SqlDequeuing(que[0],"finish",100)

        elif que[4] == "2ldefine":
            print("2ldefine")
            dic = ast.literal_eval(que[5])
            NODE_IP = virty.vsql.SqlGetData("NODE_NAME","NODE_IP",dic['node-list'])
            XML_PATH = SPATH + '/xml/net_l2less.xml'
            NAME = "2l-" + dic['net-gw']
            GW = dic['net-gw']
            virty.Network2lDefine(NODE_IP,XML_PATH,NAME,GW)
            virty.vsql.SqlAddNetwork([("l2l",NAME,dic['node-list'])])
            virty.vsql.SqlDequeuing(que[0],"finish",100)
        
        elif que[4] == "nodeadd":
            print("nodeadd")
            dic = ast.literal_eval(que[5])
            virty.NodeAdd(dic['name'],dic['user'] +'@'+ dic['ip'])
            virty.vsql.SqlDequeuing(que[0],"finish",100)

        elif que[4] == "storage":
            print("storage")
            dic = ast.literal_eval(que[5])
            if dic['system'] == "archive":NAME = "archive"
            elif dic['system'] == "data":  NAME = dic['name']
            virty.StorageMake(dic['node-list'],NAME,dic['path'])
            virty.StorageAdd(NAME,dic['node-list'],dic['device'],dic['type'],dic['path'])
            virty.vsql.SqlDequeuing(que[0],"finish",100)

        elif que[4] == "domnameedit":
            print("domnameedit")
            dic = ast.literal_eval(que[5])
            virty.DomNameEdit(dic['uuid'],dic['newname'])
            virty.vsql.SqlDequeuing(que[0],"finish",100)     

        elif que[4] == "dom_nic":
            print("dom_nic")
            dic = ast.literal_eval(que[5])
            virty.DomNicEdit(dic['uuid'],dic['mac'],dic['network'])
            virty.vsql.SqlDequeuing(que[0],"finish",100)     
<<<<<<< HEAD
            
=======
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
            virty.DomainStart(dic['domain-list'])
        elif dic['status'] == "poweroff":
            virty.DomainDestroy(dic['domain-list'])
        virty.DomainListInit()
        virty.vsql.Dequeuing(que[0],"finish","Succses")
        


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
        if dic['system'] == "archive":NAME = "archive"
        elif dic['system'] == "data":  NAME = dic['name']
        virty.StorageMake(dic['node-list'],NAME,dic['path'])
        virty.StorageAdd(NAME,dic['node-list'],dic['device'],dic['type'],dic['path'])
        virty.vsql.Dequeuing(que[0],"finish","Succses")



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
        


    elif que[3] == "network" and que[4] == "undefine":
        dic = ast.literal_eval(que[5])
        virty.NetworkUndefine(dic['uuid'])
        virty.vsql.Dequeuing(que[0],"finish","Succses")
        


    elif que[3] == "network" and que[4] == "internal-define":
        dic = ast.literal_eval(que[5])
        virty.NetworkInternalDefine(dic['node'],dic['net-name'])
        virty.vsql.Dequeuing(que[0],"finish","Succses")

    else:
        print("Found unkown Que")
>>>>>>> develop
=======
            
>>>>>>> 56babd9828bb8d157f524dc38631ca32e0778780
