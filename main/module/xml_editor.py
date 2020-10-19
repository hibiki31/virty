import os

import xml.etree.ElementTree as ET

from module import setting

class XmlEditor():
    def __init__(self,TYPE,XML):
        if TYPE == "file":
            os.chdir = setting.script_path
            tree = ET.parse(setting.script_path + '/xml/'+ XML +'.xml') 
            root = tree.getroot()
            self.xml = root
        elif TYPE == "dom":
            os.chdir = setting.script_path
            tree = ET.parse(setting.script_path + '/dump/dom/'+ XML +'.xml') 
            root = tree.getroot()
            self.xml = root
        elif TYPE == "net":
            os.chdir = setting.script_path
            tree = ET.parse(setting.script_path + '/dump/net/'+ XML +'.xml') 
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

        DATA['memory'] = unit_convertor(DATA['memory-unit'],"M",DATA['memory'])
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
                SOURCE = nic.find("source").get("bridge")
            else:
                SOURCE = nic.find("source").get("network")

            NETWORK = nic.find("source").get("network",None)
            if NETWORK != None:
                TYPE = "network"

            if nic.find("target") == None:
                TARGET = "none"
            else:
                TARGET = nic.find("target").get("dev","none")
    
            DATA['interface'].append([TYPE,MAC,TARGET,SOURCE,NETWORK])

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

        DATA['capacity'] = unit_convertor(DATA['capacity-unit'],"G",DATA['capacity'])
        DATA['capacity-unit'] = "G"
        DATA['allocation'] = unit_convertor(DATA['allocation-unit'],"G",DATA['allocation'])
        DATA['allocation-unit'] = "G"
        DATA['physical'] = unit_convertor(DATA['physical-unit'],"G",DATA['physical'])
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

        DATA['capacity'] = unit_convertor(DATA['capacity-unit'],"G",DATA['capacity'])
        DATA['capacity-unit'] = "G"
        DATA['allocation'] = unit_convertor(DATA['allocation-unit'],"G",DATA['allocation'])
        DATA['allocation-unit'] = "G"
        DATA['available'] = unit_convertor(DATA['available-unit'],"G",DATA['available'])
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
        MAC_ADDRESS = macaddress_generator()
        add = ET.SubElement(self.xml.find('devices'), "interface")
        add.set('type', 'network')
        ET.SubElement(add, 'mac').set('address', MAC_ADDRESS)
        ET.SubElement(add, 'source').set('network', NET_NAME)
        ET.SubElement(add, 'model').set('type', 'virtio')

    ############################
    # DUMP                     #
    ############################
    def DumpSave(self,TYPE):
        os.chdir = setting.script_path
        DOM_UUID = self.xml.find('uuid').text
        ET.ElementTree(self.xml).write(setting.script_path + '/dump/' +TYPE+ '/' + DOM_UUID + '.xml')

    def DumpStr(self):
        return ET.tostring(self.xml).decode()


def get_domain_info(domain_uuid):
    os.chdir = setting.script_path
    try:
        tree = ET.parse(setting.script_path + '/dump/dom/'+ domain_uuid +'.xml') 
    except:
        return None
    root = tree.getroot()

    DATA = {}
    DATA['name'] = root.find('name').text
    DATA['memory'] = root.find('memory').text
    DATA['memoryUnit'] = root.find('memory').get("unit")

    DATA['memory'] = unit_convertor(DATA['memoryUnit'],"M",DATA['memory'])
    DATA['memoryUnit'] = "M"

    DATA['vcpu'] = root.find('vcpu').text
    DATA['uuid'] = root.find('uuid').text

    vnc = root.find('devices').find('graphics')        
    DATA['vncPort'] = vnc.get("port")
    DATA['vncPortIsAuto'] = vnc.get("autoport")
    DATA['vncAllowHost'] = vnc.get("listen")
    DATA['vncPassword'] = vnc.get("passwd", None)

    DATA['selinux'] = "off"
    for seclabel in root.findall('seclabel'):
        if seclabel.get('model','None') == 'selinux':
            DATA['selinux']


    DATA['boot'] = []
    DATA['disk'] = []
    DATA['interface'] = []


    Count = 1
    for boot in root.find('os').findall('boot'):
        DATA['boot'].append({
            "order":Count,
            "device":boot.get('dev')
            })
        Count = Count + 1
    

    for disk in root.find('devices').findall('disk'):
        if disk.find("source") is not None:
            DEVICE = disk.get("device")
            TYPE = disk.get("type")
            FILE = disk.find("source").get("file","none")
            TARGET =  disk.find("target").get("dev")
        else:
            DEVICE = disk.get("device")
            TYPE = disk.get("type")
            FILE = None
            TARGET = disk.find("target").get("dev")
        DATA['disk'].append({
                "deviceType":DEVICE,
                "fileType":TYPE,
                "filePath":FILE,
                "terget":TARGET
                })


    for nic in root.find('devices').findall('interface'):
        TYPE = nic.get("type")
        MAC = nic.find("mac").get("address")

        if TYPE == "bridge":
            SOURCE = nic.find("source").get("bridge")
        else:
            SOURCE = nic.find("source").get("network")

        NETWORK = nic.find("source").get("network",None)
        if NETWORK != None:
            TYPE = "network"

        if nic.find("target") == None:
            TARGET = "none"
        else:
            TARGET = nic.find("target").get("dev","none")

        DATA['interface'].append({
            'type':TYPE,
            'macAddress':MAC,
            'terget':TARGET,
            'source':SOURCE,
            'network':NETWORK
        })

    

    return DATA


    
def unit_convertor(EC,DC,DATA):
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

def macaddress_generator():
    import random
    mac = [ 0x00, 0x16, 0x3e,
    random.randint(0x00, 0x7f),
    random.randint(0x00, 0xff),
    random.randint(0x00, 0xff) ]
    return( ':'.join(map(lambda x: "%02x" % x, mac)))