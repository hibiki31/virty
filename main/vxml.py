import xml.etree.ElementTree as ET
import os, uuid, vsql, vvirt

SPATH = '/root/virty/main'
SQLFILE = SPATH + '/data.sqlite'


class XmlEdit():
	def __init__(self,xmldata):
		self.root = ET.fromstring(xmldata)
	def dump(self):
		print(ET.tostring(self.root).decode())
	def name(self,NEW_NAME):
		self.root.findall('name')[0].text = NEW_NAME

	
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

