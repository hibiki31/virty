from time import  sleep
import virty,ast
while True:
    sleep(1)
    que = virty.SqlGetAll("kvm_que")
    if que == None:
        print("no job")
        sleep(1)
    elif que == []:
        print("no job")
        sleep(1)       
    elif que[0][1] == "domain":
        dic = ast.literal_eval(que[0][2])

        virty.XmlDomainBaseMake(dic['domain-name'],dic['domain-memory'],dic['domain-cpu'],"auto","pass")
        for nic in dic['nic']:
            print(dic['domain-name'],nic[1])
            virty.XmlBridgeNicAdd(dic['domain-name'],nic[1])
        virty.XmlMetaSetStorage(dic['domain-name'],'image',dic['archive-list'])

        print(dic['domain-name'],'image',dic['archive-list'])
        print(dic['domain-name'],dic['node-list'])

        virty.VirtyDomDefineStatic(dic['domain-name'],dic['node-list'])
        virty.VirtyDomainAutostart(dic['domain-name'])
        virty.VirtyDomainListInit()

        virty.SqlDequeDomain(que[0][0])

        print(dic)
        print("complete")
    elif que[0][1] == "power":
        dic = ast.literal_eval(que[0][2])

        if dic['status'] == "poweron":
            virty.VirtyDomainStart(dic['domain-list'])
        elif dic['status'] == "poweroff":
            virty.VirtyDomainDestroy(dic['domain-list'])   

        virty.SqlDequeDomain(que[0][0])
    elif que[0][1] == "listinit":
        
        virty.VirtyDomainListInit()
        virty.SqlDequeDomain(que[0][0])




