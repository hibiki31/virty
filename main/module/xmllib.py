import os
from statistics import mode
from uuid import uuid4

import xml.etree.ElementTree as ET

from sqlalchemy import false

from settings import APP_ROOT
from mixin.log import setup_logger
from module.model import AttributeDict

from storage.schemas import ImageRaw
from domain.schemas import *


logger = setup_logger(__name__)


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
            os.chdir = APP_ROOT
            tree = ET.parse(APP_ROOT + '/static/xml/'+ obj +'.xml') 
            root = tree.getroot()
            self.xml = root
        elif type == "domain":
            os.chdir = APP_ROOT
            tree = ET.parse(APP_ROOT + '/data/xml/domain/'+ obj +'.xml') 
            root = tree.getroot()
            self.xml = root
        elif type == "network":
            os.chdir = APP_ROOT
            tree = ET.parse(APP_ROOT + '/data/xml/network/'+ obj +'.xml') 
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
        logger.debug("ストレージのパースを開始")

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
        
        if target := self.xml.find('target'):
            data.path = target.find('path').text
        else:
            data.path = ""

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

        # タイプ判定
        if self.xml.find('forward') is not None:
            mode = self.xml.find('forward').get("mode")
            data['type'] = mode
            try:
                if self.xml.find('virtualport').get("type") == "openvswitch":
                    data['type'] = "openvswitch"
            except:
                pass
        else:
            data['type'] = "internal"

        # ブリッジ先
        data['bridge'] = self.xml.find('bridge').get("name")
        
        # MACアドレス
        try:
            data['mac'] = self.xml.find('mac').get("address",None)
        except:
            data['mac'] = None

        # IP関係
        if self.xml.find('ip') is not None:
            data['ip'] = []
            data['dhcp'] = []
            data['mac'] = None
            data['ip'].append(self.xml.find('ip').get("address",None))
            data['ip'].append(self.xml.find('ip').get("netmask",None))
            if self.xml.find('ip').find('dhcp') is not None:
                DHCP_START = self.xml.find('ip').find('dhcp').find('range').get("start",None)
                DHCP_END = self.xml.find('ip').find('dhcp').find('range').get("end",None)
                data['dhcp'].append([DHCP_START,DHCP_END])
        else:
            data['ip'] = None
            data['dhcp'] = None

        # OpenVswith
        if data['type'] == 'openvswitch':
            data['portgroup'] = []
            for portgroup in self.xml.findall('portgroup'):
                try:
                    vlan_id = portgroup.find('vlan').find('tag').get('id')
                except:
                    vlan_id = None
                data['portgroup'].append({
                    'name': portgroup.get("name"),
                    'isDefault': True if portgroup.get("default") == "yes" else False,
                    'vlanId': vlan_id
                })

        else:
            data['portgroup'] = None

        return data

    def network_ovs_find(self, name):
        for portgroup in self.xml.findall('portgroup'):
            if portgroup.get("name") == name:
                return ET.tostring(portgroup).decode()


    def domain_emulator_edit(self, os_like):
        if os_like == "Debian":
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
    
    def domain_uuid_generate(self, domain_uuid=None):
        if domain_uuid == None:
            domain_uuid = str(uuid4())
        if self.xml.find('uuid') == None:
            uuid_xml = ET.SubElement(self.xml, 'uuid') 
            uuid_xml.text = domain_uuid
        else:
            self.xml.find('uuid').text = domain_uuid
        return domain_uuid


    def domain_interface_add(self, network_name, mac_address=None, port=None):
        if mac_address == None:
            mac_address = macaddress_generator()
    
        add_interface = ET.SubElement(self.xml.find('devices'), "interface")
        add_interface.set('type', 'network')
        ET.SubElement(add_interface, 'mac').set('address', mac_address)
        ET.SubElement(add_interface, 'source').set('network', network_name)
        ET.SubElement(add_interface, 'model').set('type', 'virtio')

        if port:
            add_interface.find('source').set('portgroup', port)
    

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
    

    def domain_cdrom(self, target=None, path=None):
        '''
        ターゲットの指定がない場合最初に発見したcdromデバイスに突っ込む
        self.xmlを編集して，libvirtで使う該当部分を返す
        '''
        # デバイスリストでforを回す
        for disk in self.xml.find('devices').iter('disk'):
            # hddとcdromがいるのでcdromだけ
            # ターゲットが指定されててかつ，違う場合はスキップ
            if (disk.get('device') == "cdrom") and ((target == None) or (disk.find('target').get('dev') == target)) :    
                if disk.find('source') == None:
                    ET.SubElement(disk, 'source') 
                disk.find('source').set('file', path)
                return ET.tostring(disk).decode()
    
    def domain_network(self, mac, network, port):
        devices = self.xml.find('devices')
        for interface in devices.iter('interface'):
            if interface.find('mac').get('address') != mac:
                continue
            interface.set('type','network')
            interface.find('source').set('network', network)
            try:
                interface.find('source').attrib.pop("portid", None)
                interface.find('source').attrib.pop("bridge", None)
                interface.remove(interface.find('virtualport'))
            except:
                pass

            if port != None:
                interface.find('source').set('portgroup', port)
            return ET.tostring(interface).decode()


    def domain_parse(self):
        vnc_xml = self.xml.find('devices').find('graphics')

        memory_unit = self.xml.find('memory').get("unit")
        memory = self.xml.find('memory').text

        model = DomainDetailXml(
            name=self.xml.find('name').text,
            memory=unit_convertor(memory_unit,"M",memory),
            memoryUnit="M",
            vcpu=self.xml.find('vcpu').text,
            uuid=self.xml.find('uuid').text,
            selinux=False,
            vnc_port=vnc_xml.get("port"),
            vnc_auto_port=vnc_xml.get("autoport"),
            vnc_listen=vnc_xml.get("listen"),
            vnc_password=vnc_xml.get("passwd", "none"),
            disk=[],
            interface=[],
            boot=[],
        )

        for boot in self.xml.find('os').findall('boot'):
            model.boot.append(boot.get('dev'))

        for disk in self.xml.find('devices').findall('disk'):
            model.disk.append(DomainDetailXmlDrive(
                device=disk.get("device"),
                type=disk.get("type"),
                target=disk.find("target").get("dev") if disk.find("target") != None else None,
                source=disk.find("source").get("file") if disk.find("source") != None else None
            ))
            
        for nic in self.xml.find('devices').findall('interface'):
            model.interface.append(DomainDetailXmlInterface(
                type=nic.get("type"),
                mac=nic.find("mac").get("address"),
                bridge=nic.find("source").get("bridge", None),
                network=nic.find("source").get("network", None),
                target=nic.find("target").get("dev",None) if nic.find("target") != None else None,
                port=nic.find("source").get("portgroup")
            ))

        for seclabel in self.xml.findall('seclabel'):
            if seclabel.get('model','None') == 'selinux':
                model.selinux = True

        return model
    

    def dump_file(self,type):
        xml_dir = APP_ROOT + '/data/xml/' +type+ '/'
        os.chdir = APP_ROOT
        os.makedirs(xml_dir, exist_ok=True)
        xml_uuid = self.xml.find('uuid').text
        ET.ElementTree(self.xml).write(xml_dir + xml_uuid + '.xml')


    def storage_base_edit(self,name,path):
        self.xml.find('name').text = name
        self.xml.find('target').find('path').text = path


    def network_bridge_edit(self,name,bridge):
        self.xml.find('name').text = name
        self.xml.find('forward').set('mode', 'bridge')
        self.xml.find('bridge').set('name', bridge)

    
def unit_convertor(from_unit, to_unit, value):
    if from_unit == "bytes" and to_unit == "G":
        return round(float(value)/1024/1024/1024,1)
    elif from_unit == "bytes" and to_unit == "M":
        return round(float(value)/1024/1024,1)
    elif from_unit == "KiB" and to_unit == "M":
        return round(float(value)/1024,1)
 
    return value


def macaddress_generator():
    import random
    mac = [ 0x00, 0x16, 0x3e,
    random.randint(0x00, 0x7f),
    random.randint(0x00, 0xff),
    random.randint(0x00, 0xff) ]
    return( ':'.join(map(lambda x: "%02x" % x, mac)))