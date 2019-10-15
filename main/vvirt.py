import libvirt, sys, sqlite3, subprocess, os
import vsql, vxml, vansible, vhelp,os, uuid
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

    def DomainXmlOpen(self,DOMAIN_UUID):
        self.con = self.node.lookupByUUIDString(DOMAIN_UUID)
        self.dxml = ET.fromstring(self.con.XMLDesc())
        self.dpower = self.con.state()[0]
        #5:OFF
    
    def DomainXmlDump(self):
        self.dxmldump = ET.tostring(self.dxml).decode()
        return self.dxmldump

    def DomainNameEdit(self,NEW_NAME):
        self.dxml.findall('name')[0].text = NEW_NAME

    def DomainXmlUpdate(self):
        if self.dpower == 5:
            self.con.undefine()
            self.node.defineXML(self.dxmldump)
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
            return [2,"domain","stop","Already stop domain"]
        try:
            self.con.destroy()
        except:
            return [1,"domain","stop",""]
        else:
            return [0,"domain","stop",""]

    def DomainShutdown(self):
        if self.dpower == 5:
            return [2,"domain","shutdown","Already shutdown domain"]
        try:
            self.con.shutdown()
        except:
            return [1,"domain","shutdown",""]
        else:
            return [0,"domain","shutdown",""]

    def DomainPoweron(self):
        if self.dpower == 1:
            return [2,"domain","poweron","Already poweron domain"]
        try:
            self.con.create()
        except:
            return [1,"domain","poweron",""]
        else:
            return [0,"domain","poweron",""]
	
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
        self.nobj = self.node.networkDefineXML(ET.tostring(self.nxml).decode())

    def NetworkXmlDump(self):
        self.nxmldump = ET.tostring(self.nxml).decode()
        return self.nxmldump

    def NetworkStart(self):
        self.nobj.create()

	# xml = dom.XMLDesc()

	# macaddress = vxml.XmlGenMac()
	# source = "virbr0"

	# interface = ET.fromstring("<interface></interface>")
	# interface.set('type', 'bridge')
	# ET.SubElement(interface, 'mac').set('address', macaddress)
	# ET.SubElement(interface, 'source').set('bridge', source)
	# ET.SubElement(interface, 'model').set('type', 'virtio')
	
	# address = ET.SubElement(interface, 'address')
	# address.set('bus', '0x00')
	# address.set('domain', '0x0000')
	# address.set('function', '0x0')
	# address.set('slot', '0x02')
	# address.set('type', 'pci')


	# devices = ET.fromstring(xml).find('devices')


	# dom.updateDeviceFlags(ET.tostring(devices).decode())
	# print(ET.tostring(interface).decode())






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

