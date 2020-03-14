import sys, sqlite3, subprocess, os
import xml.etree.ElementTree as ET
import libvirt, pings
import vsql, vansible, vhelp,os, uuid


SPATH = '/root/virty/main'
SQLFILE = SPATH + '/data.sqlite'


class VirtEditor():
    def __init__(self,NODE_DOMAIN):
        self.nodeip = NODE_DOMAIN
        self.node = libvirt.open('qemu+ssh://' + NODE_DOMAIN + '/system')


    ############################
    # OPEN                     #
    ############################
    def DomainOpen(self,DOMAIN_UUID):
        self.con = self.node.lookupByUUIDString(DOMAIN_UUID)
        self.domxml = ET.fromstring(self.con.XMLDesc())
        self.dompower = self.con.state()[0]
        self.domauto = self.con.autostart()
        self.domuuid = DOMAIN_UUID

    def NetworkOpen(self,NET_UUID):
        self.network = self.node.networkLookupByUUIDString(NET_UUID)
        self.netpower = self.network.isActive()
        self.netauto = self.network.autostart()
        self.netxml = ET.fromstring(self.network.XMLDesc())
    
    def StorageXml(self,STORAGE_NAME):
        return self.node.storagePoolLookupByName(STORAGE_NAME).XMLDesc()


    ############################
    # DEFINE                   #
    ############################
    def StorageDefine(self,XML_DUMP):
        try:
            sp = self.node.storagePoolDefineXML(XML_DUMP,0)
        except:
            pass
        else:
            sp.create()
            if sp.autostart() == True:
                sp.setAutostart(0)
            else:
                sp.setAutostart(1)
                
    def StorageUndefine(self,STORAGE_NAME):
        try:
            sp = self.node.storagePoolLookupByName(STORAGE_NAME)
        except:
            pass
        else:
            print(sp.info())
            if sp.info()[0] == 2:
                sp.destroy()
            sp.undefine()
            return ["success","storagepool","undefine","Success Undefine",""]
                
    def DomainUndefine(self):
        if self.dompower == 1:
            return ["error","domain","poweron","Fail Undefine. because status is poweron",""]
        try:
            self.con.undefine()
        except:
            return ["skip","domain","poweron","Libvirt error",""]
        else:
            return ["success","domain","poweron","Success Undefine",""]                

    def NetworkUndefine(self):
        if self.netpower == 1:
            self.network.destroy()
        try:
            self.network.undefine()
        except:
            return ["error","network","undefine","Libvirt error",""]
        else:
            return ["error","network","undefine","Success Undefine",""]                


    ############################
    # INFO                     #
    ############################
    def DomainInfo(self):
        editor = XmlEditor("root",self.domxml)
        editor.DumpSave("dom")
        data = editor.DomainData()
        data['power'] = self.dompower
        data['autostart'] = self.domauto
        return data

    def NetInfo(self):
        editor = XmlEditor("root",self.netxml)
        editor.DumpSave("net")
        data = editor.DomainData()
        data['power'] = self.dompower
        data['autostart'] = self.domauto
        return data

    def StorageInfo(self,STORAGEP_NAME):
        pool = self.node.storagePoolLookupByName(STORAGEP_NAME)
        if pool == None:
            print('Failed to locate any StoragePool objects.', file=sys.stderr)
            exit(1)
        pool.refresh()
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

    def ImageInfo(self,STORAGEP_NAME,IMG_NAME):
        pool = self.node.storagePoolLookupByName(STORAGEP_NAME)
        if pool == None:
            print('Failed to locate any StoragePool objects.', file=sys.stderr)
            exit(1)

        image = pool.storageVolLookupByName(IMG_NAME)
        info = image.info()
        print('    Type: '+str(info[0]))
        print('    Capacity: '+str(info[1]))
        print('    Allocation: '+str(info[2]))


    ############################
    # ALL LSIT                 #
    ############################
    def StorageList(self):
        pools = self.node.listAllStoragePools(0)
        if pools == None:
            print('Failed to locate any StoragePool objects.', file=sys.stderr)

        for pool in pools:
            pool.refresh()
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


    ############################
    # ALL XML                  #
    ############################
    def AllStorageXml(self):
        pools = self.node.listAllStoragePools(0)
        if pools == None:
            print('Failed to locate any StoragePool objects.', file=sys.stderr)
        data = []
        for pool in pools:
            pool.refresh()
            data.append(pool.XMLDesc())
        return data
    
    def AllImageXml(self,STORAGEP_NAME):
        pool = self.node.storagePoolLookupByName(STORAGEP_NAME)
        if pool == None:
            print('Failed to locate any StoragePool objects.', file=sys.stderr)
            exit(1)
        pool.refresh()

        xmllist = []
        for imagename in pool.listVolumes():
            image = pool.storageVolLookupByName(imagename)
            xmllist.append(image.XMLDesc())
        return xmllist

    def DomainAllData(self):
        if self.node == None:
            return
        domains = self.node.listAllDomains()
        DATA = []
        for domain in domains:
            temp = {}
            temp['status'] = domain.state()[0]
            temp['auto'] = domain.autostart()
            temp['xml'] = domain.XMLDesc()
            DATA.append(temp)
        return DATA

    def StorageAllData(self):
        pools = self.node.listAllStoragePools(0)
        if pools == None:
            print('Failed to locate any StoragePool objects.', file=sys.stderr)
        data = []
        for pool in pools:
            pool.refresh()
            temp = {}
            temp['active'] = pool.isActive()
            temp['auto'] = pool.autostart()
            temp['status'] = pool.info()[0]
            temp['xml'] = pool.XMLDesc(0)
            temp['image'] = []
            for image in pool.listAllVolumes():
                xmledit = XmlEditor("str",image.XMLDesc())
                temp['image'].append(xmledit.ImageData())
            data.append(temp)
        return data

    def NetworkAllData(self):
        networks = self.node.listAllNetworks()
        data = []
        for net in networks:
            temp = {}
            temp['xml'] = net.XMLDesc()
            temp['status'] = net.isActive()
            temp['auto'] = net.autostart()
            data.append(temp)
        return data

    ############################
    # XML                  #
    ############################
    def DomainXmlPerth(self,DOM_UUID):
        if self.node == None:
            return
        domain = self.node.lookupByUUIDString(DOM_UUID)
        DATA = ["","",""]
        DATA[2] = domain.XMLDesc()
        DATA[0]= domain.state()[0]
        DATA[1] = domain.autostart()
        return DATA


    ############################
    # DELETE                   #
    ############################
    def ImageDelete(self,STORAGEP_NAME,IMG_NAME):
        pool = self.node.storagePoolLookupByName(STORAGEP_NAME)
        if pool == None:
            print('Failed to locate any StoragePool objects.', file=sys.stderr)
            exit(1)

        image = pool.storageVolLookupByName(IMG_NAME)
        image.delete()



    ############################
    # EDIT                     #
    ############################
    def DomainNameEdit(self,NEW_NAME):
        self.domxml.findall('name')[0].text = NEW_NAME
        
    def DomainMemoryEdit(self,NEW_MEM):
        self.domxml.find('memory').text = NEW_MEM
        self.domxml.find('memory').set('unit',"MiB")
        self.domxml.find('currentMemory').text = NEW_MEM
        self.domxml.find('currentMemory').set('unit',"MiB")
        
    def DomainCpuEdit(self,NEW_CPU):
        self.domxml.find('vcpu').text = NEW_CPU

    def DomainSelinuxEdit(self):
        for seclabel in self.domxml.findall('seclabel'):
            if seclabel.get('model','None') == 'selinux':
                self.domxml.remove(seclabel)


    ############################
    # UPDATE                   #
    ############################
    def DomainXmlUpdate(self):
        ET.tostring(self.domxml).decode()
        if self.dompower == 5:
            self.con.undefine()
            self.node.defineXML(ET.tostring(self.domxml).decode())
            return ["success","domain","name-edit","Success domain name edit",""]
        else:
            return ["success","domain","name-edit","domain started",""]

    def DomainPowerGet(self):
        if self.dompower == 5:
            return "SHT"
        else :
            return "RUN"
    

    ############################
    # STATUS                   #
    ############################
    def DomainDestroy(self):
        if self.dompower == 5:
            return ["error","domain","stop","Already stop domain",""]
        try:
            self.con.destroy()
        except:
            return ["skip","domain","stop","Libvirt error",""]
        else:
            self.dompower = self.con.state()[0]
            return ["success","domain","stop","Success destroy",""]

    def DomainShutdown(self):
        if self.dompower == 5:
            return ["error","domain","shutdown","Already shutdown domain",""]
        try:
            self.con.shutdown()
            self.dompower = self.con.state()[0]
        except:
            return ["skip","domain","shutdown","Libvirt error",""]
        else:
            return ["success","domain","shutdown","Success shutdown",""]

    def DomainPoweron(self):
        if self.dompower == 1:
            return ["error","domain","poweron","Already poweron domain",""]
        try:
            self.con.create()
            self.dompower = self.con.state()[0]
        except:
            return ["skip","domain","poweron","Libvirt error",""]
        else:
            return ["success","domain","poweron","Success poweron",""]

    def DomainAutostart(self,STATUS):
        if STATUS == "off":
            if self.domauto == 1:
                return ["error","domain","poweron","Already autostart domain",""]
            try:
                self.con.setAutostart(1)
                self.domauto = self.con.autostart()
            except:
                return ["skip","domain","poweron","Libvirt error",""]
            else:
                return ["success","domain","poweron","Success autostart",""]
        elif STATUS == "on":
            if self.domauto == 0:
                return ["error","domain","poweron","Already autostart domain",""]
            try:
                self.con.setAutostart(0)
                self.domauto = self.con.autostart()
            except:
                return ["skip","domain","poweron","Libvirt error",""]
            else:
                return ["success","domain","poweron","Success autostart",""]


    def NetworkXmlTemplate(self,NETWORK_TEMPLATE):
        tree = ET.parse(NETWORK_TEMPLATE) 
        self.nxml = tree.getroot()

    def NetworkDHCP(self):
        return self.network.DHCPLeases()

    def NetworkXmlL2lEdit(self,NAME,GW):
        self.nxml.find('name').text= NAME
        ip = self.nxml.find('ip').set('address',GW)
    

    def NetworkXmlDefine(self,NODEIP):
        self.network = self.node.networkDefineXML(ET.tostring(self.nxml).decode())

    def NetworkDefine(self,XML):
        self.network = self.node.networkDefineXML(XML)

    def NetworkXmlDump(self):
        return ET.tostring(self.nxml).decode()

    def NetworkStart(self):
        self.network.create()



    def NetworkList(self):
        test = []
        for net in self.node.listNetworks():
            temp = self.node.networkLookupByName(net)
            test.append({'name':temp.name(),'uuid':temp.UUIDString(),'bridge':temp.bridgeName()})
        return test
    
    def InterfaceList(self):
        return self.node.listInterfaces()
        
    def NetworkXmlRootAll(self):
        test = []
        for net in self.node.listNetworks():
            temp = self.node.networkLookupByName(net)
            test.append(ET.fromstring(temp.XMLDesc()))
        return test


    def DomainEditNicNetwork(self,NOW_MAC,NEW_BRIDGE):
        source = NEW_BRIDGE
        devices = self.domxml.find('devices')
        for interface in devices.iter('interface'):
            if interface.find('mac').get('address') == NOW_MAC:
                interface.set('type','network')
                interface.find('source').set('network', source)
                self.con.updateDeviceFlags(ET.tostring(interface).decode())

    def DomainCdromEdit(self,TARGET,ISO_PATH):
        devices = self.domxml.find('devices')
        for disk in devices.iter('disk'):
            if disk.get('device') == "cdrom":
                if disk.find('target').get('dev') == TARGET:
                    if disk.find('source') == None:
                        ET.SubElement(disk, 'source') 
                    disk.find('source').set('file', ISO_PATH)
                    self.con.updateDeviceFlags(ET.tostring(disk).decode())

    def DomainCdromExit(self,TARGET):
        devices = self.domxml.find('devices')
        for disk in devices.iter('disk'):
            if disk.get('device') == "cdrom":
                if disk.find('target').get('dev') == TARGET:
                    cdrom = disk.find('source')
                    if cdrom == None:
                        ET.SubElement(disk, 'source')
                    disk.remove(cdrom)
                    self.con.updateDeviceFlags(ET.tostring(disk).decode())                    

 
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




class XmlEditor():
    def __init__(self,TYPE,XML):
        if TYPE == "file":
            os.chdir = SPATH
            tree = ET.parse(SPATH + '/xml/'+ XML +'.xml') 
            root = tree.getroot()
            self.xml = root
        elif TYPE == "dom":
            os.chdir = SPATH
            tree = ET.parse(SPATH + '/dump/dom/'+ XML +'.xml') 
            root = tree.getroot()
            self.xml = root
        elif TYPE == "net":
            os.chdir = SPATH
            tree = ET.parse(SPATH + '/dump/net/'+ XML +'.xml') 
            root = tree.getroot()
            self.xml = root
        elif TYPE == "str":
            root = ET.fromstring(XML)
            self.xml = root

    ############################
    # DATA                     #
    ############################
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
        DATA['boot'] = []

        DATA['memory'] = UnitConvertor(DATA['memory-unit'],"M",DATA['memory'])
        DATA['memory-unit'] = "G"

        Count = 1
        for boot in self.xml.find('os').findall('boot'):
            DATA['boot'].append([Count,boot.get('dev')])
            Count = Count + 1
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

            if TYPE == "bridge":
                TO = nic.find("source").get("bridge")
            else:
                TO = nic.find("source").get("network")

            if nic.find("target") == None:TARGET = "none"
            else:TARGET = nic.find("target").get("dev","none")
    
            DATA['interface'].append([TYPE,MAC,TARGET,TO])

        DATA['selinux'] = "off"
        for seclabel in self.xml.findall('seclabel'):
            if seclabel.get('model','None') == 'selinux':
                DATA['selinux']

        return DATA

    def NetworkData(self):
        DATA = {}
        DATA['name'] = self.xml.find('name').text
        DATA['uuid'] = self.xml.find('uuid').text
       
        DATA['ip'] = []
        DATA['dhcp'] = []

        if self.xml.find('ip') is not None:
            DATA['ip'].append(self.xml.find('ip').get("address",None))
            DATA['ip'].append(self.xml.find('ip').get("netmask",None))
            if self.xml.find('ip').find('dhcp') is not None:
                DHCP_START = self.xml.find('ip').find('dhcp').find('range').get("start",None)
                DHCP_END = self.xml.find('ip').find('dhcp').find('range').get("end",None)
                DATA['dhcp'].append([DHCP_START,DHCP_END])

        DATA['bridge'] = self.xml.find('bridge').get("name")

        if self.xml.find('mac') is not None:
            DATA['mac'] = self.xml.find('mac').get("address",None)
        else:
            DATA['mac'] = None

        if self.xml.find('forward') is not None:
            DATA['forward'] = self.xml.find('forward').get("mode")
        else:
            DATA['forward'] = None

        if DATA['forward'] == "nat":
            DATA['type'] = "NAT"
        elif DATA['forward'] == None:
            DATA['type'] = "internal"
        elif DATA['forward'] == "bridge":
            DATA['type'] = "Bridge"
        else:
            DATA['type'] = "unknown"
        
        return DATA

    def ImageData(self):
        DATA = {}
        if not self.xml.get("type") == "file":
            return "dir"
        DATA['name'] = self.xml.find('name').text

        DATA['capacity-unit'] = self.xml.find('capacity').get("unit")
        DATA['capacity'] = self.xml.find('capacity').text
        DATA['allocation-unit'] = self.xml.find('allocation').get("unit")
        DATA['allocation'] = self.xml.find('allocation').text
        DATA['physical-unit'] = self.xml.find('physical').get("unit")
        DATA['physical'] = self.xml.find('physical').text

        DATA['capacity'] = UnitConvertor(DATA['capacity-unit'],"G",DATA['capacity'])
        DATA['capacity-unit'] = "G"
        DATA['allocation'] = UnitConvertor(DATA['allocation-unit'],"G",DATA['allocation'])
        DATA['allocation-unit'] = "G"
        DATA['physical'] = UnitConvertor(DATA['physical-unit'],"G",DATA['physical'])
        DATA['physical-unit'] = "G"
        
        DATA['path'] = self.xml.find('target').find('path').text

        return DATA

    def StorageData(self):
        DATA = {}
        DATA['name'] = self.xml.find('name').text
        DATA['uuid'] = self.xml.find('uuid').text

        DATA['capacity-unit'] = self.xml.find('capacity').get("unit")
        DATA['capacity'] = self.xml.find('capacity').text
        DATA['allocation-unit'] = self.xml.find('allocation').get("unit")
        DATA['allocation'] = self.xml.find('allocation').text
        DATA['available-unit'] = self.xml.find('available').get("unit")
        DATA['available'] = self.xml.find('available').text

        DATA['capacity'] = UnitConvertor(DATA['capacity-unit'],"G",DATA['capacity'])
        DATA['capacity-unit'] = "G"
        DATA['allocation'] = UnitConvertor(DATA['allocation-unit'],"G",DATA['allocation'])
        DATA['allocation-unit'] = "G"
        DATA['available'] = UnitConvertor(DATA['available-unit'],"G",DATA['available'])
        DATA['available-unit'] = "G"
        
        DATA['path'] = self.xml.find('target').find('path').text

        return DATA

    ############################
    # EDIT                     #
    ############################
    def EditNetworkInternal(self,NAME):
        self.xml.find('name').text= NAME

    def EditNetworkBridge(self,NAME,Bridge):
        self.xml.find('name').text= NAME
        self.xml.find('forward').set('mode','bridge')
        self.xml.find('bridge').set('name',Bridge)

    def EditDomainBase(self,DOM_NAME,MEMORY,CORE,VNC_PORT,VNC_PASS):
        self.xml.findall('name')[0].text = DOM_NAME
        self.xml.find('memory').text = MEMORY
        self.xml.find('currentMemory').text = MEMORY
        self.xml.find('vcpu').text = CORE

        if VNC_PORT == "auto":
            self.xml.find('devices').find('graphics').set('autoport', "yes")
            self.xml.find('devices').find('graphics').set('port', "0")	
        else:
            self.xml.find('devices').find('graphics').set('autoport', "no")
            self.xml.find('devices').find('graphics').set('port', VNC_PORT) 

        if not VNC_PASS == "":
            self.xml.find('devices').find('graphics').set('passwd', VNC_PASS)




    def EditDomainEmulator(self,DOM_EMU):
        if DOM_EMU == "debian":
            self.xml.find('devices').find('emulator').text = "/usr/bin/kvm"
            self.xml.find('os').find('type').set('machine', "pc-i440fx-2.8")
        elif DOM_EMU == "rhel fedora":
            self.xml.find('devices').find('emulator').text = "/usr/libexec/qemu-kvm"
            self.xml.find('os').find('type').set('machine', "pc-i440fx-rhel7.0.0")

    def EditDomainImageMeta(self,STORAGE_NAME,ARCHIVE_NAME):
        ET.SubElement(self.xml.find('metadata'), "storage")
        self.xml.find('metadata').find('storage').set('storage',STORAGE_NAME)
        self.xml.find('metadata').find('storage').set('archive',ARCHIVE_NAME)

    def EditStorageBase(self,STORAGE_NAME,STORAGE_PATH):
        self.xml.find('name').text = STORAGE_NAME
        self.xml.find('target').find('path').text = STORAGE_PATH

    ############################
    # ADD                      #
    ############################
    def AddDomainImage(self,IMG_PATH):
        disk = ET.SubElement(self.xml.find('devices'), "disk")
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

    def AddDomainNetwork(self,NET_NAME):
        MAC_ADDRESS = MacGen()
        add = ET.SubElement(self.xml.find('devices'), "interface")
        add.set('type', 'network')
        ET.SubElement(add, 'mac').set('address', MAC_ADDRESS)
        ET.SubElement(add, 'source').set('network', NET_NAME)
        ET.SubElement(add, 'model').set('type', 'virtio')

    ############################
    # DUMP                     #
    ############################
    def DumpSave(self,TYPE):
        os.chdir = SPATH
        DOM_UUID = self.xml.find('uuid').text
        ET.ElementTree(self.xml).write(SPATH + '/dump/' +TYPE+ '/' + DOM_UUID + '.xml')

    def DumpStr(self):
        return ET.tostring(self.xml).decode()


############################
# OTHER                    #
############################
def ping(IP):
    p = pings.Ping().ping(IP).is_reached()
    print(p)

def UnitConvertor(EC,DC,DATA):
    if EC == "bytes":
        if DC == "G":
            DATA = float(DATA)/1024
            DATA = float(DATA)/1024
            DATA = float(DATA)/1024
            return round(DATA,1)
    if EC == "KiB":
        if DC == "M":
            DATA = float(DATA)/1024
            return round(DATA,1)

def MacGen():
    import random
    mac = [ 0x00, 0x16, 0x3e,
    random.randint(0x00, 0x7f),
    random.randint(0x00, 0xff),
    random.randint(0x00, 0xff) ]
    return( ':'.join(map(lambda x: "%02x" % x, mac)))