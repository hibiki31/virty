#!/bin/python3
import libvirt
import sys
import sqlite3
import subprocess
import os
import time
import concurrent.futures
import pprint
import json
from module import vsql, vansible, vhelp, virtlib, vsh, setting
from module import model
import bcrypt



def hash_password(password, rounds=12):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds)).decode()


def check_password(hashed_password, user_password):
    return bcrypt.checkpw(user_password.encode(), hashed_password.encode())


class AttributeDict(object):
    def __init__(self, obj):
        if type(obj) != dict:
            raise 
        self.obj = obj

    ### Pickle
    def __getstate__(self):
        return self.obj.items()

    ### Pickle
    def __setstate__(self, items):
        if not hasattr(self, 'obj'):
            self.obj = {}
        for key, val in items:
            self.obj[key] = val

    ### Class["key"] = "val"
    def __setitem__(self, key, val):
        self.obj[key] = val

    ### Class["key"]
    def __getitem__(self, name):
        if name in self.obj:
            return self.obj.get(name)
        else:
            return None
    
    def get(self,name):
        if name in self.obj:
            return self.obj.get(name)
        else:
            return None

    ### Class.name
    def __getattr__(self, name):
        if name in self.obj:
            return self.obj.get(name)
        else:
            return None

    ### dict互換
    def keys(self):
        return self.obj.keys()

    ### dict互換
    def values(self):
        return self.obj.values()
    
    def dump(self):
        return json.dumps(self.obj)

class AttributeJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, AttributeDict): # NotSettedParameterは'NotSettedParameter'としてエンコード
            return o.obj
        return super(AttributeJsonEncoder, self).default(o) # 他の型はdefaultのエンコード方式を使用

def attribute_args_convertor(args):
    data = {}
    for i in args.keys():
        if args.getlist(i) == [""]:
            data[i] = None
        elif len(args.getlist(i)) == 1:
            data[i] = args.get(i)
        else:
            data[i] = args.getlist(i)
        
    return AttributeDict(data)

def attribute_args_dump(attribute_dict):
    return json.dumps(attribute_dict, cls=AttributeJsonEncoder)

#Worker
def WorkerStatus():
    p1 = subprocess.Popen(["ps", "-ef"], shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p2 = subprocess.Popen(["grep", setting.script_path + "/module/vworker.py"], stdin=p1.stdout, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
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
    p2 = subprocess.Popen(["grep", setting.script_path + "/module/vworker.py"], stdin=p1.stdout, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p3 = subprocess.Popen(["grep", "python"], stdin=p2.stdout, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p4 = subprocess.Popen(["wc", "-l"], stdin=p3.stdout, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p1.stdout.close()
    p2.stdout.close()
    p3.stdout.close()
    output = p4.communicate()[0].decode("utf8").replace('\n','')
    if int(output) == 0:
        print("Worker up")
        subprocess.Popen(["python3", setting.script_path + "/module/vworker.py"])
    else:
        print("Worker upped")

def Queuing(QUE_OBJECT,QUE_METHOD,que_dic):
    return vsql.Queuing(QUE_OBJECT,QUE_METHOD,que_dic.dump())




#Domain Power
def DomainStart(domain_uuid):
    if domain_uuid == None:
        return ["error","sql","get","Domain name not found",""]
    NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",domain_uuid)
    NODE_STATUS = vsql.Convert("NODE_NAME","NODE_STATUS",NODE_NAME)
    if not NODE_STATUS == 10:
        return ["skip","node","status","Node is not active",""]
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    manager = virtlib.VirtEditor(NODE_IP)
    manager.DomainOpen(domain_uuid)
    result = manager.DomainPoweron()

    return result

def DomainShutdown(domain_uuid):
    if domain_uuid == None:
        return ["error","sql","get","Domain name not found",""]
    NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",domain_uuid)
    NODE_STATUS = vsql.Convert("NODE_NAME","NODE_STATUS",NODE_NAME)
    if not NODE_STATUS == 10:
        return ["skip","node","status","Node is not active",""]
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)
    
    manager = virtlib.VirtEditor(NODE_IP)
    manager.DomainOpen(domain_uuid)
    result = manager.DomainShutdown()

    return result
    
def DomainDestroy(domain_uuid):
    if domain_uuid == None:
        return ["error","sql","get","Domain name not found",""]
    NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",domain_uuid)
    NODE_STATUS = vsql.Convert("NODE_NAME","NODE_STATUS",NODE_NAME)
    if not NODE_STATUS == 10:
        return ["skip","node","status","Node is not active",""]
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    manager = virtlib.VirtEditor(NODE_IP)
    manager.DomainOpen(domain_uuid)
    result = manager.DomainDestroy()

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

    manager = virtlib.VirtEditor(NODE_IP)
    manager.DomainOpen(DOM_UUID)
    result = manager.DomainAutostart(1)

    manager.DomainOpen(DOM_UUID)
    data = manager.DomainInfo()
    
    data['node-name'] = NODE_NAME
    data['node-ip'] = NODE_IP

    vsql.SqlUpdateDomain(data)
    print(data)

    return result

def DomainUndefine(DOM_UUID):
    if DOM_UUID == None:
        return ["error","sql","get","Domain name not found",""]
    NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
    NODE_STATUS = vsql.Convert("NODE_NAME","NODE_STATUS",NODE_NAME)
    if not NODE_STATUS == 10:
        return ["skip","node","status","Node is not active",""]
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    editor = virtlib.VirtEditor(NODE_IP)
    editor.DomainOpen(DOM_UUID)

    vsql.RawCommit("delete from domain where uuid=?",[DOM_UUID])

    return editor.DomainUndefine()





def DomainListInit():
    NODE_DATAS = vsql.SqlGetAll("node")

    vsql.DataStatusIsUpdating("domain_interface")
    vsql.DataStatusIsUpdating("domain_drive")
    for NODE in NODE_DATAS:
        if int(NODE[8]) == 20:#Maintenance
            vsql.DomainStatusUpdate([NODE[0]],[],7)
            continue
        elif int(NODE[8]) > 20:#Error
            vsql.DomainStatusUpdate([NODE[0]],[],20)
            continue
        try:
            manager = virtlib.VirtEditor(NODE[1])
        except:
            vsql.NodeStatusUpdate([NODE[0]],50)
            vsql.DomainStatusUpdate([NODE[0]],[],20)
            continue

        send = []
        pool = []
        datas = manager.StorageAllData()
        # vsql.RawCommit("delete from img where node=?",[(NODE[0])])
        for data in datas:
            editor = virtlib.XmlEditor("str",data['xml'])
            editor.DumpSave("storage")
            temp = editor.StorageData()
            temp['node'] = NODE[0]
            temp['device'] = "none"
            temp['type'] = "none"
            for image in data['image']:
                if type(image) == dict:
                    pool.append([image['name'], NODE[0], temp['name'], image['capacity'], image['allocation'], image['physical'], image['path']])
            send.append(temp)
        vsql.ImageAdd(pool)
        vsql.UpdateStorage(send)

        send = []
        datas = manager.DomainAllData()
        for data in datas:
            editor = virtlib.XmlEditor("str",data['xml'])
            temp = editor.DomainData()
            for interface in temp['interface']:
                interface.insert(0,temp['uuid'])
                vsql.DomainInterfaceAdd(interface)
            for disk in temp['disk']:
                disk.insert(0,temp['uuid'])
                vsql.DomainDriveAdd(disk)
            temp['node-name'] = NODE[0]
            temp['node-ip'] = NODE[1]
            temp['power'] = data['status']
            temp['autostart'] = data['auto']
            send.append((temp['name'], temp['power'],temp['node-name'],temp['vcpu'],temp['memory'],temp['uuid'],"unknown","unknown"))
            editor.DumpSave("dom")
        vsql.DomainStatusUpdate([NODE[0]],[],10)
        vsql.SqlAddDomain(send)

        send = []
        datas = manager.NetworkAllData()
        for data in datas:
            editor = virtlib.XmlEditor("str",data['xml'])
            editor.DumpSave("net")
            temp = editor.NetworkData()
            temp['node'] = NODE[0]
            send.append(temp)
        vsql.NetworkAdd(send)
    vsql.DataStatusDelete("domain_interface")
    vsql.DataStatusDelete("domain_drive")
    return ["success","domain list init"]
        
   
def UserAdd(USER_ID,PASSWORD):
    SQL = "insert into users (id,password) values (?,?)"
    DATA = [USER_ID,PASSWORD]
    vsql.RawCommit(SQL,DATA)


def UserReset(USER_ID,PASSWORD):
    SQL = "update users set password=? where id=?"
    DATA = [PASSWORD,USER_ID]
    vsql.RawCommit(SQL,DATA)


def userIsExist(USER_ID):
    if vsql.RawFetchall("select * from users where id=?",[USER_ID]) == []:
        return False
    else:
        return True


def groupIsExist(GROUP_ID):
    if vsql.RawFetchall("select * from groups where id=?",[GROUP_ID]) == []:
        return False
    else:
        return True


def GetNicData(DOM_UUID):
    NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    editor = virtlib.VirtEditor(NODE_IP)
    editor.DomainOpen(DOM_UUID)

    return editor.DomainNicShow()

def DomainData(DOM_UUID):
    NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    editor = virtlib.XmlEditor("dom",DOM_UUID)

    data = editor.DomainData()
    data['node-name'] = NODE_NAME
    data['node-ip'] = NODE_IP

    return data

############################
# Storage                  #
############################
def StorageListAll():
    NODE_DATAS = vsql.SqlGetAll("node")
    data = []
    for NODE in NODE_DATAS:
        try:
            editor = virtlib.VirtEditor(NODE[1])
        except:
            continue
        xmls = editor.AllStorageXml()
        for xml in xmls:
            xmledit = virtlib.XmlEditor("str",xml)
            get = xmledit.StorageData()
            get['node'] = NODE[0]
            get['device'] = "none"
            get['type'] = "none"
            data.append(get)
    vsql.UpdateStorage(data)
    return data



def StorageList(NODE_NAME):
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)
    editor = virtlib.VirtEditor(NODE_IP)
    xmls = editor.AllStorageXml()
    data = []
    for xml in xmls:
        xmledit = virtlib.XmlEditor("str",xml)
        get = xmledit.StorageData()
        get['node'] = NODE_NAME
        data.append(get)
    return data

def StoragepoolXmlDump(NODE_NAME,STORAGE_NAME):
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)
    editor = virtlib.VirtEditor(NODE_IP)
    return editor.StorageXml(STORAGE_NAME)

def StorageMake(NODE_NAME,STORAGE_NAME,STORAGE_PATH):
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    editor = virtlib.XmlEditor("file","storage_dir")
    editor.EditStorageBase(STORAGE_NAME,STORAGE_PATH)

    server = virtlib.VirtEditor(NODE_IP)
    server.StorageDefine(editor.DumpStr())

def StorageUndefine(NODE_NAME,STORAGE_NAME):
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    server = virtlib.VirtEditor(NODE_IP)
    server.StorageUndefine(STORAGE_NAME)

    return [0,"storage","undefine","Success",""]




#Image
def ImageList(NODE_NAME,STORAGEP_NAME):
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    editor = virtlib.VirtEditor(NODE_IP)
    editor.ImageList(STORAGEP_NAME)



def queueLogErr(ID):
    with open(setting.script_path+"/log/queue_"+ID+"_err.log") as f:
        return f.read()

def queueLogOut(ID):
    with open(setting.script_path+"/log/queue_"+ID+"_out.log") as f:
        return f.read()


def ImageInfo(NODE_NAME,STORAGEP_NAME,IMG_NAME):
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    editor = virtlib.VirtEditor(NODE_IP)
    editor.ImageInfo(STORAGEP_NAME,IMG_NAME)    

def ImageListXml(NODE_NAME,STORAGEP_NAME):
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)
    editor = virtlib.VirtEditor(NODE_IP)
    xmls = editor.AllImageXml(STORAGEP_NAME)
    data = []
    for xml in xmls:
        xmledit = virtlib.XmlEditor("str",xml)
        data.append(xmledit.ImageData())
    return data


def ImageDelete(NODE_NAME,STORAGEP_NAME,IMG_NAME):
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    editor = virtlib.VirtEditor(NODE_IP)
    editor.ImageDelete(STORAGEP_NAME,IMG_NAME)
    vsql.RawCommit("delete from img where node=? and pool=? and name=?",(NODE_NAME,STORAGEP_NAME,IMG_NAME))


def ImageIsoList(NODE_NAME):
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    image = []
    nodepoint = virtlib.VirtEditor(NODE_IP)
    images = nodepoint.AllImageXml("iso")

    for xml in images:
        imageedit = virtlib.XmlEditor("str",xml)
        image.append(imageedit.ImageData())
    return image

def ImageArchiveList(NODE_NAME):
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    image = []
    nodepoint = virtlib.VirtEditor(NODE_IP)
    images = nodepoint.AllImageXml("archive")

    for xml in images:
        imageedit = virtlib.XmlEditor("str",xml)
        image.append(imageedit.ImageData())
    return image

def ImageArchiveListAll():
    NODE_DATAS = vsql.SqlGetAll("node")
    image = []
    for NODE in NODE_DATAS:
        try:
            nodepoint = virtlib.VirtEditor(NODE[1])
        except:
            continue
        images = nodepoint.AllImageXml("archive")
        for xml in images:
            imageedit = virtlib.XmlEditor("str",xml)
            data = imageedit.ImageData()
            data['node'] = NODE[0]
            image.append(data)
    return image

#Node
def NodeAdd(NODE_NAME,NODE_IP):
    try:
        MEM = SshInfoMem(NODE_IP)
        CORE = SshInfocpu(NODE_IP)
        CPU = SshInfocpuname(NODE_IP)
        OS = SshOsinfo(NODE_IP)
        QEMU = SshInfoQemu(NODE_IP)
        VIRT = SshInfoLibvirt(NODE_IP)
    except Exception as e:
        return ["error","node","add",str(e)]

    DATA = [NODE_NAME,NODE_IP,MEM,CORE,CPU,OS['NAME'],OS['VERSION'],OS['ID_LIKE'],10,QEMU,VIRT]
    SQL = "replace into node (name, ip, memory, core, cpugen, os_name, os_version, os_like, status, qemu, libvirt) values (?,?,?,?,?,?,?,?,?,?,?)"
    vsql.RawCommit(SQL,DATA)
    vansible.AnsibleNodelistInit()
    return ["success","node","add","Succes"]


def node_delete(node_name):
    print("delete node: ",node_name)
    sql = "delete from node where name=?"
    model.raw_commit(sql,[node_name])
    
    sql = "delete from domain where node_name=?"
    model.raw_commit(sql,[node_name])

    sql = "delete from network where node=?"
    model.raw_commit(sql,[node_name])

    sql = "delete from storage where node_name=?"
    model.raw_commit(sql,[node_name])

    sql = "delete from archive_img where node=?"
    model.raw_commit(sql,[node_name])

    sql = "delete from img where node=?"
    model.raw_commit(sql,[node_name])

    return ["success", "Success"]


def NetworkXmlSaveAll():
    NODE_DATAS = vsql.SqlGetAll("node")
    for NODE in NODE_DATAS:
        try:
            manager = virtlib.VirtEditor(NODE[1])
        except:
            continue
        if manager.node == None:
            print("cont "+NODE[0])
            continue
        xmls = manager.NetworkXmlRootAll()
        for xml in xmls:
            editor = virtlib.XmlEditor("root",xml)
            editor.DumpSave("net")



def NetworkDHCP(NODE_NAME,NET_UUID):
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)
    manager = virtlib.VirtEditor(NODE_IP)
    if manager.node == None:
        print("cont "+NET_UUID)
        return 1
    manager.NetworkOpen(NET_UUID)
    editor = virtlib.XmlEditor("root",manager.netxml)
    return editor.NetworkData()
    

def NetworkInternalDefine(NODE_NAME,NET_NAME):
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    editor = virtlib.XmlEditor("file","net_internal")
    editor.EditNetworkInternal(NET_NAME)

    manager = virtlib.VirtEditor(NODE_IP)
    manager.NetworkDefine(editor.DumpStr())
    manager.NetworkStart()

def NetworkBridgeDefine(NODE_NAME,NET_NAME,BRIDGE):
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    editor = virtlib.XmlEditor("file","net_bridge")
    editor.EditNetworkBridge(NET_NAME,BRIDGE)

    manager = virtlib.VirtEditor(NODE_IP)
    manager.NetworkDefine(editor.DumpStr())
    manager.NetworkStart()

def Network2lDefine(NODE_IP,XML_PATH,NAME,GW):
    editor = virtlib.VirtEditor(NODE_IP)
    editor.NetworkXmlTemplate(XML_PATH)

    print(editor.NetworkXmlDump())
    editor.NetworkXmlL2lEdit(NAME,GW)
    print(editor.NetworkXmlDump())
    editor.NetworkXmlDefine(NODE_IP)
    editor.NetworkStart()

    

def NetworkUndefine(NET_UUID):
    NODE_DATAS = vsql.SqlGetAll("node")
    for NODE in NODE_DATAS:
        editor = virtlib.VirtEditor(NODE[1])
        editor.NetworkOpen(NET_UUID)
        editor.NetworkUndefine()
    





def InterfaceList(NODE_NAME):
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)
    editor = virtlib.VirtEditor(NODE_IP)

    return editor.InterfaceList()

def AllInterfaceList():
    NODE_DATAS = vsql.SqlGetAll("node")
    data = []
    for NODE in NODE_DATAS:
        editor = virtlib.VirtEditor(NODE[1])
        temp = {}
        temp['node'] = NODE[0]
        temp['network'] = editor.InterfaceList()
        data.append(temp)
    return data

def NodeNetworkList(NODE_NAME):
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)
    editor = virtlib.VirtEditor(NODE_IP)
    data = [editor.InterfaceList()]
    data.append(editor.NetworkList())
    return data

def NodeNetworkAllList():
    NODE_DATAS = vsql.SqlGetAll("node")
    data = []
    for NODE in NODE_DATAS:
        temp = {}
        editor = virtlib.VirtEditor(NODE[1])
        temp['int'] = editor.InterfaceList()
        temp['net'] = editor.NetworkList()
        temp['node'] = NODE[0]
        data.append(temp)
    return data


def DomainDefineStatic(defineData):
    ### name,node,memory,cpu,archive,pool,nic[],type,size

    domainName = defineData['name']

    nodeName = defineData['node']
    nodeIp = vsql.SqlGetData("NODE_NAME","NODE_IP",nodeName)
    nodeData = vsql.SqlGetData("NODE_NAME","NODE_DATA",nodeName)
    nodeEmulator = nodeData[5]

    manager = virtlib.VirtEditor(nodeIp)
   
    editor = virtlib.XmlEditor("file","dom_base")
    editor.EditDomainEmulator(nodeEmulator)
    editor.EditDomainBase(defineData['name'],defineData['memory'],defineData['cpu'],"auto","")
    
    if not "networks" in defineData:
        defineData['networks'] = []
    elif type(defineData['networks']) == str:
        defineData['networks'] = [defineData['networks']]
    
    for network in defineData['networks']:
        editor.AddDomainNetwork(network)

    imgDevice = ["vda","vdb","vdc"]
    imgData = virtlib.XmlEditor("str",manager.StorageXml(defineData['pool'])).StorageData()
    imgPath = imgData['path'] +"/"+ domainName + "_" + imgDevice[0] + '.img'

    editor.AddDomainImage(imgPath)
    

    if defineData['type'] == "archive":
        archiveImg = vsql.RawFetchall("select * from archive_img where archive_id=?",[defineData['archive']])[0]
        archivePath = vsql.RawFetchall("select path from img where node=? and pool=? and name=?",[archiveImg[2],archiveImg[3],archiveImg[1]])[0][0]
        vansible.AnsibleFilecpInnode(nodeIp,archivePath,imgPath)
    elif defineData['type'] == "empty":
        SshQemuCreate(nodeIp,imgPath,defineData['disk-size'])
    
    else:
        return ["error","domain","define",]

    manager.node.defineXML(editor.DumpStr())




def DomainDefineStaticOld(DOM_DIC):
    NODE_NAME = DOM_DIC['node']
    DOM_NAME = DOM_DIC['name']
    NODE_IP = vsql.SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
    NODE_DATA = vsql.SqlGetData("NODE_NAME","NODE_DATA",NODE_NAME)

    node = virtlib.VirtEditor(NODE_IP)

    editor = virtlib.XmlEditor("file","dom_base")

    editor.EditDomainEmulator(NODE_DATA[5])
    editor.EditDomainBase(DOM_DIC['name'],DOM_DIC['memory'],DOM_DIC['cpu'],"auto","")
    editor.EditDomainImageMeta(DOM_DIC['storage'],DOM_DIC['archive'])
    print(DOM_DIC['nic'])

    for network in DOM_DIC['nic']:
        editor.AddDomainNetwork(network[1])
        print(network[1])

    IMG_DEVICE_NAME = ["vda","vdb","vdc"]
    COUNTER = 0
    storages = editor.xml.find('metadata').findall('storage')

    for storage in storages:
        IMG_NAME = IMG_DEVICE_NAME[COUNTER]
        COUNTER = COUNTER + 1
        STORAGE_NAME = storage.get('storage')
        ARCHIVE_NAME = storage.get('archive')

        ARCHIVE_POOL_DATA = virtlib.XmlEditor("str",node.StorageXml("archive")).StorageData()
        STORAGE_POOL_DATA = virtlib.XmlEditor("str",node.StorageXml(STORAGE_NAME)).StorageData()
        
        ARCHIVE_PATH = ARCHIVE_POOL_DATA['path'] + "/" + ARCHIVE_NAME
        IMG_PATH = STORAGE_POOL_DATA['path'] +"/"+ DOM_NAME + "_" + IMG_NAME + '.img'

        editor.AddDomainImage(IMG_PATH)
        vansible.AnsibleFilecpInnode(NODE_IP,ARCHIVE_PATH,IMG_PATH)

    conn = libvirt.open('qemu+ssh://' + NODE_IP + '/system')
    print(editor.DumpStr())
    conn.defineXML(editor.DumpStr())


############################
# Domain-Edit              #
############################
def DomNameEdit(DOM_UUID,NEW_NAME):
    NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    editor = virtlib.VirtEditor(NODE_IP)
    editor.DomainOpen(DOM_UUID)
    editor.DomainNameEdit(NEW_NAME)
    vsql.DomainDelete(DOM_UUID)
    return editor.DomainXmlUpdate()

def DomSelinux(DOM_UUID):
    NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    editor = virtlib.VirtEditor(NODE_IP)
    editor.DomainOpen(DOM_UUID)

    return editor.ShowSelinux()

def DomSelinuxDisable(DOM_UUID):
    NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    editor = virtlib.VirtEditor(NODE_IP)
    editor.DomainOpen(DOM_UUID)

    editor.DomainSelinuxEdit()
    return editor.DomainXmlUpdate()

def DomainEditNicNetwork(DOM_UUID,NOW_MAC,NEW_NIC):
    NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    editor = virtlib.VirtEditor(NODE_IP)
    editor.DomainOpen(DOM_UUID)
    editor.DomainEditNicNetwork(NOW_MAC,NEW_NIC)

def DomCdromExit(DOM_UUID,TARGET):
    NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    editor = virtlib.VirtEditor(NODE_IP)
    editor.DomainOpen(DOM_UUID)
    editor.DomainCdromExit(TARGET)

def DomCdromEdit(DOM_UUID,TARGET,ISO_PATH):
    NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    editor = virtlib.VirtEditor(NODE_IP)
    editor.DomainOpen(DOM_UUID)
    editor.DomainCdromEdit(TARGET,ISO_PATH)

def DomainEditMemory(DOM_UUID,NEW_MEMORY):
    NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    editor = virtlib.VirtEditor(NODE_IP)
    editor.DomainOpen(DOM_UUID)
    editor.DomainMemoryEdit(NEW_MEMORY)
    return editor.DomainXmlUpdate()

def DomainEditCpu(DOM_UUID,NEW_CPU):
    NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

    editor = virtlib.VirtEditor(NODE_IP)
    editor.DomainOpen(DOM_UUID)
    editor.DomainCpuEdit(NEW_CPU)
    return editor.DomainXmlUpdate()




############################
# SSH                      #
############################
def SshInfoMem(user, domain, port):
    cmd = ["ssh" , user+"@"+domain ]
    cmd.extend(["sudo", "cat /proc/meminfo |grep MemTotal"])
    print(cmd)
    mem = subprocess.check_output(cmd)
    words = float(str(mem).split()[1])
    memory = words/1024000
    return memory

def SshInfocpu(user, domain, port):
    cmd = ["ssh" , user+"@"+domain ]
    cmd.extend(["sudo", "grep processor /proc/cpuinfo | wc -l"])
    words = str(subprocess.check_output(cmd)).rstrip("\\n'").lstrip("'b")
    return words

def SshInfoLibvirt(user, domain, port):
    cmd = ["ssh" , user+"@"+domain ]
    cmd.extend(["sudo", "virsh version --daemon|grep libvirt|grep Using"])
    try:
        version = str(subprocess.check_output(cmd))
    except:
        return "error"
    return version.rstrip("\\n'").lstrip("'b").split()[3]
    
def SshInfoQemu(user, domain, port):
    cmd = ["ssh" , user+"@"+domain ]
    cmd.extend(["sudo", "virsh version --daemon|grep hypervisor:"])
    try:
        version = str(subprocess.check_output(cmd))
    except:
        return "error"
    return version.rstrip("\\n'").lstrip("'b").split()[3]

def SshInfocpuname(user, domain, port):
    cmd = ["ssh" , user+"@"+domain ]
    cmd.extend(["sudo", "grep 'model name' /proc/cpuinfo|uniq"])
    mem = subprocess.check_output(cmd)
    words = str(mem).split(":")[1].rstrip("\\n'")
    return words

def SshInfoDir(NODE_IP,NODE_DIR):
    cmd = ["ssh" , user+"@"+domain ]
    cmd.extend(["sudo", "df" ,NODE_DIR,"|sed -e '1d'"])
    get = subprocess.check_output(cmd)
    storage = str(get).rstrip("\\n'").lstrip("b'").split()
    return storage

def SshOsinfo(user, domain, port):
    cmd = ["ssh" , user+"@"+domain ]
    cmd.extend(["sudo", "cat" ,"/etc/os-release"])
    get = subprocess.check_output(cmd)
    result = {}
    for data in str(get).rstrip("\\n'").lstrip("b'").split("\\n"):
        if not data == "":
            result[data.split("=")[0]] = data.split("=")[1].strip("\"")
    return result

def SshQemuCreate(NODE_IP,PATH,SIZE):
    cmd = ["ssh" , user+"@"+domain ]
    cmd.extend(["sudo", "test -e" ,PATH,"; echo $?"])
    get = subprocess.check_output(cmd)
    if get.decode("UTF-8").splitlines()[0] == "1":
        cmd = ["ssh" , NODE_IP, "sudo", "qemu-img create -f qcow2 " ,PATH, SIZE+"G"]
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

def SshQemuResize(NODE_IP,PATH,SIZE):
    cmd = ["ssh" , user+"@"+domain ]
    cmd.extend(["sudo", "test -e" ,PATH,"; echo $?"])
    get = subprocess.check_output(cmd)
    if get.decode("UTF-8").splitlines()[0] == "0":
        cmd = ["ssh" , NODE_IP,  "sudo", "qemu-img resize " ,PATH, SIZE+"G"]
        try:
            create = subprocess.check_output(cmd)
        except Exception as e:
            return ["error","img","resize","fail", str(e)]
        if create.decode("UTF-8").splitlines()[0].split(" ")[0] == "Formatting" or True:
            return ["success","img","resize","Success",""]
        else:
            return ["error","img","resize","fail",create.decode("UTF-8")]
    else:
        return ["skip","img","resize","image not found",""]

def ImageResize(NODE,POOL,FILE,SIZE):
    NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE)
    imagelist = ImageListXml(NODE,POOL)
    for image in imagelist:
        if image['name'] == FILE:
            return SshQemuResize(NODE_IP,image['path'],SIZE)

if __name__ == "__main__":
    args = sys.argv
    argnum = len(args)
    if argnum == 1:
        argobj = "none"
    else:
        argobj = args[1]


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