import os

import xml.etree.ElementTree as ET

from mixin.settings import virty_root
from module.model import AttributeDict

from storage.schemas import ImageRaw

class XmlEditor():
    def __init__(self, type, obj):
        """
        パーサに複数の手段でxml_rootを渡す

        Parameters
        ----------
        type : str
            file, dom, net, str
        """
        if type == "static":
            os.chdir = virty_root
            tree = ET.parse(virty_root + 'static/xml/'+ obj +'.xml') 
            root = tree.getroot()
            self.xml = root
        elif type == "dom":
            os.chdir = virty_root
            tree = ET.parse(virty_root + 'data/xml/domain/'+ obj +'.xml') 
            root = tree.getroot()
            self.xml = root
        elif type == "net":
            os.chdir = virty_root
            tree = ET.parse(virty_root + '/dump/net/'+ obj +'.xml') 
            root = tree.getroot()
            self.xml = root
        elif type == "str":
            root = ET.fromstring(obj)
            self.xml = root


    def storage_pase(self):
        """
        ストレージのXMLをパースする
        Returns
        -------
        AttributeDict()
        """

        data = AttributeDict()
        
        data.name = self.xml.find('name').text
        data.uuid = self.xml.find('uuid').text
        data.capacity = self.xml.find('capacity').text
        data.capacity_unit = self.xml.find('capacity').get("unit")
        data.allocation_unit = self.xml.find('allocation').get("unit")
        data.allocation = self.xml.find('allocation').text
        data.available_unit = self.xml.find('available').get("unit")
        data.available = self.xml.find('available').text

        data.capacity = unit_convertor(data.capacity_unit, "G", data.capacity)
        data.capacity_unit = "G"
        data.allocation = unit_convertor(data.allocation_unit, "G", data.allocation)
        data.allocation_unit = "G"
        data.available = unit_convertor(data.available_unit, "G", data.available)
        data.available_unit = "G"
        
        data.path = self.xml.find('target').find('path').text

        return data
    
    def image_pase(self):
        """
        イメージのXMLをパースする
        Returns
        -------
        AttributeDict()
        """

        data = ImageRaw(
            name = self.xml.find('name').text,
            capacity = unit_convertor( self.xml.find('capacity').get("unit"), "G",  self.xml.find('capacity').text),
            allocation = unit_convertor( self.xml.find('allocation').get("unit"), "G",  self.xml.find('allocation').text),
            capacity_unit = "G",
            allocation_unit = "G",
            path = self.xml.find('target').find('path').text
        )

        return data
    
    def network_pase(self):
        data = {}
        data['name'] = self.xml.find('name').text
        data['uuid'] = self.xml.find('uuid').text
       
        data['ip'] = []
        data['dhcp'] = []

        if self.xml.find('ip') is not None:
            data['ip'].append(self.xml.find('ip').get("address",None))
            data['ip'].append(self.xml.find('ip').get("netmask",None))
            if self.xml.find('ip').find('dhcp') is not None:
                DHCP_START = self.xml.find('ip').find('dhcp').find('range').get("start",None)
                DHCP_END = self.xml.find('ip').find('dhcp').find('range').get("end",None)
                data['dhcp'].append([DHCP_START,DHCP_END])

        data['bridge'] = self.xml.find('bridge').get("name")

        if self.xml.find('mac') is not None:
            data['mac'] = self.xml.find('mac').get("address",None)
        else:
            data['mac'] = None

        if self.xml.find('forward') is not None:
            data['forward'] = self.xml.find('forward').get("mode")
        else:
            data['forward'] = None

        if data['forward'] == "nat":
            data['type'] = "NAT"
        elif data['forward'] == None:
            data['type'] = "internal"
        elif data['forward'] == "bridge":
            data['type'] = "Bridge"
        else:
            data['type'] = "unknown"
        
        return data


    def domain_emulator_edit(self, os_like):
        if os_like == "debian":
            self.xml.find('devices').find('emulator').text = "/usr/bin/kvm"
            self.xml.find('os').find('type').set('machine', "pc-i440fx-2.8")
        elif os_like == "rhel fedora":
            self.xml.find('devices').find('emulator').text = "/usr/libexec/qemu-kvm"
            self.xml.find('os').find('type').set('machine', "pc-i440fx-rhel7.0.0")
        
    
    def domain_base_edit(self, domain_name, memory_mega_byte, core, vnc_port:int=None, vnc_passwd=None):
        self.xml.findall('name')[0].text = domain_name
        self.xml.find('memory').text = str(memory_mega_byte)
        self.xml.find('currentMemory').text = str(memory_mega_byte)
        self.xml.find('vcpu').text = str(core)

        if vnc_port == 0:
            self.xml.find('devices').find('graphics').set('autoport', "yes")
            self.xml.find('devices').find('graphics').set('port', "0")	
        elif vnc_port > 0:
            self.xml.find('devices').find('graphics').set('autoport', "no")
            self.xml.find('devices').find('graphics').set('port', vnc_port) 

        if vnc_passwd != None:
            self.xml.find('devices').find('graphics').set('passwd', VNC_PASS)

    def domain_interface_add(self, network_name, mac_address=None):
        if mac_address == None:
            mac_address = macaddress_generator()
    
        add_interface = ET.SubElement(self.xml.find('devices'), "interface")
        add_interface.set('type', 'network')
        ET.SubElement(add_interface, 'mac').set('address', mac_address)
        ET.SubElement(add_interface, 'source').set('network', network_name)
        ET.SubElement(add_interface, 'model').set('type', 'virtio')
    
    def domain_device_image_add(self,image_path, target_device):
        disk = ET.SubElement(self.xml.find('devices'), "disk")
        disk.set('type', 'file')
        disk.set('device', 'disk')
        driver = ET.SubElement(disk, 'driver')
        source = ET.SubElement(disk, 'source')
        target = ET.SubElement(disk, 'target')
        address = ET.SubElement(disk, 'address')
        driver.set('name','qemu')
        driver.set('type','qcow2')
        source.set('file',image_path)
        target.set('dev',target_device)
        target.set('bus','virtio')
        address.set('bus', '0x00')
        address.set('domain', '0x0000')
        address.set('function', '0x0')
        address.set('slot', '0x04')
        address.set('type', 'pci')

    def dump_str(self):
        return ET.tostring(self.xml).decode()

    ############################
    # DATA                     #
    ############################
    def domain_parse(self):
        DATA = {}
        DATA['name'] = self.xml.find('name').text
        DATA['memory'] = self.xml.find('memory').text
        DATA['memory-unit'] = self.xml.find('memory').get("unit")
        DATA['vcpu'] = self.xml.find('vcpu').text
        DATA['uuid'] = self.xml.find('uuid').text
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
    
        DATA['vnc_port'] = vnc.get("port")
        # DATA['vnc'].append(vnc.get("autoport"))
        # DATA['vnc'].append(vnc.get("listen"))
        # DATA['vnc'].append(vnc.get("passwd", "none"))

        for disk in self.xml.find('devices').findall('disk'):
            if disk.find("source") is not None:
                DATA['disk'].append({
                    "device": disk.get("device"),
                    "type": disk.get("type"),
                    "file": disk.find("source").get("file","none"),
                    "target": disk.find("target").get("dev")
                })
            else:
                DATA['disk'].append({
                    "device": disk.get("device"),
                    "type": disk.get("type"),
                    "file": None,
                    "target": disk.find("target").get("dev")
                })
            
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
    
            DATA['interface'].append({
                "type":TYPE,
                "mac":MAC,
                "target":TARGET,
                "source":SOURCE,
                "network":NETWORK
                })

        DATA['selinux'] = "off"
        for seclabel in self.xml.findall('seclabel'):
            if seclabel.get('model','None') == 'selinux':
                DATA['selinux']

        return DATA
    
    def dump_file(self,type):
        xml_dir = virty_root + 'data/xml/' +type+ '/'
        os.chdir = virty_root
        os.makedirs(xml_dir, exist_ok=True)
        uuid = self.xml.find('uuid').text
        ET.ElementTree(self.xml).write(xml_dir + uuid + '.xml')

class XMLOLD():

    
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
    

    def DumpStr(self):
        return ET.tostring(self.xml).decode()


def get_domain_info(domain_uuid):
    os.chdir = virty_root
    try:
        tree = ET.parse(virty_root + '/dump/dom/'+ domain_uuid +'.xml') 
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