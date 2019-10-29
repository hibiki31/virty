import libvirt, sys, sqlite3, subprocess, os
import vsql, vansible, vhelp,os, uuid
import xml.etree.ElementTree as ET


SPATH = '/root/virty/main'
SQLFILE = SPATH + '/data.sqlite'

def DomXmldump(DOM_NAME):
    NODE_NAME = vsql.SqlGetData("DOM_NAME","NODE_NAME",DOM_NAME)
    NODE_IP = vsql.SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
    conn = libvirt.open('qemu+ssh://' + NODE_IP + '/system')
    con = conn.lookupByName(DOM_NAME)
    return con.XMLDesc()


def DomainDefine(XML_DATA,NODE_IP):
    conn = libvirt.open('qemu+ssh://' + NODE_IP + '/system')
    conn.defineXML(XML_DATA)


class Libvirtc():

    def __init__(self,NODE_DOMAIN):
        self.node = libvirt.open('qemu+ssh://' + NODE_DOMAIN + '/system')

    def DomainOpen(self,DOMAIN_UUID):
        self.con = self.node.lookupByUUIDString(DOMAIN_UUID)
        self.domxml = ET.fromstring(self.con.XMLDesc())
        self.dpower = []
        self.dpower = self.con.state()[0]
        self.dautos = self.con.autostart()
        print(self.con.autostart())
        print(self.con.info())

        return self.con.XMLDesc()

    
    #Storage
    def StorageInfo(self,STORAGEP_NAME):
        pool = self.node.storagePoolLookupByName(STORAGEP_NAME)
        if pool == None:
            print('Failed to locate any StoragePool objects.', file=sys.stderr)
            exit(1)

        info = pool.info()

        print('Pool: '+pool.name())
        print('  UUID: '+pool.UUIDString())
        print('  Autostart: '+str(pool.autostart()))
        print('  Is active: '+str(pool.isActive()))
        print('  Is persistent: '+str(pool.isPersistent()))
        print('  Num volumes: '+str(pool.numOfVolumes()))
        print('  Pool state: '+str(info[0]))
        print('  Capacity: '+str(info[1]))
        print('  Allocation: '+str(info[2]))
        print('  Available: '+str(info[3]))

        print(pool.XMLDesc(0))

    def StorageList(self):
        pools = self.node.listAllStoragePools(0)
        if pools == None:
            print('Failed to locate any StoragePool objects.', file=sys.stderr)

        for pool in pools:
            info = pool.info()
            print('Pool: '+pool.name())
            print('  UUID: '+pool.UUIDString())
            print('  Autostart: '+str(pool.autostart()))
            print('  Is active: '+str(pool.isActive()))
            print('  Is persistent: '+str(pool.isPersistent()))
            print('  Num volumes: '+str(pool.numOfVolumes()))
            print('  Pool state: '+str(info[0]))
            print('  Capacity: '+str(round(int(info[1])/1000000000,1))+' GB')
            print('  Allocation: '+str(round(int(info[2])/1000000000,1))+' GB')
            print('  Available: '+str(round(int(info[3])/1000000000,1))+' GB')

    def ImageList(self,STORAGEP_NAME):
        pool = self.node.storagePoolLookupByName(STORAGEP_NAME)
        if pool == None:
            print('Failed to locate any StoragePool objects.', file=sys.stderr)
            exit(1)

        for image in pool.listVolumes():
            print(image)


    #Domain
    def DomainXmlDump(self): 
        return  [0,"domain","xmldump","Get domain xml",ET.tostring(self.domxml).decode()]

    def DomainNameEdit(self,NEW_NAME):
        self.domxml.findall('name')[0].text = NEW_NAME
        
    def DomainXmlUpdate(self):
        ET.tostring(self.domxml).decode()
        if self.dpower == 5:
            self.con.undefine()
            self.node.defineXML(ET.tostring(self.domxml).decode())
            return [0,"domain","define",""]
        else:
            return [1,"domain","define",""]

    def DomainPowerGet(self):
        if self.dpower == 5:
            return "SHT"
        else :
            return "RUN"
    
    def DomainDestroy(self):
        if self.dpower == 5:
            return [1,"domain","stop","Already stop domain",""]
        try:
            self.con.destroy()
        except:
            return [2,"domain","stop","Libvirt error",""]
        else:
            return [0,"domain","stop","Success destroy",""]

    def DomainShutdown(self):
        if self.dpower == 5:
            return [1,"domain","shutdown","Already shutdown domain",""]
        try:
            self.con.shutdown()
        except:
            return [2,"domain","shutdown","Libvirt error",""]
        else:
            return [0,"domain","shutdown","Success shutdown",""]

    def DomainPoweron(self):
        if self.dpower == 1:
            return [1,"domain","poweron","Already poweron domain",""]
        try:
            self.con.create()
        except:
            return [2,"domain","poweron","Libvirt error",""]
        else:
            return [0,"domain","poweron","Success poweron",""]

    def DomainAutostart(self):
        if self.dautos == 1:
            return [1,"domain","poweron","Already autostart domain",""]
        try:
            self.con.setAutostart(1)
        except:
            return [2,"domain","poweron","Libvirt error",""]
        else:
            return [0,"domain","poweron","Success autostart",""]

    def DomainNotautostart(self):
        if self.dautos == 0:
            return [1,"domain","poweron","Already autostart domain",""]
        try:
            self.con.setAutostart(0)
        except:
            return [2,"domain","poweron","Libvirt error",""]
        else:
            return [0,"domain","poweron","Success autostart",""]

    def DomainUndefine(self):
        if self.dpower == 1:
            return [2,"domain","poweron","Fail Undefine. because status is poweron",""]
        try:
            self.con.undefine()
        except:
            return [2,"domain","poweron","Libvirt error",""]
        else:
            return [0,"domain","poweron","Success Undefine",""]

    def AllDomainXmlPerth(self):
        DOMAINS = self.node.listAllDomains()
        PERTHDATA = []
        for domain in DOMAINS:
            DATA = ["","",""]
            DATA[2] = domain.XMLDesc()
            if domain.state()[0]==5:
                DATA[0]="SHT"
            else:
                DATA[0]="RUN"
            DATA[1] = domain.autostart()
            PERTHDATA.append((DATA))
        return PERTHDATA


    #Network
    def NetworkXmlTemplate(self,NETWORK_TEMPLATE):
        tree = ET.parse(NETWORK_TEMPLATE) 
        self.nxml = tree.getroot()

    def NetworkXmlL2lEdit(self,NAME,GW):
        self.nxml.findall('name')[0].text= NAME
        bridge = self.nxml.findall('bridge')[0]
        ip = self.nxml.findall('ip')[0]
        ip.set('address',GW)
        bridge.set('name',NAME)

    def NetworkXmlDefine(self,NODEIP):
        self.network = self.node.networkDefineXML(ET.tostring(self.nxml).decode())

    def NetworkXmlDump(self):
        return ET.tostring(self.nxml).decode()

    def NetworkStart(self):
        self.network.create()

    def DomainNicEdit(self,NOW_MAC,NEW_BRIDGE):
        source = NEW_BRIDGE
        devices = self.domxml.find('devices')
        for interface in devices.iter('interface'):
            if interface.find('mac').get('address') == NOW_MAC:
                interface.find('source').set('bridge', source)
                self.con.updateDeviceFlags(ET.tostring(interface).decode())
 
    def DomainNicShow(self):
        root = ET.fromstring(self.con.XMLDesc())
        self.nicdata = []
        for nic in root.find('devices').findall('interface'):
            TYPE = nic.get("type")
            MAC = nic.find("mac").get("address")
            if nic.find("target") == None:
                TARGET = "none"
            else:
                TARGET = nic.find("target").get("dev","none") 
            TO = nic.find("source").get("bridge")
            self.nicdata.append([TYPE,MAC,TARGET,TO])
        return self.nicdata

    def ShowSelinux(self):
        flag = 0
        for seclabel in self.domxml.findall('seclabel'):
            if seclabel.get('model','None') == 'selinux':
                print("selinuxis arrrr")
                flag = 1
            
        if flag == 1:
            return "on"
        else :
            return "off"

    def DeleteSelinux(self):
        for seclabel in self.domxml.findall('seclabel'):
            if seclabel.get('model','None') == 'selinux':
                self.domxml.remove(seclabel)


class Xmlc():
    def __init__(self,XML_STRING):
        self.xml = ET.fromstring(XML_STRING)

    def DomainData(self):
        DATA = {}
        DATA['name'] = self.xml.find('name').text
        DATA['memory'] = self.xml.find('memory').text
        DATA['memory-unit'] = self.xml.find('memory').get("unit")
        DATA['vcpu'] = self.xml.find('vcpu').text
        DATA['uuid'] = self.xml.find('uuid').text
        DATA['vnc'] = []
        DATA['disk'] = []
        DATA['interface'] = []

        vnc = self.xml.find('devices').find('graphics')        
    
        DATA['vnc'].append(vnc.get("port"))
        DATA['vnc'].append(vnc.get("autoport"))
        DATA['vnc'].append(vnc.get("listen"))
        DATA['vnc'].append(vnc.get("passwd", "none"))

        for disk in self.xml.find('devices').findall('disk'):
            if disk.find("source") is not None:
                DEVICE = disk.get("device")
                TYPE = disk.get("type")
                FILE = disk.find("source").get("file","none")
                TARGET =  disk.find("target").get("dev")
                DATA['disk'].append([DEVICE,TYPE,FILE,TARGET])
            else:
                DEVICE = disk.get("device")
                TYPE = disk.get("type")
                FILE = "Not Connect"
                TARGET = disk.find("target").get("dev")
                DATA['disk'].append([DEVICE,TYPE,FILE,TARGET])
        for nic in self.xml.find('devices').findall('interface'):
            TYPE = nic.get("type")
            MAC = nic.find("mac").get("address")
            TO = nic.find("source").get("bridge")

            if nic.find("target") == None:TARGET = "none"
            else:TARGET = nic.find("target").get("dev","none")
    
            DATA['interface'].append([TYPE,MAC,TARGET,TO])

        DATA['selinux'] = "off"
        for seclabel in self.xml.findall('seclabel'):
            if seclabel.get('model','None') == 'selinux':
                DATA['selinux']

        return DATA


def XmlGenMac():
    import random
    mac = [ 0x00, 0x16, 0x3e,
    random.randint(0x00, 0x7f),
    random.randint(0x00, 0xff),
    random.randint(0x00, 0xff) ]
    return( ':'.join(map(lambda x: "%02x" % x, mac)))

def XmlDomainBaseMake(DOM_NAME,MEMORY,CORE,VNC_PORT,VNC_PASS):
    os.chdir = SPATH

    tree = ET.parse(SPATH + '/xml/dom_base.xml') 
    root = tree.getroot()

    root.findall('name')[0].text = DOM_NAME
    root.find('memory').text = MEMORY
    root.find('currentMemory').text = MEMORY
    root.find('vcpu').text = CORE

    if VNC_PORT == "auto":
        root.find('devices').find('graphics').set('autoport', "yes")
        root.find('devices').find('graphics').set('port', "0")	
        #root.find('devices').find('graphics').set('passwd', "pass")	
    else:
        root.find('devices').find('graphics').set('autoport', "no")
        root.find('devices').find('graphics').set('port', VNC_PORT)
    
    tree.write(SPATH + '/define/' + DOM_NAME + '.xml')

def XmlBridgeNicAdd(DOM_NAME,SOURCE):
    os.chdir = SPATH

    MAC_ADDRESS = XmlGenMac()

    tree = ET.parse(SPATH + '/define/' + DOM_NAME + '.xml') 
    root = tree.getroot()

    interface = ET.SubElement(root.find('devices'), "interface")
    interface.set('type', 'bridge')
    ET.SubElement(interface, 'mac').set('address', MAC_ADDRESS)
    ET.SubElement(interface, 'source').set('bridge', SOURCE)
    ET.SubElement(interface, 'model').set('type', 'virtio')
    
    # address = ET.SubElement(interface, 'address')
    # address.set('bus', '0x00')
    # address.set('domain', '0x0000')
    # address.set('function', '0x0')
    # address.set('slot', '0x03')
    # address.set('type', 'pci')

    tree.write(SPATH + '/define/' + DOM_NAME + '.xml')

def XmlL2lessnetMake(l2l_NAME,l2l_GW,l2l_IP):
    tree = ET.parse(SPATH + '/xml/net_l2less.xml') 
    root = tree.getroot()
    ## L1
    root.findall('name')[0].text= l2l_NAME
    bridge = root.findall('bridge')[0]
    ip = root.findall('ip')[0]
    ## L2
    ip.set('address',l2l_GW)
    bridge.set('name',l2l_NAME)
    # ## L3
    # dhcp = ip.findall('dhcp')[0]
    # ## L4
    # rangex = dhcp.findall('range')[0]
    # rangex.set('start',l2l_IP)
    # rangex.set('end',l2l_IP)

    tree.write(SPATH + '/define/' + l2l_NAME + '.xml')

def XmlImgAdd(DOM_NAME,STORAGE_PATH,IMG_NAME,STORAGE_NAME,ARCHIVE_NAME):
    os.chdir = SPATH

    IMG_PATH = STORAGE_PATH + DOM_NAME + IMG_NAME + '.img'

    tree = ET.parse(SPATH + '/define/' + DOM_NAME + '.xml') 
    root = tree.getroot()

    disk = ET.SubElement(root.find('devices'), "disk")
    disk.set('type', 'file')
    disk.set('device', 'disk')
    driver = ET.SubElement(disk, 'driver')
    source = ET.SubElement(disk, 'source')
    target = ET.SubElement(disk, 'target')
    address = ET.SubElement(disk, 'address')
    driver.set('name','qemu')
    driver.set('type','qcow2')
    source.set('file',IMG_PATH)
    target.set('dev','vda')
    target.set('bus','virtio')
    address.set('bus', '0x00')
    address.set('domain', '0x0000')
    address.set('function', '0x0')
    address.set('slot', '0x04')
    address.set('type', 'pci')
    
    tree.write(SPATH + '/define/' + DOM_NAME + '.xml')

    vsql.SqlAddImg([(IMG_NAME,ARCHIVE_NAME,DOM_NAME,"none")])

def XmlMetaSetStorage(DOM_NAME,STORAGE_NAME,ARCHIVE_NAME):
    os.chdir = SPATH
    tree = ET.parse(SPATH + '/define/' + DOM_NAME + '.xml') 
    root = tree.getroot()

    storage = ET.SubElement(root.find('metadata'), "storage")
    storage.set('storage',STORAGE_NAME)
    storage.set('archive',ARCHIVE_NAME)

    tree.write(SPATH + '/define/' + DOM_NAME + '.xml')