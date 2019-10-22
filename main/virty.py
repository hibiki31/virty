#!/usr/local/bin/python3
import libvirt, sys, sqlite3, subprocess, os
import vsql, vxml, vansible, vhelp, vvirt

SPATH = '/root/virty/main'
SQLFILE = SPATH + '/data.sqlite'

class Color():
	BLACK     = '\033[30m'
	RED       = '\033[31m'
	GREEN     = '\033[32m'
	YELLOW    = '\033[33m'
	BLUE      = '\033[34m'
	PURPLE    = '\033[35m'
	CYAN      = '\033[36m'
	WHITE     = '\033[37m'
	END       = '\033[0m'
	BOLD      = '\038[1m'
	UNDERLINE = '\033[4m'
	INVISIBLE = '\033[08m'
	REVERCE   = '\033[07m'


def QueuStatus():
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


def Pooler():
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
		#proc = subprocess.Popen(["python3", "/root/virty/main/vworker.py"],shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		proc = subprocess.Popen(["python3", "/root/virty/main/vworker.py"])

################## LOG ##################
def LogInfo(TAG,TEXT):
	print("[" + Color.CYAN + TAG + Color.END + "] " +  TEXT)

def LogError(TAG,TEXT):
	print("[" + Color.RED + TAG + Color.END + "] " +  TEXT)

def LogSuccess(TAG,TEXT):
	print("[" + Color.GREEN + TAG + Color.END + "] " +  TEXT)


################## Libvirt ##################
def LibvirtDomainListConnect():
	nodes = vsql.SqlGetAll("kvm_node")
	for node in nodes:
		conn = libvirt.open('qemu+ssh://' + node[1] + '/system')
		domains = conn.listAllDomains()
		for domain in domains:
			con = conn.lookupByName(domain.name())
			state, reason = con.state()
			if state == libvirt.VIR_DOMAIN_NOSTATE:
				print('The state is VIR_DOMAIN_NOSTATE')
			elif state == libvirt.VIR_DOMAIN_RUNNING:
				LogSuccess("RUN",'{0:24} {1:8}'.format(domain.name(),node[0]))
			elif state == libvirt.VIR_DOMAIN_BLOCKED:
				print('The state is VIR_DOMAIN_BLOCKED')
			elif state == libvirt.VIR_DOMAIN_PAUSED:
				print('The state is VIR_DOMAIN_PAUSED')
			elif state == libvirt.VIR_DOMAIN_SHUTDOWN:
				print('The state is VIR_DOMAIN_SHUTDOWN')
			elif state == libvirt.VIR_DOMAIN_SHUTOFF:
				LogError("DED",'{0:24} {1:8}'.format(domain.name(),node[0]))
			elif state == libvirt.VIR_DOMAIN_CRASHED:
				print('The state is VIR_DOMAIN_CRASHED')
			elif state == libvirt.VIR_DOMAIN_PMSUSPENDED:
				print('The state is VIR_DOMAIN_PMSUSPENDED')
			else:
				print(' The state is unknown.')
		conn.close
	

def LibvirtDomainUndefine(NODE_IP,DOM_NAME):
	conn = libvirt.open('qemu+ssh://' + NODE_IP + '/system')
	con = conn.lookupByName(DOM_NAME)
	try: 
		con.undefine()
	except:
		LogError("NG",DOM_NAME + " catn't delete")
	else:
		LogSuccess("OK",DOM_NAME + " deleted")

def LibvirtDomainDestroy(NODE_IP,DOM_NAME):
	conn = libvirt.open('qemu+ssh://' + NODE_IP + '/system')
	con = conn.lookupByName(DOM_NAME)
	try: 
		con.destroy()
	except:
		LogError("NG",DOM_NAME + " catn't stop")
	else:
		LogSuccess("OK",DOM_NAME + " stop")

def LibvirtDomainShutdown(NODE_IP,DOM_NAME):
	conn = libvirt.open('qemu+ssh://' + NODE_IP + '/system')
	con = conn.lookupByName(DOM_NAME)
	try: 
		con.shutdown()
	except:
		LogError("NG",DOM_NAME + " catn't stop")
	else:
		LogSuccess("OK",DOM_NAME + " stop")

def LibvirtNetworkUndefine(NODE_IP,NET_NAME):
	conn = libvirt.open('qemu+ssh://' + NODE_IP + '/system')
	con = conn.networkLookupByName(NET_NAME)
	try: 
		con.undefine()
	except:
		LogError("NG",NET_NAME + " catn't delete")
	else:
		LogSuccess("OK",NET_NAME + " deleted")

def LibvirtNetworkStop(NODE_IP,NET_NAME):
	conn = libvirt.open('qemu+ssh://' + NODE_IP + '/system')
	con = conn.networkLookupByName(NET_NAME)
	try:
		con.destroy()
	except:
		LogError("NG",NET_NAME + " catn't stop")
	else:
		LogSuccess("OK",NET_NAME + " stop")

 
def VirtyInit():
	inputvalue = input("Do you want to initialize the database?(y or other):")
	if inputvalue == "y":
		vsql.SqlInit()
	inputvalue = input("Do you want to add node now?(y or other):")
	if inputvalue == "y":
		inputvalue = int(input("How many nodes do you want to add(int):"))
		nodelist = []
		for i in range(inputvalue):
			n = str(i+1)
			node_name = input("Enter the name of the " + n  + "th node :")
			node_ip = input("Enter the ip of the " + n + "th node :")
			node_core = input("Enter the core of the " + n + "th node :")
			node_memory = input("Enter the memory MB of the " + n + "th node :")
			nodelist.append([node_name,node_ip,node_core,node_memory])
		vsql.SqlAddNode(nodelist)
	inputvalue = input("Do you want to elase L2Lesspool?(y or other):")
	if inputvalue == "y":
		vsql.SqlClearL2lesspool()
	inputvalue = input("Do you want to initialize the L2Lesspool?(y or other):")
	if inputvalue == "y":
		with open(SPATH + '/file/l2l.csv', 'r') as f:
			for line in f:
				elements = line.split(',') 
				vsql.SqlAddL2lesspool([(elements[0],elements[1],elements[2],elements[3],elements[4])])
	inputvalue = input("Do you want to initialize the VNCPOOL?(y or other):")
	if inputvalue == "y":
		nodes = vsql.SqlGetAll("kvm_node")
		for node in nodes:
			for i in range(5900,6000):
				vsql.SqlAddVncpool([(i,"none","VNCpassWord",node[0])])
	

def VirtyVncFree(NODENAME):
	vnc = vsql.SqlGetVncportFree(NODENAME)
	return int(vnc[0][0])

def Virtyl2lFree():
	get = vsql.SqlGetL2lessFree()
	print(get)
	
def VirtyNodeList():
	nodes = vsql.SqlGetAll("kvm_node")
	for data in nodes:
		LogInfo("NODE",'{0:8} {1:14} {2:6.2f} {3:2} {4:8}'.format(data[0], data[1], data[2], str(data[3]),data[4]))
	vansible.AnsibleNodelistInit()
	

def VirtyVncList():
	vnc = vsql.SqlGetVncport()
	print("test")
	for node in vnc:
		LogInfo("List","name: {0}     IP: {1}    Memory: {2}".format(node[0], node[1], node[3]))

def VirtyNodeAddinput():
	nodelist = []
	node_name = input("Enter the name of the node :")
	node_ip = input("Enter the ip of the node :")
	node_core = input("Enter the core of the node :")
	node_memory = input("Enter the memory MB of the node :")
	nodelist.append([node_name,node_ip,node_core,node_memory])
	vsql.SqlAddNode(nodelist)	

def VirtyNodeAdd(NODE_NAME,NODE_IP):
	NODE_MEM = VirtyInfoMem(NODE_IP)
	NODE_CORE = VirtyInfocpu(NODE_IP)
	NODE_CPU = VirtyInfocpuname(NODE_IP)
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
	

def VirtyNodeDelete(NODENAME):
	vsql.SqlDeleteNode(NODENAME)
	LogInfo("OK", str(NODENAME) + "is deleted")

def VirtyDomainpoolAdd():
	poollist = []
	pool_name = input("Enter the pool name:")
	pool_node_name = input("Enter the node name:")
	pool_setram = input("Enter the Set memory MB:")
	poollist.append([pool_name,pool_node_name,pool_setram])
	vsql.SqlAddDomainpool(poollist)

def VirtyDomainpoolAddLine(POOL_NAME,NODE_NAME,POOL_RAM):
	print([(POOL_NAME,NODE_NAME,POOL_RAM)])
	vsql.SqlAddDomainpool([(POOL_NAME,NODE_NAME,POOL_RAM)])

def VirtyDomainpoolList():
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

def VirtyDomainpoolFree(POOLNAME):
	domains = vsql.SqlGetAll("kvm_domain")
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

def VirtyArchiveInit(NAME):
	nodes = vsql.SqlGetAll("kvm_node")
	for node in nodes:
		ARCHIVE_DIR = vsql.SqlGetData("NODE_NAME","ARCHIVE_DIR",node[0])
		if ARCHIVE_DIR == None:
			LogInfo("Skip",node[0] + " archive storage dose not exits")
			break
		LogInfo("Info",node[0] + "  on  " + ARCHIVE_DIR)
		vansible.AnsibleFilecpTonode(node[1], SPATH + '/img/' + NAME + '.img', ARCHIVE_DIR + NAME + '.img')
		vsql.SqlAddArchive([(NAME,ARCHIVE_DIR + NAME + '.img',node[0])])
	



def VirtyArchiveList():
	datas = vsql.SqlGetArchive()
	for data in datas:
		LogInfo("Archive","name: {0}     PATH: {1}    NODE: {2}".format(data[0], data[1], data[2]))
	

def VirtyL2lesspoolList():
	datas = vsql.SqlGetL2less()
	for data in datas:
		LogInfo("l2l","name: {0} ip: {1} gw: {2} domain: {3} node: {4}".format(data[0], data[1], data[2], data[3], data[4]))

def VirtyDomainMakeNomal(ARCHIVE_NAME,NODE_NAME,DOM_NAME,NIC,VNC,MEMORY,CORE,DOMAINPOOL_NAME):
	NODE_IP = vsql.SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
	ARCHIVE_PATH = vsql.SqlHitData("ARCHIVE_NAMEtoARCHIVE_PATH",ARCHIVE_NAME)
	vansible.AnsibleFilecpInnode(NODE_IP,ARCHIVE_PATH,'/kvm/dom/'+ DOM_NAME + '.img')
	vxml.XmlDomainMake(DOM_NAME,'/kvm/dom/'+ DOM_NAME + '.img',VNC,NIC,MEMORY,CORE)
	VirshDefine(NODE_IP)
	vsql.SqlAddDomain([(DOM_NAME,0,NODE_NAME,CORE,MEMORY,DOMAINPOOL_NAME,"Nomal","Unkwon")])
	
	
def VirtyDomMakeL2l(ARCHIVE_NAME,DOM_NAME,NIC,MEMORY,CORE,DOMAINPOOL_NAME):
	NODE_NAME = VirtyDomainpoolFree(DOMAINPOOL_NAME)
	NODE_IP = vsql.SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
	ARCHIVE_PATH = vsql.SqlHitData("ARCHIVE_NAMEtoARCHIVE_PATH",ARCHIVE_NAME)
	VNC = str(VirtyVncFree(NODE_NAME))
	vsql.SqlAddDomain([(DOM_NAME,0,NODE_NAME,CORE,MEMORY,DOMAINPOOL_NAME)])
	vansible.AnsibleFilecpInnode(NODE_IP,ARCHIVE_PATH,'/kvm/dom/'+ DOM_NAME + '.img')
	vxml.XmlDomainMake(DOM_NAME,'/kvm/dom/'+ DOM_NAME + '.img',VNC,NIC,MEMORY,CORE)
	VirshDefine(NODE_IP)
	VirtyNetMake(NIC,NODE_NAME,DOM_NAME)

def VirtyDomUndefine(DOM_NAME):
	NODE_NAME = vsql.SqlGetData("DOM_NAME","NODE_NAME",DOM_NAME)
	NODE_IP = vsql.SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)

	LibvirtDomainDestroy(NODE_IP,DOM_NAME)
	LibvirtDomainUndefine(NODE_IP,DOM_NAME)

	# vsql.SqlDeleteDomain([(DOM_NAME)])
	

def VirtyDiskDelete(DOM_NAME):
	NODE_NAME = vsql.SqlGetData("DOM_NAME","NODE_NAME",DOM_NAME)
	NODE_IP = vsql.SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)

	LibvirtDomainDestroy(NODE_IP,DOM_NAME)

	vansible.AnsibleFiledeleteInnode(NODE_IP,"/kvm/dom/" + DOM_NAME + ".img")


def VirtyNetDefine(NODEIP):
	with open(SPATH + "/xml/temp_net.xml") as f:
		s = f.read()
		conn = libvirt.open('qemu+ssh://' + NODEIP + '/system')
		conn.networkDefineXML(s)

def VirtyNetMake(L2l_NAME,NODE_NAME,DOM_NAME):
	NODE_IP = vsql.SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
	datas = vsql.SqlHitL2less("NAMEtoDATA",L2l_NAME)
	for data in datas:
		vxml.XmlL2lessnetMake(data[0],data[2],data[1])
		vsql.SqlAddL2lesspool([(data[0],data[1],data[2],DOM_NAME,NODE_NAME)])
	VirtyNetDefine(NODE_IP)
	VirtyNetStart(L2l_NAME)

##L2l
def VirtyL2lnetMake(L2L_NAME,NODE_NAME,GW_IP):
	NODE_IP = vsql.SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
	vxml.XmlL2lessnetMake(L2L_NAME,GW_IP,"None")
	VirtyNetDefine(NODE_IP)
	VirtyNetStart(L2l_NAME)



def VirtyNetDelete(l2l_NAME):
	l2l_NODE_NAME = vsql.SqlHitData("l2l_NAMEtol2l_NODE_NAME",l2l_NAME)
	l2l_NODE_IP = vsql.SqlHitData("NODE_NAMEtoNODE_IP",l2l_NODE_NAME)
	conn = libvirt.open('qemu+ssh://' + l2l_NODE_IP + '/system')
	con = conn.networkLookupByName(l2l_NAME)
	try: 
		con.undefine()
	except:
		LogError("NG",l2l_NAME + " catn't delete")
		exit(1)

def VirtyNetStart(l2l_NAME):
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
	

def VirtyNodeInit(PBNAME,EXVALUE):
	if PBNAME == "gluster":
		cmd = 'ansible-playbook ' + SPATH + '/ansible/pb_init_gluster.yml -i  ' + SPATH + '/ansible/host_node.ini --extra-vars ' + EXVALUE
		subprocess.check_call(cmd, shell=True)
	elif PBNAME == "libvirt":
		cmd = 'ansible-playbook ' + SPATH + '/ansible/pb_init_libvirt.yml -i  ' + SPATH + '/ansible/host_node.ini'
		subprocess.check_call(cmd, shell=True)	
	elif PBNAME == "frr":
		cmd = 'ansible-playbook ' + SPATH + '/ansible/pb_init_frr.yml -i  ' + SPATH + '/ansible/host_node.ini'
		subprocess.check_call(cmd, shell=True)
	

def VirtyImgInit(IMG):
	nodes = vsql.SqlGetAll("kvm_node")
	for node in nodes:
		FileCpToNode(node[1], '../img/' + IMG + '.img', IMG + '.img')

def VirtyDevelopDomain(DOM_NAME):
	NODE_NAME = vsql.SqlGetData("DOM_NAME","NODE_NAME",DOM_NAME)
	NODE_IP = vsql.SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
	conn = libvirt.open('qemu+ssh://' + NODE_IP + '/system')
	p = conn.lookupByName(DOM_NAME)
	clist = dir(p)
	for item in clist:
		print(item)
	


################## Virty List ##################
def VirtyDomainListInit():
	import xml.etree.ElementTree as ET 
	nodes = vsql.SqlGetAll("kvm_node")
	domlist = []
	for node in nodes:
		conn = libvirt.open('qemu+ssh://' + node[1] + '/system')
		domains = conn.listAllDomains()
		for domain in domains:
			if domain.state()[0]==5:DOM_POWER = "SHT"
			else :DOM_POWER = "RUN"
			ROOT = ET.fromstring(domain.XMLDesc())
			DOM_NAME = domain.name()
			NODE_NAME = node[0]
			DOM_CORE = ROOT.find('vcpu').text
			DOM_MEMORY = int(ROOT.find('memory').text)/1024
			DOM_UUID = ROOT.find('uuid').text
			DOM_TYPE = "unkwon"
			DOM_OS = "unknow"
			domlist.append((DOM_NAME, DOM_POWER,NODE_NAME,DOM_CORE,DOM_MEMORY,DOM_UUID,DOM_TYPE,DOM_OS))
		conn.close
	vsql.SqlAddDomain(domlist)
	VirtyDomainList()

def VirtyStorageList():
	datas = vsql.SqlGetAll("kvm_storage")
	print('          {0:12} {1:8} {2:8} {3:8} {4:8}'.format("NAME","NODE","DEVICE","TYPE","PATH"))
	for data in datas:
		LogSuccess("STORAGE",'{0:12} {1:8} {2:8} {3:8} {4:8}'.format(data[0], data[1], data[2], data[3], data[4]))
	

def VirtyQueList():
	datas = vsql.SqlGetAll("kvm_que")
	print('          {0:12} {1:8}'.format("NAME","NODE"))
	for data in datas:
		LogSuccess("QUE",'{0:12} {1:8}'.format(data[0], data[1]))
	

################## Virty Define ##################
def VirtyNicAdd(DOM_NAME):
	import xml.etree.ElementTree as ET 
	NODE_NAME = vsql.SqlGetData("DOM_NAME","NODE_NAME",DOM_NAME)
	NODE_IP = vsql.SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
	conn = libvirt.open('qemu+ssh://' + NODE_IP + '/system')
	dom = conn.lookupByName(DOM_NAME)
	
	xml = dom.XMLDesc()

	macaddress = vxml.XmlGenMac()
	source = "virbr0"

	interface = ET.fromstring("<interface></interface>")
	interface.set('type', 'bridge')
	ET.SubElement(interface, 'mac').set('address', macaddress)
	ET.SubElement(interface, 'source').set('bridge', source)
	ET.SubElement(interface, 'model').set('type', 'virtio')
	
	address = ET.SubElement(interface, 'address')
	address.set('bus', '0x00')
	address.set('domain', '0x0000')
	address.set('function', '0x0')
	address.set('slot', '0x02')
	address.set('type', 'pci')


	devices = ET.fromstring(xml).find('devices')


	dom.updateDeviceFlags(ET.tostring(devices).decode())
	print(ET.tostring(interface).decode())




	

def VirtyDomMakeBase(DOM_NAME,MEMORY,CORE,VNC_PORT,VNC_PASS):
	vxml.XmlDomainBaseMake(DOM_NAME,MEMORY,CORE,VNC_PORT,VNC_PASS)
	LogSuccess("OK","Base maked")
	

def VirtyDomMakeNicBridge(DOM_NAME,SOURCE):
	vxml.XmlBridgeNicAdd(DOM_NAME,SOURCE)
	LogInfo("OK","Nic added")
	

def VirtyDomMakeImg(DOM_NAME,STORAGE_NAME,ARCHIVE_NAME):
	vxml.XmlMetaSetStorage(DOM_NAME,STORAGE_NAME,ARCHIVE_NAME)
	LogInfo("OK","Img added")
	



def VirtyDomXmlSummry(DOM_NAME):
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
	


def VirtyDomXmlSummryGet(DOM_NAME):
	import xml.etree.ElementTree as ET 
	NODE_NAME = vsql.SqlGetData("DOM_NAME","NODE_NAME",DOM_NAME)
	NODE_IP = vsql.SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
	conn = libvirt.open('qemu+ssh://' + NODE_IP + '/system')
	con = conn.lookupByName(DOM_NAME)
	root = ET.fromstring(con.XMLDesc())
	NAME = root.find('name').text
	RAM = root.find('memory').text
	UNIT = root.find('memory').get("unit")
	vCPU = root.find('vcpu').text
	UUID = root.find('uuid').text

	vnc = root.find('devices').find('graphics')
	
	PORT = vnc.get("port")
	AUTO = vnc.get("autoport")
	LISTEN = vnc.get("listen")
	PASSWD = vnc.get("passwd", "none")

	infodata = [NAME,RAM,vCPU,PORT,AUTO,PASSWD,[],[],NODE_NAME,NODE_IP,UUID]


	for disk in root.find('devices').findall('disk'):
		if disk.find("source") is not None:
			DEVICE = disk.get("device")
			TYPE = disk.get("type")
			FILE = disk.find("source").get("file","none")
			TARGET =  disk.find("target").get("dev")
			infodata[6].append([DEVICE,TYPE,FILE,TARGET])
		else:
			DEVICE = disk.get("device")
			TYPE = disk.get("type")
			FILE = "Not Connect"
			TARGET = disk.find("target").get("dev")
			infodata[6].append([DEVICE,TYPE,FILE,TARGET])
	for nic in root.find('devices').findall('interface'):
		TYPE = nic.get("type")
		MAC = nic.find("mac").get("address")
		if nic.find("target") == None:
			TARGET = "none"
		else:
			TARGET = nic.find("target").get("dev","none")
		
		TO = nic.find("source").get("bridge")
		infodata[7].append([TYPE,MAC,TARGET,TO])

	return infodata
	

def DomainXmlSummary(DOM_UUID):
	import xml.etree.ElementTree as ET 
	NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
	NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)
	conn = libvirt.open('qemu+ssh://' + NODE_IP + '/system')
	con = conn.lookupByUUIDString(DOM_UUID)
	root = ET.fromstring(con.XMLDesc())
	NAME = root.find('name').text
	RAM = root.find('memory').text
	UNIT = root.find('memory').get("unit")
	vCPU = root.find('vcpu').text
	UUID = root.find('uuid').text

	vnc = root.find('devices').find('graphics')
	
	PORT = vnc.get("port")
	AUTO = vnc.get("autoport")
	LISTEN = vnc.get("listen")
	PASSWD = vnc.get("passwd", "none")

	infodata = [NAME,RAM,vCPU,PORT,AUTO,PASSWD,[],[],NODE_NAME,NODE_IP,UUID]


	for disk in root.find('devices').findall('disk'):
		if disk.find("source") is not None:
			DEVICE = disk.get("device")
			TYPE = disk.get("type")
			FILE = disk.find("source").get("file","none")
			TARGET =  disk.find("target").get("dev")
			infodata[6].append([DEVICE,TYPE,FILE,TARGET])
		else:
			DEVICE = disk.get("device")
			TYPE = disk.get("type")
			FILE = "Not Connect"
			TARGET = disk.find("target").get("dev")
			infodata[6].append([DEVICE,TYPE,FILE,TARGET])
	for nic in root.find('devices').findall('interface'):
		TYPE = nic.get("type")
		MAC = nic.find("mac").get("address")
		if nic.find("target") == None:
			TARGET = "none"
		else:
			TARGET = nic.find("target").get("dev","none")
		
		TO = nic.find("source").get("bridge")
		infodata[7].append([TYPE,MAC,TARGET,TO])

	return infodata


def VirtyDomDefineStatic(DOM_NAME,NODE_NAME):
	import xml.etree.ElementTree as ET

	NODE_IP = vsql.SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)

	

	try:
		tree = ET.parse(SPATH + '/define/' + DOM_NAME + '.xml') 
		root = tree.getroot()
	except:
		LogError("NG","File dose not exit")
		exit(2)

	IMG_DEVICE_NAME = ["vda","vdb","vdc"]
	COUNTER = 0
	storages = root.find('metadata').findall('storage')
	for storage in storages:
		IMG_NAME = IMG_DEVICE_NAME[COUNTER]
		COUNTER = COUNTER + 1
		STORAGE_NAME = storage.get('storage')

		STORAGE_PATH = vsql.SqlGetData("STORAGE_DATA","STORAGE_PATH",(NODE_NAME,STORAGE_NAME))
		IMG_PATH = STORAGE_PATH + DOM_NAME + IMG_NAME + '.img'

		ARCHIVE_NAME = storage.get('archive')
		ARCHIVE_PATH = vsql.SqlHitData("ARCHIVE_NAMEtoARCHIVE_PATH",ARCHIVE_NAME)
		vxml.XmlImgAdd(DOM_NAME,STORAGE_PATH,IMG_NAME,STORAGE_NAME,ARCHIVE_NAME)
		
		vansible.AnsibleFilecpInnode(NODE_IP,ARCHIVE_PATH,IMG_PATH)
	return VirshDefine(DOM_NAME,NODE_IP)
	


def VirtyDomCheckStatic(DOM_NAME,NODE_NAME):
	import xml.etree.ElementTree as ET 

	NODE_IP = vsql.SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
	if NODE_IP == None:
		LogError("NG",NODE_NAME + " is not found")
		exit(1)
	else:
		LogSuccess("OK","Node is found")

	try:
		tree = ET.parse(SPATH + '/define/' + DOM_NAME + '.xml') 
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
	


################## Virty Undefine ##################
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
	

def VirtyDomUndefineStatic(DOM_NAME):
	NODE_NAME = vsql.SqlGetData("DOM_NAME","NODE_NAME",DOM_NAME)	
	NODE_IP = vsql.SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
	LibvirtDomainUndefine(NODE_IP,DOM_NAME)
	vsql.SqlDeleteDomain([(DOM_NAME)])
	


################## Virty Power ##################
def VirtyDomainStart(DOM_NAME):
	NODE_NAME = vsql.SqlGetData("DOM_NAME","NODE_NAME",DOM_NAME)
	NODE_IP = vsql.SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
	conn = libvirt.open('qemu+ssh://' + NODE_IP + '/system')
	con = conn.lookupByName(DOM_NAME)
	try:
		con.create()
	except libvirt.libvirtError as e:
		LogInfo("INFO",DOM_NAME + " " +e.args[0])
	LogSuccess("SUCC", DOM_NAME + " started")

def VirtyDomainAutostart(DOM_NAME):
	NODE_NAME = vsql.SqlGetData("DOM_NAME","NODE_NAME",DOM_NAME)
	NODE_IP = vsql.SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
	conn = libvirt.open('qemu+ssh://' + NODE_IP + '/system')
	con = conn.lookupByName(DOM_NAME)
	try:
		con.setAutostart(1)
	except libvirt.libvirtError as e:
		LogInfo("INFO",DOM_NAME + " " +e.args[0])
	LogSuccess("SUCC", DOM_NAME + " auto started")


def VirtyDomainShutdown(DOM_NAME):
	NODE_NAME = vsql.SqlGetData("DOM_NAME","NODE_NAME",DOM_NAME)
	NODE_IP = vsql.SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
	LibvirtDomainShutdown(NODE_IP,DOM_NAME)
	

def VirtyDomainDestroy(DOM_NAME):
	NODE_NAME = vsql.SqlGetData("DOM_NAME","NODE_NAME",DOM_NAME)
	NODE_IP = vsql.SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
	LibvirtDomainDestroy(NODE_IP,DOM_NAME)


################## Bata ##################
def VirshCommandList():
	conn = libvirt.open('qemu:///system')
	names = conn.listDefinedDomains()
	print(names)
	clist = dir(conn)
	for item in clist:
		print(item)


def VirshDefine(DOM_NAME,NODE_IP):
	with open(SPATH + '/define/' + DOM_NAME + '.xml') as f:
		s = f.read()
		conn = libvirt.open('qemu+ssh://' + NODE_IP + '/system')
		try:
			conn.defineXML(s)
		except Exception as e:
			return e
		return 0

############## GET INFO WITH SSH ################

def VirtyInfoMem(NODE_IP):
	cmd = ["ssh" , NODE_IP, "cat /proc/meminfo |grep MemTotal"]
	mem = subprocess.check_output(cmd)
	words = float(str(mem).split()[1])
	memory = words/1024000
	return memory

def VirtyInfocpu(NODE_IP):
	cmd = ["ssh" , NODE_IP, "grep processor /proc/cpuinfo | wc -l"]
	words = str(subprocess.check_output(cmd)).rstrip("\\n'").lstrip("'b")
	return words

def VirtyInfocpuname(NODE_IP):
	cmd = ["ssh" , NODE_IP, "grep 'model name' /proc/cpuinfo|uniq"]
	mem = subprocess.check_output(cmd)
	words = str(mem).split(":")[1].rstrip("\\n'")
	return words

def VirtyInfoDir(NODE_IP,NODE_DIR):
	cmd = ["ssh" , NODE_IP, "df" ,NODE_DIR,"|sed -e '1d'"]
	get = subprocess.check_output(cmd)
	storage = str(get).rstrip("\\n'").lstrip("b'").split()
	return storage


def VirtyStorageInfo(STORAGE_NAME):
	datas = vsql.SqlPush("select * from kvm_storage where storage_name='" + STORAGE_NAME + "'")
	print('{0:12} {1:8} {2:8} {3:8} {4:8}'.format("NAME","NODE","DEVICE","TYPE","PATH"))
	for data in datas:
		NODE_IP = vsql.SqlGetData("NODE_NAME","NODE_IP",data[1])
		if NODE_IP == None:	break
		DF = VirtyInfoDir(NODE_IP,data[4])
		print('{0:12} {1:8} {2:8} {3:8} {4:8} {5:12} {6:4.0f} {7:4.0f} {8:4.0f} {9:4} {10:4}'
		.format(data[0], data[1], data[2], data[3], data[4], DF[0], int(DF[1])/1000000, int(DF[2])/1000000, int(DF[3])/1000000, DF[4], DF[5]))
	


def VirtyNetworkAdd(NETWORK_NAME,NETWORK_BRIDGE,NETWORK_NODE):
	LogInfo("OK","Network added")
	vsql.SqlAddNetwork([(NETWORK_NAME,NETWORK_BRIDGE,NETWORK_NODE)])



################ Storage #################
def VirtyStorageAdd(STORAGE_NAME,STORAGE_NODE,STORAGE_DEVICE,STORAGE_TYPE,STORAGE_PATH):
	LogInfo("OK","Storage added")
	#virty storage add dir arhicve ssd chinon /kvm/archive
	vsql.SqlAddStorage([(STORAGE_NAME,STORAGE_NODE,STORAGE_DEVICE,STORAGE_TYPE,STORAGE_PATH)])


def VirtyDomXmldump(DOM_NAME):
	print(vvirt.DomXmldump(DOM_NAME))
	

def DomNameEdit(DOM_UUID,NEW_NAME):
	NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
	NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

	editor = vvirt.Libvirtc(NODE_IP)
	editor.DomainOpen(DOM_UUID)
	editor.DomainNameEdit(NEW_NAME)

	print(editor.DomainXmlUpdate())
	print(editor.DomainXmlDump())


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
	print(editor.DomainXmlUpdate())
	print(editor.DomainXmlDump())



def DomNicEdit(DOM_UUID,NOW_MAC,NEW_NIC):
	NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
	NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

	editor = vvirt.Libvirtc(NODE_IP)
	editor.DomainOpen(DOM_UUID)
	editor.DomainNicEdit(NOW_MAC,NEW_NIC)



def VirtyDomainList():
	datas = vsql.SqlGetDomain()
	print('POWER {0:16} {1:8} {2:4} {3:5} {4:36} {5:8} {6:8}'.format("NAME","NODE","CORE","MEMORY","UUID","TYPE","OS"))
	for data in datas:
		if data[1] == "SHT":
			LogError("SHT",'{0:16} {1:8} {2:4} {3:5.0f} {4:36} {5:8} {6:8}'.format(data[0], data[2], data[3],int(data[4])/1024,data[5], data[6], data[7]))
		elif data[1] == "RUN":
			LogSuccess("RUN",'{0:16} {1:8} {2:4} {3:5.0f} {4:36} {5:8} {6:8}'.format(data[0], data[2], data[3], int(data[4])/1024,data[5], data[6], data[7]))


def VirtyNetwork2lDefine(NODE_IP,XML_PATH,NAME,GW):
	editor = vvirt.Libvirtc(NODE_IP)
	editor.NetworkXmlTemplate(XML_PATH)
	print(editor.NetworkXmlDump())
	editor.NetworkXmlL2lEdit(NAME,GW)
	print(editor.NetworkXmlDump())
	editor.NetworkXmlDefine(NODE_IP)
	editor.NetworkStart()

def GetNicData(DOM_UUID):
	NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
	NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

	editor = vvirt.Libvirtc(NODE_IP)
	editor.DomainOpen(DOM_UUID)

	return editor.DomainNicShow()

def DomainData(DOM_UUID):
	NODE_NAME = vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
	NODE_IP = vsql.Convert("NODE_NAME","NODE_IP",NODE_NAME)

	manager = vvirt.Libvirtc(NODE_IP)
	editor = vvirt.Xmlc(manager.DomainOpen(DOM_UUID))

	data = editor.DomainData()
	data['node-name'] = NODE_NAME
	data['node-ip'] = NODE_IP

	return data


if __name__ == "__main__":


	args = sys.argv
	argnum = len(args)


	if argnum == 1:
		vhelp.VirtyHelp()
	elif argnum == 3:
		if args[1] == "dom" and args[2] == "make":vhelp.VirtyDomMakeHelp()
		if args[1] == "node" and args[2] == "add":vhelp.VirtyNodeAddHelp()
		if args[1] == "storage" and args[2] == "add":vhelp.VirtyStorageAddHelp()
	elif argnum == 4:
		if args[1] == "dom" and args[2] == "make" and args[3] == "nomal":vhelp.VirtyDomainMakeNomalHelp()
		if args[1] == "dom" and args[2] == "make" and args[3] == "base":vhelp.VirtyDomMakeBaseHelp()
		if args[1] == "dom" and args[2] == "make" and args[3] == "nic":vhelp.VirtyDomMakeNicHelp()	


	if argnum == 2:
		if args[1] == "init":VirtyInit()
		if args[1] == "develop":VirshCommandList()
	elif argnum == 3:
		if args[1] == "dom" and args[2] == "list":VirtyDomainList()
		if args[1] == "vnc" and args[2] == "list":VirtyVncList()
		if args[1] == "que" and args[2] == "list":VirtyQueList()
		if args[1] == "node" and args[2] == "list":VirtyNodeList()
		if args[1] == "node" and args[2] == "add-input":VirtyNodeAddinput()
		if args[1] == "archive" and args[2] == "list":VirtyArchiveList()
		if args[1] == "l2lpool" and args[2] == "list":VirtyL2lesspoolList()
		if args[1] == "storage" and args[2] == "list":VirtyStorageList()
		if args[1] == "dompool" and args[2] == "add":VirtyDomainpoolAdd()
		if args[1] == "dompool" and args[2] == "list":VirtyDomainpoolList()
	elif argnum == 4:
		if args[1] == "dom" and args[2] == "list" and args[3] == "connect":LibvirtDomainListConnect()
		if args[1] == "dom" and args[2] == "start": VirtyDomainStart(args[3])
		if args[1] == "dom" and args[2] == "autostart": VirtyDomainAutostart(args[3])
		if args[1] == "net" and args[2] == "start": VirtyNetStart(args[3])
		if args[1] == "net" and args[2] == "delete": VirtyNetDelete(args[3])
		if args[1] == "nic" and args[2] == "add": VirtyNicAdd(args[3])
		if args[1] == "node" and args[2] == "delete": VirtyNodeDelete([args[3]])
		if args[1] == "node" and args[2] == "init": VirtyNodeInit(args[3],"")
		if args[1] == "dom" and args[2] == "list" and args[3] == "init":VirtyDomainListInit()
		if args[1] == "archive" and args[2] == "init":VirtyArchiveInit(args[3])
		if args[1] == "develop" and args[2] == "dom": VirtyDevelopDomain(args[3])
		if args[1] == "dom" and args[2] == "destroy": VirtyDomainDestroy(args[3])
		if args[1] == "dom" and args[2] == "shutdown": VirtyDomainShutdown(args[3])
		if args[1] == "dom" and args[2] == "undefine": VirtyDomUndefine(args[3])
		if args[1] == "disk" and args[2] == "delete": VirtyDiskDelete(args[3])
		if args[1] == "dom" and args[2] == "info": VirtyDomXmlSummry(args[3])
		if args[1] == "storage" and args[2] == "info": VirtyStorageInfo(args[3])
		if args[1] == "dom" and args[2] == "undefine" : VirtyDomUndefineStatic(args[3])
	elif argnum == 5:
		if args[1] == "node" and args[2] == "add":VirtyNodeAdd(args[3],args[4])
		if args[1] == "node" and args[2] == "init": VirtyNodeInit(args[3],args[4])
		if args[1] == "dom" and args[2] == "img" and args[3] == "delete": VirtyImgDeleteStatic(args[4])
		if args[1] == "dom" and args[2] == "xml" and args[3] == "dump": VirtyDomXmldump(args[4])
	elif argnum == 6:
		if args[1] == "dom" and args[2] == "define" and args[3] == "static": VirtyDomDefineStatic(args[4],args[5])
		if args[1] == "dom" and args[2] == "check" and args[3] == "static": VirtyDomCheckStatic(args[4],args[5])
		if args[1] == "dompool" and args[2] == "add":VirtyDomainpoolAddLine(args[3],args[4],args[5])
		if args[1] == "network" and args[2] == "add":VirtyNetworkAdd(args[3],args[4],args[5])	
	elif argnum == 7:
		if args[1] == "dom" and args[2] == "make" and args[3] == "nic" and args[4] == "bridge":VirtyDomMakeNicBridge(args[5],args[6])
		if args[1] == "dom" and args[2] == "make" and args[3] == "img":VirtyDomMakeImg(args[4],args[5],args[6])
	elif argnum == 8:
		if args[1] == "storage" and args[2] == "add":VirtyStorageAdd(args[3],args[4],args[5],args[6],args[7])	
	elif argnum == 9:
		if args[1] == "dom" and args[2] == "make" and args[3] == "base":VirtyDomMakeBase(args[4],args[5],args[6],args[7],args[8])
	elif argnum == 10:
		if args[1] == "dom" and args[2] == "make" and args[3] == "l2l":VirtyDomMakeL2l(args[4],args[5],args[6],args[7],args[8],args[9])
	elif argnum == 12:
		if args[1] == "dom" and args[2] == "make" and args[3] == "nomal":VirtyDomainMakeNomal(args[4],args[5],args[6],args[7],args[8],args[9],args[10],args[11])
