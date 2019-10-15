import virty
import ast
from time import sleep

SPATH = '/root/virty/main'
SQLFILE = SPATH + '/data.sqlite'

while True:
    sleep(3)
    que = virty.vsql.SqlQueuget()
    if que == None:
        print("no job")
        sleep(3)
    elif que == []:
        print("no job")
        sleep(3)
    else:
        print("exist task")
        que = virty.vsql.SqlQueuget()[0]
        if que[4] == "domain":
            print("domain")
            dic = ast.literal_eval(que[5])

            virty.vxml.XmlDomainBaseMake(dic['domain-name'],dic['domain-memory'],dic['domain-cpu'],"auto","pass")
            for nic in dic['nic']:
                print(dic['domain-name'],nic[1])
                virty.vxml.XmlBridgeNicAdd(dic['domain-name'],nic[1])
            virty.vxml.XmlMetaSetStorage(dic['domain-name'],'image',dic['archive-list'])

            print(dic['domain-name'],'image',dic['archive-list'])
            print(dic['domain-name'],dic['node-list'])

            virty.VirtyDomDefineStatic(dic['domain-name'],dic['node-list'])
            virty.VirtyDomainListInit()
            virty.VirtyDomainAutostart(dic['domain-name'])
            virty.vsql.SqlDequeuing(que[0],"finish",100)

            print(dic)
            print("complete")
        elif que[4] == "power":
            print("power")
            dic = ast.literal_eval(que[5])
            if dic['status'] == "poweron":
                virty.VirtyDomainStart(dic['domain-list'])
            elif dic['status'] == "poweroff":
                virty.VirtyDomainDestroy(dic['domain-list'])   
            virty.vsql.SqlDequeuing(que[0],"finish",100)
            virty.VirtyDomainListInit()
        elif que[4] == "listinit":
            print("init")
            virty.vsql.SqlDeleteAll("kvm_domain")
            virty.VirtyDomainListInit()
            virty.vsql.SqlDequeuing(que[0],"finish",100)
        elif que[4] == "undefine":
            print("undefine")
            dic = ast.literal_eval(que[5])
            virty.VirtyDomUndefine(dic['domain-list'])
            virty.vsql.SqlDeleteAll("kvm_domain")
            virty.VirtyDomainListInit()
            virty.vsql.SqlDequeuing(que[0],"finish",100)

        elif que[4] == "2ldefine":
            print("2ldefine")
            dic = ast.literal_eval(que[5])
            NODE_IP = virty.vsql.SqlGetData("NODE_NAME","NODE_IP",dic['node-list'])
            XML_PATH = SPATH + '/xml/net_l2less.xml'
            NAME = dic['net-name']
            GW = dic['net-gw']
            virty.VirtyNetwork2lDefine(NODE_IP,XML_PATH,NAME,GW)
            virty.vsql.SqlAddNetwork([("l2l",NAME,dic['node-list'])])
            virty.vsql.SqlDequeuing(que[0],"finish",100)