#!/usr/local/bin/python3
import libvirt
import sys
import sqlite3
import subprocess
import os
from module import vsql, vansible, vhelp, virtlib, virty, setting


#Class
class Color():
    BLACK     = '\033[30m'
    RED       = '\033[31m'
    GREEN     = '\033[32m'
    CYAN      = '\033[36m'
    END       = '\033[0m'
  



#Log
def LogInfo(TAG,TEXT):
    print("[" + Color.CYAN + TAG + Color.END + "] " +  TEXT)

def LogError(TAG,TEXT):
    print("[" + Color.RED + TAG + Color.END + "] " +  TEXT)

def LogSuccess(TAG,TEXT):
    print("[" + Color.GREEN + TAG + Color.END + "] " +  TEXT)



#Ohter
def Init():
    inputvalue = input("Do you want to initialize the database?(y or other):")
    if inputvalue == "y":
        vsql.SqlInit()

def Develop():
    conn = libvirt.open('qemu:///system')
    names = conn.listDefinedDomains()
    print(names)
    clist = dir(conn)
    for item in clist:
        print(item)



#Domain
def DomainList():
    datas = vsql.SqlGetDomain()
    print('POWER {0:16} {1:8} {2:4} {3:5} {4:36} {5:8} {6:8}'.format("NAME","NODE","CORE","MEMORY","UUID","TYPE","OS"))
    for data in datas:
        if data[1] == "SHT":
            LogError("SHT",'{0:16} {1:8} {2:4} {3:5} {4:36} {5:8} {6:8}'.format(data[0], data[2], data[3],data[4],data[5], data[6], data[7]))
        elif data[1] == "RUN":
            LogSuccess("RUN",'{0:16} {1:8} {2:4} {3:5} {4:36} {5:8} {6:8}'.format(data[0], data[2], data[3], data[4],data[5], data[6], data[7]))

def DomainStart(DOM_NAME):
    result = virty.DomainStart(DOM_NAME)
    if result[0] == 0:
        LogSuccess("SUCC", result[3])
    elif result[0] == 1:
        LogInfo("INFO", result[3])
    else:
        LogError("ERRO", result[3])
    
def DomainAutostart(DOM_NAME):
    result = virty.DomainAutostart(DOM_NAME)
    if result[0] == 0:
        LogSuccess("SUCC", result[3])
    elif result[0] == 1:
        LogInfo("INFO", result[3])
    else:
        LogError("ERRO", result[3])

def DomainNotautostart(DOM_NAME):
    result = virty.DomainNotautostart(DOM_NAME)
    if result[0] == 0:
        LogSuccess("SUCC", result[3])
    elif result[0] == 1:
        LogInfo("INFO", result[3])
    else:
        LogError("ERRO", result[3])

def DomainShutdown(DOM_NAME):
    result = virty.DomainShutdown(DOM_NAME)
    if result[0] == 0:
        LogSuccess("SUCC", result[3])
    elif result[0] == 1:
        LogInfo("INFO", result[3])
    else:
        LogError("ERRO", result[3])
    
def DomainDestroy(DOM_NAME):
    result = virty.DomainDestroy(DOM_NAME)
    if result[0] == 0:
        LogSuccess("SUCC", result[3])
    elif result[0] == 1:
        LogInfo("INFO", result[3])
    else:
        LogError("ERRO", result[3])

def DomainInfo(DOM_NAME):
    import xml.etree.ElementTree as ET 
    NODE_NAME = vsql.SqlGetData("DOM_NAME","NODE_NAME",DOM_NAME)
    NODE_IP = vsql.SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
    conn = libvirt.open('qemu+ssh://' + NODE_IP + '/system')
    con = conn.lookupByName(DOM_NAME)
    root = ET.fromstring(con.XMLDesc())
    print("NAME  :"+root.find('name').text)
    print("RAM   :"+root.find('memory').text)
    print("UNIT  :"+root.find('memory').get("unit"))
    print("vCPU  :"+root.find('vcpu').text)
    vnc = root.find('devices').find('graphics')
    print("VNC   :" +
        "  PORT:" + vnc.get("port") +\
        "  AUTO:" + vnc.get("autoport") +\
        "  LISTEN:" + vnc.get("listen") +\
        "  PASSWD:" + vnc.get("passwd", "none"))
    for disk in root.find('devices').findall('disk'):
        if disk.find("source") is not None:
            print(\
                "DEVICE:" + disk.get("device") +\
                "   TYPE:" + disk.get("type") +\
                "   FILE:" + disk.find("source").get("file","none")+\
                "   TARGET:" + disk.find("target").get("dev"))
        else:
            print("DEVICE:" + \
                disk.get("device") + "  TYPE:" + \
                disk.get("type") + "  " + \
                "Not Connected"+ "  " + \
                disk.find("target").get("dev"))
    for nic in root.find('devices').findall('interface'):
        print("DEVICE:NIC  TYPE:" + \
            nic.get("type") + "   MAC:" + \
            nic.find("mac").get("address")+ "   Target:" + \
            nic.find("target").get("dev")+ "   " + \
            nic.find("source").get("bridge"))

def DomainListInit():
    virty.DomainListInit()
    DomainList()

def DomainUndefine(DOM_NAME):
    result = virty.DomainUndefine(DOM_NAME)
    if result[0] == 0:
        LogSuccess("SUCC", result[3])
    elif result[0] == 1:
        LogInfo("INFO", result[3])
    else:
        LogError("ERRO", result[3])

def DomainDevelop(DOM_NAME):
    NODE_NAME = vsql.SqlGetData("DOM_NAME","NODE_NAME",DOM_NAME)
    NODE_IP = vsql.SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
    conn = libvirt.open('qemu+ssh://' + NODE_IP + '/system')
    p = conn.lookupByName(DOM_NAME)
    clist = dir(p)
    for item in clist:
        print(item)



#DomainMake
def DomainCheckStatic(DOM_NAME,NODE_NAME):
    import xml.etree.ElementTree as ET 

    NODE_IP = vsql.SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
    if NODE_IP == None:
        LogError("NG",NODE_NAME + " is not found")
        exit(1)
    else:
        LogSuccess("OK","Node is found")

    try:
        tree = ET.parse(setting.script_path + '/define/' + DOM_NAME + '.xml') 
        root = tree.getroot()
    except:
        LogError("NG","File dose not exit")
        exit(2)

    LogSuccess("OK","File is exist")	



    print("NAME  :"+root.find('name').text)
    print("RAM   :"+root.find('memory').text)
    print("UNIT  :"+root.find('memory').get("unit"))
    print("vCPU  :"+root.find('vcpu').text)

    storages = root.find('metadata').findall('storage')
    for storage in storages:
        if vsql.SqlGetData("ARCHIVE_DATA","EXIST_STATUS",(NODE_NAME,storage.get('archive'))) == 1:
            LogError("NG","Archive dose not exits")
            exit(3)
        LogSuccess("OK",storage.get('archive') + " dose exits")	

        STORAGE_PATH = vsql.SqlGetData("STORAGE_DATA","STORAGE_PATH",(NODE_NAME,storage.get('storage')))
        if STORAGE_PATH == 1:
            LogError("NG","Storage dose not found in node")
            exit(4)
        LogSuccess("OK",str(storage.get('storage')) + " is exist")

def DomainDefineStatic(DOM_NAME,NODE_NAME):
    virty.DomainDefineStatic(DOM_NAME,NODE_NAME)
    
def DomainMakeBase(DOM_NAME,MEMORY,CORE,VNC_PORT,VNC_PASS):
    virty.DomainMakeBase(DOM_NAME,MEMORY,CORE,VNC_PORT,VNC_PASS)
    LogSuccess("OK","Base maked")

def DomainMakeNicBridge(DOM_NAME,SOURCE):
    vxml.XmlBridgeNicAdd(DOM_NAME,SOURCE)
    LogInfo("OK","Nic added")
    
def DomainMakeImg(DOM_NAME,STORAGE_NAME,ARCHIVE_NAME):
    vxml.XmlMetaSetStorage(DOM_NAME,STORAGE_NAME,ARCHIVE_NAME)
    LogInfo("OK","Img added")

def DomainXmlDump(DOM_NAME):
    result = virty.DomainXmlDump(DOM_NAME)
    if result[0] == 0:
        LogSuccess("SUCC", result[3])
        print(result[4])
    elif result[0] == 1:
        LogInfo("INFO", result[3])
    else:
        LogError("ERRO", result[3])



#Node
def NodeList():
    nodes = vsql.SqlGetAll("node")
    for data in nodes:
        LogInfo("NODE",'{0:8} {1:14} {2:6.2f} {3:2} {4:8}'.format(data[0], data[1], data[2], str(data[3]),data[4]))
    vansible.AnsibleNodelistInit()

def NodeAdd(NODE_NAME,NODE_IP):
    NODE_MEM = virty.SshInfoMem(NODE_IP)
    NODE_CORE = virty.SshInfocpu(NODE_IP)
    NODE_CPU = virty.SshInfocpuname(NODE_IP)
    NODE_DATAS_NEW = []
    NODE_DATAS_NEW.append([NODE_NAME,NODE_IP,NODE_MEM,NODE_CORE,NODE_CPU])
    vsql.SqlAddNode(NODE_DATAS_NEW)

    print(
        "\nNAME: " + NODE_NAME +
        "\nIP: " + NODE_IP +
        "\nMemory: " + str(NODE_MEM) +
        "\nCore: " + str(NODE_CORE) +
        "\nCPU: " + str(NODE_CPU)	
    )
    LogInfo("OK","Node added")
    
def NodeDelete(NODENAME):
    vsql.SqlDeleteNode(NODENAME)
    LogInfo("OK", str(NODENAME) + "is deleted")

def NodeInit(PBNAME,EXVALUE):
    if PBNAME == "gluster":
        cmd = 'ansible-playbook ' + setting.script_path + '/ansible/pb_init_gluster.yml -i  ' + setting.script_path + '/ansible/host_node.ini --extra-vars ' + EXVALUE
        subprocess.check_call(cmd, shell=True)
    elif PBNAME == "libvirt":
        cmd = 'ansible-playbook ' + setting.script_path + '/ansible/pb_init_libvirt.yml -i  ' + setting.script_path + '/ansible/host_node.ini'
        subprocess.check_call(cmd, shell=True)	
    elif PBNAME == "frr":
        cmd = 'ansible-playbook ' + setting.script_path + '/ansible/pb_init_frr.yml -i  ' + setting.script_path + '/ansible/host_node.ini'
        subprocess.check_call(cmd, shell=True)



#Storage
def StorageList():
    datas = vsql.SqlGetAll("storage")
    print('          {0:12} {1:8} {2:8} {3:8} {4:8}'.format("NAME","NODE","DEVICE","TYPE","PATH"))
    for data in datas:
        LogSuccess("STORAGE",'{0:12} {1:8} {2:8} {3:8} {4:8}'.format(data[0], data[1], data[2], data[3], data[4]))

def StorageAdd(STORAGE_NAME,STORAGE_NODE,STORAGE_DEVICE,STORAGE_TYPE,STORAGE_PATH):
    LogInfo("OK","Storage added")
    vsql.SqlAddStorage([(STORAGE_NAME,STORAGE_NODE,STORAGE_DEVICE,STORAGE_TYPE,STORAGE_PATH)])    

def StorageInfo(STORAGE_NAME):
    datas = vsql.SqlPush("select * from storage where name='" + STORAGE_NAME + "'")
    print('{0:12} {1:8} {2:8} {3:8} {4:8}'.format("NAME","NODE","DEVICE","TYPE","PATH"))
    for data in datas:
        NODE_IP = vsql.SqlGetData("NODE_NAME","NODE_IP",data[1])
        if NODE_IP == None:	break
        DF = virty.SshInfoDir(NODE_IP,data[4])
        print('{0:12} {1:8} {2:8} {3:8} {4:8} {5:12} {6:4.0f} {7:4.0f} {8:4.0f} {9:4} {10:4}'
        .format(data[0], data[1], data[2], data[3], data[4], DF[0], int(DF[1])/1000000, int(DF[2])/1000000, int(DF[3])/1000000, DF[4], DF[5]))
    
def StorageXmlDump(NODE_NAME,STORAGE_NAME):
    print(virty.StoragepoolXmlDump(NODE_NAME,STORAGE_NAME))

def StorageMake(NODE_NAME,STORAGE_NAME,STORAGE_PATH):
    virty.StorageMake(NODE_NAME,STORAGE_NAME,STORAGE_PATH)

#Archive
def ArchiveInit(NAME):
    nodes = vsql.SqlGetAll("node")
    for node in nodes:
        ARCHIVE_DIR = vsql.SqlGetData("NODE_NAME","ARCHIVE_DIR",node[0])
        if ARCHIVE_DIR == None:
            LogInfo("Skip",node[0] + " archive storage dose not exits")
            break
        LogInfo("Info",node[0] + "  on  " + ARCHIVE_DIR)
        vansible.AnsibleFilecpTonode(node[1], setting.script_path + '/img/' + NAME + '.img', ARCHIVE_DIR + NAME + '.img')
        vsql.SqlAddArchive([(NAME,ARCHIVE_DIR + NAME + '.img',node[0])])
    
def ArchiveList():
    datas = vsql.SqlGetArchive()
    for data in datas:
        LogInfo("Archive","name: {0}     PATH: {1}    NODE: {2}".format(data[0], data[1], data[2]))
    


#Que
def QueList():
    datas = vsql.SqlGetAll("que")
    print('          {0:12} {1:8}'.format("NAME","NODE"))
    for data in datas:
        LogSuccess("QUE",'{0:12} {1:8}'.format(data[0], data[1]))



#DomainPool
def DomainpoolAdd():
    poollist = []
    pool_name = input("Enter the pool name:")
    pool_node_name = input("Enter the node name:")
    pool_setram = input("Enter the Set memory MB:")
    poollist.append([pool_name,pool_node_name,pool_setram])
    vsql.SqlAddDomainpool(poollist)

def DomainpoolAddLine(POOL_NAME,NODE_NAME,POOL_RAM):
    print([(POOL_NAME,NODE_NAME,POOL_RAM)])
    vsql.SqlAddDomainpool([(POOL_NAME,NODE_NAME,POOL_RAM)])

def DomainpoolList():
    pools = vsql.SqlGetDomainpool()
    poolnode = {}
    poolram = {}
    for pool in pools:
        KEY = pool[0]
        if KEY not in poolnode:
            poolnode[KEY] = []
            poolram[KEY] = 0
        RAM = int(poolram[KEY])
        RAMADD = int(pool[2])
        poolnode[KEY].append(pool[1])
        poolram[KEY] = str(RAM + RAMADD)
    for get in poolnode:
        LogInfo("List","name: {0}     node: {1}    memory: {2}".format(get, poolnode[get], poolram[get]))
    return poolnode

def DomainpoolFree(POOLNAME):
    domains = vsql.SqlGetAll("dom")
    poollist = vsql.SqlGetDomainpool()
    nodememory = {}
    for node in poollist:
        Key = node[1]
        if Key not in nodememory:
            nodememory[Key]=0
    for domain in domains:
        POOL = domain[5]
        Key = domain[2]
        if POOL == POOLNAME:
            nodememory[Key]=str(int(nodememory[Key])+int(domain[4]))
    print(nodememory)
    return max(nodememory)



#Network
def NetworkDefine(NODEIP):
    with open(setting.script_path + "/xml/temp_net.xml") as f:
        s = f.read()
        conn = libvirt.open('qemu+ssh://' + NODEIP + '/system')
        conn.networkDefineXML(s)

def NetworkMake(L2l_NAME,NODE_NAME,DOM_NAME):
    NODE_IP = vsql.SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
    datas = vsql.SqlHitL2less("NAMEtoDATA",L2l_NAME)
    for data in datas:
        vxml.XmlL2lessnetMake(data[0],data[2],data[1])
        vsql.SqlAddL2lesspool([(data[0],data[1],data[2],DOM_NAME,NODE_NAME)])
    VirtyNetDefine(NODE_IP)
    VirtyNetStart(L2l_NAME)

def NetworkDelete(l2l_NAME):
    l2l_NODE_NAME = vsql.SqlHitData("l2l_NAMEtol2l_NODE_NAME",l2l_NAME)
    l2l_NODE_IP = vsql.SqlHitData("NODE_NAMEtoNODE_IP",l2l_NODE_NAME)
    conn = libvirt.open('qemu+ssh://' + l2l_NODE_IP + '/system')
    con = conn.networkLookupByName(l2l_NAME)
    try: 
        con.undefine()
    except:
        LogError("NG",l2l_NAME + " catn't delete")
        exit(1)

def NetworkStart(l2l_NAME):
    l2l_NODE_NAME = vsql.SqlHitData("l2l_NAMEtol2l_NODE_NAME",l2l_NAME)
    l2l_NODE_IP = vsql.SqlHitData("NODE_NAMEtoNODE_IP",l2l_NODE_NAME)
    conn = libvirt.open('qemu+ssh://' + l2l_NODE_IP + '/system')
    con = conn.networkLookupByName(l2l_NAME)
    try:
        con.create()
    except:
        LogError("ERRO",l2l_NAME + " catn't start ")
        exit(1)
    LogSuccess("SUCC", l2l_NAME + " started")
    
def NetworkAdd(NETWORK_NAME,NETWORK_BRIDGE,NETWORK_NODE):
    LogInfo("OK","Network added")
    vsql.SqlAddNetwork([(NETWORK_NAME,NETWORK_BRIDGE,NETWORK_NODE)])  

  

#Network2l
def Network2l(ARCHIVE_NAME,DOM_NAME,NIC,MEMORY,CORE,DOMAINPOOL_NAME):
    NODE_NAME = VirtyDomainpoolFree(DOMAINPOOL_NAME)
    NODE_IP = vsql.SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
    ARCHIVE_PATH = vsql.SqlHitData("ARCHIVE_NAMEtoARCHIVE_PATH",ARCHIVE_NAME)
    VNC = str(VirtyVncFree(NODE_NAME))
    vsql.SqlAddDomain([(DOM_NAME,0,NODE_NAME,CORE,MEMORY,DOMAINPOOL_NAME)])
    vansible.AnsibleFilecpInnode(NODE_IP,ARCHIVE_PATH,'/kvm/dom/'+ DOM_NAME + '.img')
    vxml.XmlDomainMake(DOM_NAME,'/kvm/dom/'+ DOM_NAME + '.img',VNC,NIC,MEMORY,CORE)
    VirshDefine(NODE_IP)
    VirtyNetMake(NIC,NODE_NAME,DOM_NAME)

def Netwrok2lnetMake(L2L_NAME,NODE_NAME,GW_IP):
    NODE_IP = vsql.SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
    vxml.XmlL2lessnetMake(L2L_NAME,GW_IP,"None")
    VirtyNetDefine(NODE_IP)
    VirtyNetStart(L2l_NAME)



#Image
def ImageDelete(DOM_NAME):
    NODE_NAME = vsql.SqlGetData("DOM_NAME","NODE_NAME",DOM_NAME)
    NODE_IP = vsql.SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)

    LibvirtDomainDestroy(NODE_IP,DOM_NAME)

    vansible.AnsibleFiledeleteInnode(NODE_IP,"/kvm/dom/" + DOM_NAME + ".img")

def VirtyImgInit(IMG):
    nodes = vsql.SqlGetAll("node")
    for node in nodes:
        FileCpToNode(node[1], '../img/' + IMG + '.img', IMG + '.img')

def VirtyImgDeleteStatic(DOM_NAME):
    import xml.etree.ElementTree as ET 
    NODE_NAME = vsql.SqlGetData("DOM_NAME","NODE_NAME",DOM_NAME)
    NODE_IP = vsql.SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
    conn = libvirt.open('qemu+ssh://' + NODE_IP + '/system')
    con = conn.lookupByName(DOM_NAME)
    root = ET.fromstring(con.XMLDesc())
    for disk in root.find('devices').findall('disk'):
        if disk.get("device") == "disk":
            IMG_PATH = disk.find("source").get("file","none")
            LogInfo("INFO",IMG_PATH + "    @" + NODE_NAME)
            vansible.AnsibleFiledeleteInnode(NODE_IP,IMG_PATH)
    LogSuccess("OK","All deletions are complete")