#!/bin/python3
import libvirt, sys, sqlite3, subprocess, os, time, concurrent.futures, pprint
import vsql, vansible, vhelp, vvirt,vsh

SPATH = '/root/virty/main'
SQLFILE = SPATH + '/data.sqlite'



#Worker
def WorkerStatus():
    p1 = subprocess.Popen(["ps", "-ef"], shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p2 = subprocess.Popen(["grep", "/root/virty/main/vworker.py"], stdin=p1.stdout, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p3 = subprocess.Popen(["grep", "python"], stdin=p2.stdout, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p4 = subprocess.Popen(["wc", "-l"], stdin=p3.stdout, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p1.stdout.close()
    p2.stdout.close()
    p3.stdout.close()
    output = p4.communicate()[0].decode("utf8").replace('\n','')
    if int(output) == 0:
        return "Down"
    else:
        return "Up"

def WorkerUp():
    p1 = subprocess.Popen(["ps", "-ef"], shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p2 = subprocess.Popen(["grep", "/root/virty/main/vworker.py"], stdin=p1.stdout, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p3 = subprocess.Popen(["grep", "python"], stdin=p2.stdout, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p4 = subprocess.Popen(["wc", "-l"], stdin=p3.stdout, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p1.stdout.close()
    p2.stdout.close()
    p3.stdout.close()
    output = p4.communicate()[0].decode("utf8").replace('\n','')
    print(output)
    if int(output) == 0:
        subprocess.Popen(["python3", "/root/virty/main/vworker.py"])


def Queuing(QUE_OBJECT,QUE_METHOD,QUE_JSON):
    vsql.Queuing(QUE_OBJECT,QUE_METHOD,QUE_JSON)




#Domain Power
def DomainStart(DOM_NAME):
    DOM_UUID = vsql.Convert("DOM_NAME","DOM_UUID",DOM_NAME)
    if DOM_UUID == None:
        return ["error","sql","get","Domain name not found",""]
    NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
    NODE_STATUS = vsql.Convert("NODE_NAME","NODE_STATUS",NODE_NAME)
    if not NODE_STATUS == 10:
        return ["skip","node","status","Node is not active",""]
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)



    


    manager = vvirt.Libvirtc(NODE_IP)
    manager.DomainOpen(DOM_UUID)
    result = manager.DomainPoweron()

    manager.DomainOpen(DOM_UUID)
    data = manager.DomainInfo()

    data['node-name'] = NODE_NAME
    data['node-ip'] = NODE_IP

    vsql.SqlUpdateDomain(data)
    print(data)

    return result


def DomainShutdown(DOM_NAME):
    DOM_UUID = vsql.Convert("DOM_NAME","DOM_UUID",DOM_NAME)
    if DOM_UUID == None:
        return ["error","sql","get","Domain name not found",""]
    NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
    NODE_STATUS = vsql.Convert("NODE_NAME","NODE_STATUS",NODE_NAME)
    if not NODE_STATUS == 10:
        return ["skip","node","status","Node is not active",""]
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)
    

    manager = vvirt.Libvirtc(NODE_IP)
    manager.DomainOpen(DOM_UUID)
    result = manager.DomainShutdown()

    manager.DomainOpen(DOM_UUID)
    data = manager.DomainInfo()
    
    data['node-name'] = NODE_NAME
    data['node-ip'] = NODE_IP

    vsql.SqlUpdateDomain(data)
    print(data)

    return result
    
def DomainDestroy(DOM_NAME):
    DOM_UUID = vsql.Convert("DOM_NAME","DOM_UUID",DOM_NAME)
    if DOM_UUID == None:
        return ["error","sql","get","Domain name not found",""]
    NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
    NODE_STATUS = vsql.Convert("NODE_NAME","NODE_STATUS",NODE_NAME)
    if not NODE_STATUS == 10:
        return ["skip","node","status","Node is not active",""]
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)


    manager = vvirt.Libvirtc(NODE_IP)
    manager.DomainOpen(DOM_UUID)
    result = manager.DomainDestroy()

    manager.DomainOpen(DOM_UUID)
    data = manager.DomainInfo()
    
    data['node-name'] = NODE_NAME
    data['node-ip'] = NODE_IP

    vsql.SqlUpdateDomain(data)
    print(data)

    return result

def DomainAutostart(DOM_NAME):
    DOM_UUID = vsql.Convert("DOM_NAME","DOM_UUID",DOM_NAME)
    if DOM_UUID == None:
        return ["error","sql","get","Domain name not found",""]
    NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
    NODE_STATUS = vsql.Convert("NODE_NAME","NODE_STATUS",NODE_NAME)
    if not NODE_STATUS == 10:
        return ["skip","node","status","Node is not active",""]
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    manager = vvirt.Libvirtc(NODE_IP)
    manager.DomainOpen(DOM_UUID)
    result = manager.DomainAutostart()

    manager.DomainOpen(DOM_UUID)
    data = manager.DomainInfo()
    
    data['node-name'] = NODE_NAME
    data['node-ip'] = NODE_IP

    vsql.SqlUpdateDomain(data)
    print(data)

    return result


def DomainNotautostart(DOM_NAME):
    DOM_UUID = vsql.Convert("DOM_NAME","DOM_UUID",DOM_NAME)
    if DOM_UUID == None:
        return ["error","sql","get","Domain name not found",""]
    NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
    NODE_STATUS = vsql.Convert("NODE_NAME","NODE_STATUS",NODE_NAME)
    if not NODE_STATUS == 10:
        return ["skip","node","status","Node is not active",""]
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    editor = vvirt.Libvirtc(NODE_IP)
    editor.DomainOpen(DOM_UUID)
    
    return editor.DomainNotautostart()

def DomainUndefine(DOM_NAME):
    DOM_UUID = vsql.Convert("DOM_NAME","DOM_UUID",DOM_NAME)
    if DOM_UUID == None:
        return ["error","sql","get","Domain name not found",""]
    NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
    NODE_STATUS = vsql.Convert("NODE_NAME","NODE_STATUS",NODE_NAME)
    if not NODE_STATUS == 10:
        return ["skip","node","status","Node is not active",""]
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    editor = vvirt.Libvirtc(NODE_IP)
    editor.DomainOpen(DOM_UUID)
    
    return editor.DomainUndefine()



#Domain Info
def DomainXmlDump(DOM_NAME):
    DOM_UUID = vsql.Convert("DOM_NAME","DOM_UUID",DOM_NAME)
    if DOM_UUID == None:
        return ["error","sql","get","Domain name not found",""]
    NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
    NODE_STATUS = vsql.Convert("NODE_NAME","NODE_STATUS",NODE_NAME)
    if not NODE_STATUS == 10:
        return ["skip","node","status","Node is not active",""]
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    editor = vvirt.Libvirtc(NODE_IP)
    editor.DomainOpen(DOM_UUID)
    
    return editor.DomainXmlDump()

def AllDomainXmlSave():
    NODE_DATAS = vsql.SqlGetAll("kvm_node")
    for NODE in NODE_DATAS:
        manager = vvirt.Libvirtc(NODE[1])
        if manager.node == None:
            print("cont "+NODE[0])
            continue
        xmls = manager.AllDomainXmlPerth()
        for xml in xmls:
            editor = vvirt.Xmlc(vvirt.XmlStringRoot(xml[2]))
            editor.Save("dom")


def DomainXmlSave(NODE_NAME,DOM_UUID):
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)
    manager = vvirt.Libvirtc(NODE_IP)
    if manager.node == None:
        print("cont "+DOM_UUID)
        return 1
    xml = manager.DomainXmlPerth(DOM_UUID)
    editor = vvirt.Xmlc(vvirt.XmlStringRoot(xml[2]))
    editor.Save("dom")


def DomainListInit():
    NODE_DATAS = vsql.SqlGetAll("kvm_node")
    DOMLIST = []
    for NODE in NODE_DATAS:
        if int(NODE[8]) == 20:
            vsql.UpdateDomainStatus([NODE[0]],[],7)
            continue
        elif int(NODE[8]) > 20:
            vsql.UpdateDomainStatus([NODE[0]],[],20)
            continue
        try:
            manager = vvirt.Libvirtc(NODE[1])
        except:
            vsql.UpdateNodeStatus([NODE[0]],50)
            vsql.UpdateDomainStatus([NODE[0]],[],20)
            continue
        xmls = manager.AllDomainXmlPerth()
        for xml in xmls:
            editor = vvirt.Xmlc(vvirt.XmlStringRoot(xml[2]))
            data = editor.DomainData()
            data['node-name'] = NODE[0]
            data['node-ip'] = NODE[1]
            data['power'] = xml[0]
            data['autostart'] = xml[1]
            DOMLIST.append((data['name'], data['power'],data['node-name'],data['vcpu'],data['memory'],data['uuid'],"unknown","unknown"))
            editor.Save("dom")
    vsql.SqlAddDomain(DOMLIST)


def GetNicData(DOM_UUID):
    NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    editor = vvirt.Libvirtc(NODE_IP)
    editor.DomainOpen(DOM_UUID)

    return editor.DomainNicShow()

def DomainData(DOM_UUID):
    NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    editor = vvirt.Xmlc(vvirt.XmlDomainXml(DOM_UUID))

    data = editor.DomainData()
    data['node-name'] = NODE_NAME
    data['node-ip'] = NODE_IP

    return data

def DomainDataNC(DOM_UUID):
    NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    manager = vvirt.Libvirtc(NODE_IP)
    root = vvirt.XmlStringRoot(manager.DomainOpen(DOM_UUID))
    editor = vvirt.Xmlc(root)

    data = editor.DomainData()
    data['node-name'] = NODE_NAME
    data['node-ip'] = NODE_IP

    return data

############################
# Storage                  #
############################
def StorageAdd(STORAGE_NAME,STORAGE_NODE,STORAGE_DEVICE,STORAGE_TYPE,STORAGE_PATH):
    vsql.SqlAddStorage([(STORAGE_NAME,STORAGE_NODE,STORAGE_DEVICE,STORAGE_TYPE,STORAGE_PATH)])    

def StorageListAll():
    NODE_DATAS = vsql.SqlGetAll("kvm_node")
    data = []
    for NODE in NODE_DATAS:
        try:
            editor = vvirt.Libvirtc(NODE[1])
        except:
            continue
        xmls = editor.AllStorageXml()
        for xml in xmls:
            xmledit = vvirt.Xmlc(vvirt.XmlStringRoot(xml))
            get = xmledit.StorageData()
            get['node'] = NODE[0]
            get['device'] = "none"
            get['type'] = "none"
            data.append(get)
    vsql.UpdateStorage(data)
    return data



def StorageList(NODE_NAME):
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)
    editor = vvirt.Libvirtc(NODE_IP)
    xmls = editor.AllStorageXml()
    data = []
    for xml in xmls:
        xmledit = vvirt.Xmlc(vvirt.XmlStringRoot(xml))
        get = xmledit.StorageData()
        get['node'] = NODE_NAME
        data.append(get)
    return data

def StoragepoolXmlDump(NODE_NAME,STORAGE_NAME):
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)
    editor = vvirt.Libvirtc(NODE_IP)
    return editor.StorageXml(STORAGE_NAME)

def StorageMake(NODE_NAME,STORAGE_NAME,STORAGE_PATH):
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    root = vvirt.XmlFileRoot("storage_dir")
    editor = vvirt.Xmlc(root)
    editor.StorageMake(STORAGE_NAME,STORAGE_PATH)

    server = vvirt.Libvirtc(NODE_IP)
    server.StorageDefine(editor.Dump())

def StorageUndefine(NODE_NAME,STORAGE_NAME):
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    server = vvirt.Libvirtc(NODE_IP)
    server.StorageUndefine(STORAGE_NAME)
    return [0,"storage","undefine","Success",""]




#Image
def ImageList(NODE_NAME,STORAGEP_NAME):
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    editor = vvirt.Libvirtc(NODE_IP)
    editor.ImageList(STORAGEP_NAME)



def ImageInfo(NODE_NAME,STORAGEP_NAME,IMG_NAME):
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    editor = vvirt.Libvirtc(NODE_IP)
    editor.ImageInfo(STORAGEP_NAME,IMG_NAME)    

def ImageListXml(NODE_NAME,STORAGEP_NAME):
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    editor = vvirt.Libvirtc(NODE_IP)
    xmls = editor.AllImageXml(STORAGEP_NAME)
    data = []
    for xml in xmls:
        xmledit = vvirt.Xmlc(xml)
        data.append(xmledit.ImageData())
    return data


def AllImageXml():
    NODE_DATAS = vsql.SqlGetAll("kvm_node")
    pool = []
    image = []
    for NODE in NODE_DATAS:
        try:
            nodepoint = vvirt.Libvirtc(NODE[1])
        except:
            continue
        storages = nodepoint.AllStorageXml()
        
        for storage in storages:
            xmledit = vvirt.Xmlc(vvirt.XmlStringRoot(storage))
            get = xmledit.StorageData()
            get['node'] = NODE[0]
            pool.append(get)
            images = nodepoint.AllImageXml(get['name'])
            for xml in images:  
                temp = {}
                imageedit = vvirt.Xmlc(vvirt.XmlStringRoot(xml))
                temp['data']= imageedit.ImageData()
                temp['node'] = NODE[0]
                temp['pool'] = get['name']
                if not temp['data'] == "dir":
                    image.append(temp)

    data = {}
    data['pool'] = pool
    data['image'] = image

    return data



def ImageDelete(NODE_NAME,STORAGEP_NAME,IMG_NAME):
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    editor = vvirt.Libvirtc(NODE_IP)
    editor.ImageDelete(STORAGEP_NAME,IMG_NAME)    


def ImageIsoList(NODE_NAME):
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    image = []
    nodepoint = vvirt.Libvirtc(NODE_IP)
    images = nodepoint.AllImageXml("iso")

    for xml in images:
        imageedit = vvirt.Xmlc(vvirt.XmlStringRoot(xml))
        image.append(imageedit.ImageData())
    return image

def ImageArchiveList(NODE_NAME):
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    image = []
    nodepoint = vvirt.Libvirtc(NODE_IP)
    images = nodepoint.AllImageXml("archive")

    for xml in images:
        imageedit = vvirt.Xmlc(vvirt.XmlStringRoot(xml))
        image.append(imageedit.ImageData())
    return image

def ImageArchiveListAll():
    NODE_DATAS = vsql.SqlGetAll("kvm_node")
    image = []
    for NODE in NODE_DATAS:
        try:
            nodepoint = vvirt.Libvirtc(NODE[1])
        except:
            continue
        images = nodepoint.AllImageXml("archive")
        for xml in images:
            imageedit = vvirt.Xmlc(vvirt.XmlStringRoot(xml))
            data = imageedit.ImageData()
            data['node'] = NODE[0]
            image.append(data)
    return image

#Node
def NodeAdd(NODE_NAME,NODE_IP):
    try:
        NODE_MEM = SshInfoMem(NODE_IP)
        NODE_CORE = SshInfocpu(NODE_IP)
        NODE_CPU = SshInfocpuname(NODE_IP)
        NODE_OS = SshOsinfo(NODE_IP)
    except Exception as e:
        return ["error","node","add",str(e)]

    NODE_DATAS_NEW = []
    NODE_DATAS_NEW.append([NODE_NAME,NODE_IP,NODE_MEM,NODE_CORE,NODE_CPU,NODE_OS['NAME'],NODE_OS['VERSION'],NODE_OS['ID_LIKE'],10])
    vsql.SqlAddNode(NODE_DATAS_NEW)

    print(
        "\nNAME: " + NODE_NAME +
        "\nIP: " + NODE_IP +
        "\nMemory: " + str(NODE_MEM) +
        "\nCore: " + str(NODE_CORE) +
        "\nCPU: " + str(NODE_CPU)	
    )

    print(NODE_OS)
    return ["success","","","Succes"]

#Network
def NetworkXmlSave(NODE_NAME,NET_UUID):
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)
    manager = vvirt.Libvirtc(NODE_IP)
    if manager.node == None:
        print("cont "+NET_UUID)
        return 1
    manager.NetworkOpen(NET_UUID)

    editor = vvirt.Xmlc(manager.netxml)
    editor.Save("net")


def NetworkXmlSaveAll():
    NODE_DATAS = vsql.SqlGetAll("kvm_node")
    for NODE in NODE_DATAS:
        try:
            manager = vvirt.Libvirtc(NODE[1])
        except:
            continue
        if manager.node == None:
            print("cont "+NODE[0])
            continue
        xmls = manager.NetworkXmlRootAll()
        for xml in xmls:
            editor = vvirt.Xmlc(xml)
            editor.Save("net")



def NetworkDHCP(NODE_NAME,NET_UUID):
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)
    manager = vvirt.Libvirtc(NODE_IP)
    if manager.node == None:
        print("cont "+NET_UUID)
        return 1
    manager.NetworkOpen(NET_UUID)
    editor = vvirt.Xmlc(manager.netxml)
    return editor.NetworkData()
    

def NetworkInternalDefine(NODE_NAME,NET_NAME):
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    root = vvirt.XmlFileRoot("net_internal")

    editor = vvirt.Xmlc(root)
    editor.NetworkInternal(NET_NAME)

    manager = vvirt.Libvirtc(NODE_IP)
    manager.NetworkDefine(editor.Dump())
    manager.NetworkStart()


def Network2lDefine(NODE_IP,XML_PATH,NAME,GW):
    editor = vvirt.Libvirtc(NODE_IP)
    editor.NetworkXmlTemplate(XML_PATH)

    print(editor.NetworkXmlDump())
    editor.NetworkXmlL2lEdit(NAME,GW)
    print(editor.NetworkXmlDump())
    editor.NetworkXmlDefine(NODE_IP)
    editor.NetworkStart()

def NetworkListinit():
    vsql.SqlDeleteAll("kvm_network")
    NODE_DATAS = vsql.SqlGetAll("kvm_node")
    data = []
    for NODE in NODE_DATAS:
        try:
            manager = vvirt.Libvirtc(NODE[1])
        except:
            continue
        if manager.node == None:
            print("cont "+NODE[0])
            continue
        xmls = manager.NetworkXmlRootAll()
        for xml in xmls:
            editor = vvirt.Xmlc(xml)
            editor.Save("net")
            temp = editor.NetworkData()
            temp['node'] = NODE[0]
            data.append(temp)
    vsql.NetworkListUpdate(data)


    

def NetworkUndefine(NET_UUID):
    NODE_DATAS = vsql.SqlGetAll("kvm_node")
    for NODE in NODE_DATAS:
        editor = vvirt.Libvirtc(NODE[1])
        editor.NetworkOpen(NET_UUID)
        editor.NetworkStop()
        editor.NetworkUndefine()





def InterfaceList(NODE_NAME):
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)
    editor = vvirt.Libvirtc(NODE_IP)

    return editor.InterfaceList()

def AllInterfaceList():
    NODE_DATAS = vsql.SqlGetAll("kvm_node")
    data = []
    for NODE in NODE_DATAS:
        editor = vvirt.Libvirtc(NODE[1])
        temp = {}
        temp['node'] = NODE[0]
        temp['network'] = editor.InterfaceList()
        data.append(temp)
    return data

def NodeNetworkList(NODE_NAME):
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)
    editor = vvirt.Libvirtc(NODE_IP)
    data = [editor.InterfaceList()]
    data.append(editor.NetworkList())
    return data

def NodeNetworkAllList():
    NODE_DATAS = vsql.SqlGetAll("kvm_node")
    data = []
    for NODE in NODE_DATAS:
        temp = {}
        editor = vvirt.Libvirtc(NODE[1])
        temp['int'] = editor.InterfaceList()
        temp['net'] = editor.NetworkList()
        temp['node'] = NODE[0]
        data.append(temp)
    return data

#DomainMake
def DomainMakeBase(DOM_NAME,MEMORY,CORE,VNC_PORT,VNC_PASS):
    vvirt.XmlDomainBaseMake(DOM_NAME,MEMORY,CORE,VNC_PORT,VNC_PASS)

def DomainMakeNicBridge(DOM_NAME,SOURCE):
    vvirt.XmlBridgeNicAdd(DOM_NAME,SOURCE) 

def DomainMakeImg(DOM_NAME,STORAGE_NAME,ARCHIVE_NAME):
    vvirt.XmlMetaSetStorage(DOM_NAME,STORAGE_NAME,ARCHIVE_NAME)

def DomainDefineStatic(DOM_DIC):
    NODE_NAME = DOM_DIC['node']
    DOM_NAME = DOM_DIC['name']
    NODE_IP = vsql.SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
    NODE_DATA = vsql.SqlGetData("NODE_NAME","NODE_DATA",NODE_NAME)

    editor = vvirt.Xmlc(vvirt.XmlFileRoot("dom_base"))

    editor.DomainEmulator(NODE_DATA[5])
    editor.DomainBaseEdit(DOM_DIC['name'],DOM_DIC['memory'],DOM_DIC['cpu'],"auto","pass")
    editor.DomainImageMeta(DOM_DIC['storage'],DOM_DIC['archive'])
    print(DOM_DIC['nic'])

    for network in DOM_DIC['nic']:
        editor.DomainNetworkAdd(network[1])
        print(network[1])

    IMG_DEVICE_NAME = ["vda","vdb","vdc"]
    COUNTER = 0
    storages = editor.xml.find('metadata').findall('storage')

    for storage in storages:
        IMG_NAME = IMG_DEVICE_NAME[COUNTER]
        COUNTER = COUNTER + 1
        STORAGE_NAME = storage.get('storage')

        for data in StorageList(NODE_NAME):
            if data['name'] == STORAGE_NAME:
                STORAGE_PATH = data['path']
            

        ARCHIVE_NAME = storage.get('archive')
        ARCHIVE_PATH = "/kvm/archive/"+ARCHIVE_NAME

        IMG_PATH = STORAGE_PATH +"/"+ DOM_NAME + "_" + IMG_NAME + '.img'


        editor.DomainImageSet(IMG_PATH)
        vansible.AnsibleFilecpInnode(NODE_IP,ARCHIVE_PATH,IMG_PATH)

    conn = libvirt.open('qemu+ssh://' + NODE_IP + '/system')
    conn.defineXML(editor.Dump())





############################
# Domain-Edit              #
############################
def DomNameEdit(DOM_UUID,NEW_NAME):
    NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    editor = vvirt.Libvirtc(NODE_IP)
    editor.DomainOpen(DOM_UUID)
    editor.DomainNameEdit(NEW_NAME)
    return editor.DomainXmlUpdate()

def DomSelinux(DOM_UUID):
    NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    editor = vvirt.Libvirtc(NODE_IP)
    editor.DomainOpen(DOM_UUID)

    return editor.ShowSelinux()

def DomSelinuxDisable(DOM_UUID):
    NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    editor = vvirt.Libvirtc(NODE_IP)
    editor.DomainOpen(DOM_UUID)

    editor.DeleteSelinux()
    return editor.DomainXmlUpdate()

def DomainEditNicNetwork(DOM_UUID,NOW_MAC,NEW_NIC):
    NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    editor = vvirt.Libvirtc(NODE_IP)
    editor.DomainOpen(DOM_UUID)
    editor.DomainEditNicNetwork(NOW_MAC,NEW_NIC)
    DomainXmlSave(NODE_NAME,DOM_UUID)

def DomCdromExit(DOM_UUID,TARGET):
    NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    editor = vvirt.Libvirtc(NODE_IP)
    editor.DomainOpen(DOM_UUID)
    editor.DomainCdromExit(TARGET)

def DomCdromEdit(DOM_UUID,TARGET,ISO_PATH):
    NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    editor = vvirt.Libvirtc(NODE_IP)
    editor.DomainOpen(DOM_UUID)
    editor.DomainCdromEdit(TARGET,ISO_PATH)

def DomainEditMemory(DOM_UUID,NEW_MEMORY):
    NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    editor = vvirt.Libvirtc(NODE_IP)
    editor.DomainOpen(DOM_UUID)
    editor.DomainEditMemory(NEW_MEMORY)
    return editor.DomainXmlUpdate()

def DomainEditCpu(DOM_UUID,NEW_CPU):
    NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    editor = vvirt.Libvirtc(NODE_IP)
    editor.DomainOpen(DOM_UUID)
    editor.DomainEditCpu(NEW_CPU)
    return editor.DomainXmlUpdate()

############################
# SSH                      #
############################
def SshInfoMem(NODE_IP):
    cmd = ["ssh" , NODE_IP, "cat /proc/meminfo |grep MemTotal"]
    try:
        mem = subprocess.check_output(cmd)
    except Exception as e:
        raise Exception(e)
    words = float(str(mem).split()[1])
    memory = words/1024000
    return memory

def SshInfocpu(NODE_IP):
    cmd = ["ssh" , NODE_IP, "grep processor /proc/cpuinfo | wc -l"]
    words = str(subprocess.check_output(cmd)).rstrip("\\n'").lstrip("'b")
    return words

def SshInfocpuname(NODE_IP):
    cmd = ["ssh" , NODE_IP, "grep 'model name' /proc/cpuinfo|uniq"]
    mem = subprocess.check_output(cmd)
    words = str(mem).split(":")[1].rstrip("\\n'")
    return words

def SshInfoDir(NODE_IP,NODE_DIR):
    cmd = ["ssh" , NODE_IP, "df" ,NODE_DIR,"|sed -e '1d'"]
    get = subprocess.check_output(cmd)
    storage = str(get).rstrip("\\n'").lstrip("b'").split()
    return storage


def SshOsinfo(NODE_IP):
    cmd = ["ssh" , NODE_IP, "cat" ,"/etc/os-release"]
    get = subprocess.check_output(cmd)
    result = {}
    for data in str(get).rstrip("\\n'").lstrip("b'").split("\\n"):
        if not data == "":
            result[data.split("=")[0]] = data.split("=")[1].strip("\"")
    return result

def SshScript(NODE_IP,SCRIPT):
    with open(SPATH + "/script/" + SCRIPT) as f:
        s = f.read().splitlines()
        send = ""
        for a in s:
            if not a == "":
                send = send +  a + ";"
        
    cmd = ["ssh" , NODE_IP, send]
    get = subprocess.check_output(cmd)
    print(get.decode("UTF-8"))
    
        
def SshQemuCreate(NODE_IP,PATH,SIZE):
    cmd = ["ssh" , NODE_IP, "test -e" ,PATH,"; echo $?"]
    get = subprocess.check_output(cmd)
    if get.decode("UTF-8").splitlines()[0] == "1":
        cmd = ["ssh" , NODE_IP, "qemu-img create " ,PATH, SIZE+"G"]
        try:
            create = subprocess.check_output(cmd)
        except Exception as e:
            return ["error","img","create","fail", str(e)]
        if create.decode("UTF-8").splitlines()[0].split(" ")[0] == "Formatting":
            return ["success","img","create","Success",""]
        else:
            return ["error","img","create","fail",create.decode("UTF-8")]
    else:
        return ["skip","img","create","allready",""]
    



if __name__ == "__main__":
    # start = time.time()
    # executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)
    # for i in range(10000):
    #     executor.submit(vsql.SqlGetAll("kvm_domain"))
    # elapsed_time = time.time() - start
    # print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")

    #NetworkInternalDefine("ruri","test-net")

    args = sys.argv
    argnum = len(args)
    if argnum == 1:argobj = "none"
    else: argobj = args[1]

    #Help
    if argnum == 1:
        vhelp.Help()
    elif argnum == 3:
        if args[1] == "dom" and args[2] == "make":vhelp.DomMakeHelp()
        if args[1] == "node" and args[2] == "add":vhelp.NodeAddHelp()
        if args[1] == "storage" and args[2] == "add":vhelp.StorageAddHelp()
    elif argnum == 4:
        if args[1] == "dom" and args[2] == "make" and args[3] == "nomal":vhelp.DomainMakeNomalHelp()
        if args[1] == "dom" and args[2] == "make" and args[3] == "base":vhelp.DomMakeBaseHelp()
        if args[1] == "dom" and args[2] == "make" and args[3] == "nic":vhelp.DomMakeNicHelp()	


    #Ohter
    if argnum == 2:
        if args[1] == "init":vsh.Init()
        if args[1] == "develop":vsh.Develop()
    

    #Domain
    if argobj == "dom":
        if argnum == 3:
            if args[2] == "list":vsh.DomainList()
        elif argnum == 4:
            if args[2] == "start": vsh.DomainStart(args[3])
            if args[2] == "destroy": vsh.DomainDestroy(args[3])
            if args[2] == "shutdown": vsh.DomainShutdown(args[3])
            if args[2] == "autostart": vsh.DomainAutostart(args[3])
            if args[2] == "notautostart": vsh.DomainNotautostart(args[3])
            if args[2] == "info": vsh.DomainInfo(args[3])
            if args[2] == "undefine": vsh.DomainUndefine(args[3])
            if args[2] == "develop": vsh.DomainDevelop(args[3])
            if args[2] == "list" and args[3] == "init":vsh.DomainListInit()
        elif argnum == 5:
            if args[2] == "xml" and args[3] == "dump": vsh.DomainXmlDump(args[4])
        elif argnum == 6:
            if args[2] == "check" and args[3] == "static": vsh.DomainCheckStatic(args[4],args[5])
            if args[2] == "define" and args[3] == "static": vsh.DomainDefineStatic(args[4],args[5])
        elif argnum == 7:
            if args[2] == "make" and args[3] == "nic" and args[4] == "bridge":vsh.DomainMakeNicBridge(args[5],args[6])
            if args[2] == "make" and args[3] == "img":vsh.DomainMakeImg(args[4],args[5],args[6])
        elif argnum == 9:
            if args[2] == "make" and args[3] == "base":vsh.DomainMakeBase(args[4],args[5],args[6],args[7],args[8])

       
    #Node
    if argobj == "node":
        if argnum == 3:
            if args[1] == "node" and args[2] == "list":vsh.NodeList()
        elif argnum == 4:
            if args[1] == "node" and args[2] == "delete":vsh.NodeDelete([args[3]])
        elif argnum == 5:
            if args[1] == "node" and args[2] == "add":vsh.NodeAdd(args[3],args[4])
            if args[1] == "node" and args[2] == "init":vsh.NodeInit(args[3],args[4])
    
    
    #Storage
    if argobj == "storage":
        if argnum == 3:
            if args[2] == "list":vsh.StorageList()
        elif argnum == 4:
            if args[2] == "info":vsh.StorageInfo(args[3])
        elif argnum == 6:
            if args[2] == "xml" and args[3] == "dump":vsh.StorageXmlDump(args[4],args[5])
        elif argnum == 8:
            if args[2] == "add":vsh.StorageAdd(args[3],args[4],args[5],args[6],args[7])	


    #Archive
    if argobj == "archive":
        if argnum == 3:
            if args[1] == "archive" and args[2] == "list":vsh.ArchiveList()
        elif argnum == 4:
            if args[1] == "archive" and args[2] == "init":vsh.ArchiveInit(args[3])


    #Que
    if argobj == "que":
        if argnum == 3:
            if args[2] == "list":vsh.QueList()