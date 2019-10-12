#!/usr/local/bin/python3
import libvirt, sys, sqlite3, subprocess, os

#Settings
SCRIPTPATH = '/root/virty/main'

#Global
SP = SCRIPTPATH
SQLFILE = SCRIPTPATH + '/data.sqlite'

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
def SqlPost():
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	cur.execute('create table if not exists kvm_network (network_name,network_bridge,network_node,primary key (network_name,network_node))')



def Pooler():
    p1 = subprocess.Popen(["ps", "-ef"], shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p2 = subprocess.Popen(["grep", "/root/virty/main/spool.py"], stdin=p1.stdout, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p3 = subprocess.Popen(["grep", "python"], stdin=p2.stdout, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p4 = subprocess.Popen(["wc", "-l"], stdin=p3.stdout, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p1.stdout.close()
    p2.stdout.close()
    p3.stdout.close()
    output = p4.communicate()[0].decode("utf8").replace('\n','')
    print(output)
    if int(output) == 0:
        proc = subprocess.Popen(["python3", "/root/virty/main/spool.py"],shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

################## LOG ##################
def LogInfo(TAG,TEXT):
	print("[" + Color.CYAN + TAG + Color.END + "] " +  TEXT)

def LogError(TAG,TEXT):
	print("[" + Color.RED + TAG + Color.END + "] " +  TEXT)

def LogSuccess(TAG,TEXT):
	print("[" + Color.GREEN + TAG + Color.END + "] " +  TEXT)


################## Libvirt ##################
def LibvirtDomainListConnect():
	nodes = SqlGetAll("kvm_node")
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
	exit(0)

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


########### Ansible ########### 
def AnsibleFiledeleteInnode(NODEIP,FILE):
	exvar = ' "file=' + FILE  + ' host=' + NODEIP + '"'
	cmd = 'ansible-playbook ' + SP + '/ansible/pb_deleteinnode.yml -i  ' + SP + '/ansible/host_node.ini --extra-vars ' + exvar
	subprocess.check_call(cmd, shell=True)

def AnsibleFilecpInnode(NODEIP,CP,TO):
	print(NODEIP + CP + TO)
	exvar = ' "cp=' + CP  + ' host=' + NODEIP + ' to=' + os.path.basename(TO) + ' dir=' + os.path.dirname(TO) + '/"'
	print(exvar)
	cmd = 'ansible-playbook ' + SP + '/ansible/pb_cpinnode.yml -i  ' + SP + '/ansible/host_node.ini --extra-vars ' + exvar
	subprocess.check_call(cmd, shell=True)

def AnsibleFilecpTonode(NODEIP,CP,TO):
	exvar = ' "cp=' + CP  + ' host=' + NODEIP + ' to=' + os.path.basename(TO) + ' dir=' + os.path.dirname(TO) + '/"'
	cmd = 'ansible-playbook ' + SP + '/ansible/pb_cptonode.yml -i  ' + SP + '/ansible/host_node.ini --extra-vars ' + exvar
	subprocess.check_call(cmd, shell=True)

def	AnsibleNodelistInit():
	NODE_DATAS = SqlGetAll("kvm_node")
	nodeiplist = []
	for node in NODE_DATAS:
		nodeiplist.append(node[1] + "\n")
	f = open(SP + '/ansible/host_node.ini','w')
	f.writelines(nodeiplist)
	f.close()


########### Sql ########### 
def SqlClearL2lesspool():
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	cur.execute('delete from kvm_l2lesspool')
	con.commit()
	cur.close()
	con.close()

def SqlDeleteNode(NODENAMES):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	for node in NODENAMES:
		sql = 'delete from kvm_node where node_name = "' + node + '"'
		cur.execute(sql)
	con.commit()
	cur.close()
	con.close()	
	AnsibleNodelistInit()

def SqlDeleteDomain(DOM_NAMES):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	for dom in DOM_NAMES:
		sql = 'delete from kvm_domain where domain_name = "' + dom + '"'
		cur.execute(sql)
	con.commit()
	cur.close()
	con.close()	

def SqlGetVncport():
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'select * from kvm_vncpool'
	return cur.execute(sql).fetchall()
	cur.close()
	con.close()

def SqlGetAll(TABLE):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'select * from ' + TABLE
	return cur.execute(sql).fetchall()
	cur.close()
	con.close()

def SqlGetVncportFree(NODENAME):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'select min(vncpool_port) from kvm_vncpool where vncpool_domain_name="none" and vncpool_node_name ="' + NODENAME +'"'
	return cur.execute(sql).fetchall()
	cur.close()
	con.close()

def SqlGetDomainpool():
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'select * from kvm_domainpool'
	return cur.execute(sql).fetchall()
	cur.close()
	con.close()

def SqlGetArchive():
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'select * from kvm_archive'
	return cur.execute(sql).fetchall()
	cur.close()
	con.close()

def SqlGetDomain():
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'select * from kvm_domain'
	return cur.execute(sql).fetchall()
	cur.close()
	con.close()	

def SqlSumNode():
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'select sum(node_memory) from kvm_node'
	RAM = cur.execute(sql).fetchall()
	sql = 'select sum(node_core) from kvm_node'
	CORE = cur.execute(sql).fetchall()
	return [RAM,CORE]
	cur.close()
	con.close()	

def SqlSumDomain():
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'select sum(domain_memory) from kvm_domain'
	RAM = cur.execute(sql).fetchall()
	sql = 'select sum(domain_core) from kvm_domain'
	CORE = cur.execute(sql).fetchall()
	return [RAM[0][0],CORE[0][0]]
	cur.close()
	con.close()	

def SqlGetL2less():
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'select * from kvm_l2lesspool'
	return cur.execute(sql).fetchall()
	con.commit()
	cur.close()
	con.close()	

def SqlGetL2lessFree():
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'select * from kvm_l2lesspool where l2lesspool_domain_name="none"'
	return cur.execute(sql).fetchall()
	cur.close()
	con.close()

def SqlAddNode(NODE_DATAS):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'replace into kvm_node (node_name, node_ip, node_core, node_memory, node_cpugen) values (?,?,?,?,?)'
	cur.executemany(sql, NODE_DATAS)
	con.commit()
	cur.close()
	con.close()
	AnsibleNodelistInit()
	exit(0)

def SqlAddStorage(STORAGE_DATAS):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'replace into kvm_storage (storage_name, storage_node_name, storage_device, storage_type, storage_path) values (?,?,?,?,?)'
	cur.executemany(sql, STORAGE_DATAS)
	con.commit()
	cur.close()
	con.close()
	AnsibleNodelistInit()
	exit(0)

def SqlAddNetwork(NETWORK_DATAS):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'replace into kvm_network (network_name,network_bridge,network_node) values (?,?,?)'
	cur.executemany(sql, NETWORK_DATAS)
	con.commit()
	cur.close()
	con.close()
	exit(0)	

def SqlAddVncpool(VNC_DATAS):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'replace into kvm_vncpool (vncpool_port, vncpool_domain_name, vncpool_passwd, vncpool_node_name) values (?,?,?,?)'
	cur.executemany(sql, VNC_DATAS)
	con.commit()
	cur.close()
	con.close()

def SqlAddL2lesspool(POOL_DATAS):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'replace into kvm_l2lesspool (l2lesspool_name, l2lesspool_ip, l2lesspool_gw, l2lesspool_domain_name, l2lesspool_node_name) values (?,?,?,?,?)'
	cur.executemany(sql, POOL_DATAS)
	con.commit()
	cur.close()
	con.close()
	AnsibleNodelistInit()

def SqlAddArchive(ARCHIVE_DATAS):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'replace into kvm_archive (archive_name, archive_path, archive_node_name) values (?,?,?)'
	cur.executemany(sql, ARCHIVE_DATAS)
	con.commit()
	cur.close()
	con.close()

def SqlAddImg(IMG_DATAS):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'replace into kvm_img (img_name, img_archive_name, img_domain_name,img_node_name) values (?,?,?,?)'
	cur.executemany(sql, IMG_DATAS)
	con.commit()
	cur.close()
	con.close()

def SqlAddDomain(DOMAIN_DATAS):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'replace into kvm_domain (domain_name, domain_status, domain_node_name, domain_core,domain_memory,domain_uuid, domain_type,domain_os) values (?,?,?,?,?,?,?,?)'
	cur.executemany(sql, DOMAIN_DATAS)
	con.commit()
	cur.close()
	con.close()

def SqlQueDomain(QUE_TYPE,DOMAIN_DATAS):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = "replace into kvm_que (que_type, que_json) values (\""+QUE_TYPE+"\",\""+str(DOMAIN_DATAS)+"\");"
	print(sql)
	cur.execute(sql)
	con.commit()
	cur.close()
	con.close()

def SqlDequeDomain(QUE_ID):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'delete from kvm_que where QUE_ID = ' + str(QUE_ID)
	cur.execute(sql)
	con.commit()
	cur.close()
	con.close()	


def	SqlAddDomainpool(POOL_DATAS):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'replace into kvm_domainpool (domainpool_name,domainpool_node_name,domainpool_setram) values (?,?,?)'
	cur.executemany(sql, POOL_DATAS)
	con.commit()
	cur.close()
	con.close()

def SqlHitData(HITCODE,HITNAME):
	if HITCODE == "ARCHIVE_NAMEtoARCHIVE_PATH":
		datas = SqlGetArchive()
		getdata = ""
		for data in datas:
			if data[0] == HITNAME:
				getdata = data[1]
		return getdata
	if HITCODE == "DOM_NAMEtoNODE_NAME":
		datas = SqlGetAll("kvm_domain")
		getdata = ""
		for data in datas:
			if data[0] == HITNAME:
				getdata = data[2]
		return getdata
	if HITCODE == "l2l_NAMEtol2l_NODE_NAME":
		datas = SqlGetL2less()
		getdata = ""
		for data in datas:
			if data[0] == HITNAME:
				getdata = data[4]
		return getdata	

def SqlGetData(SRC,DST,HINT):
	if SRC == "DOM_NAME":
		if DST == "NODE_NAME":
			for data in SqlGetAll("kvm_domain"):
				if data[0] == HINT:
					return data[2]
	elif SRC == "NODE_NAME":
		if DST == "NODE_IP":
			for data in SqlGetAll("kvm_node"):
				if data[0] == HINT:
					return data[1]
		elif DST == "ARCHIVE_DIR":
			GET = SqlPush("select * from kvm_storage where storage_name='archive' and storage_node_name='" + HINT + "'")
			if GET == []:	return
			return GET[0][4].rstrip("/") + "/"

	elif SRC == "ARCHIVE_DATA":
		if DST == "EXIST_STATUS":
			GET = SqlPush("select * from kvm_archive where archive_node_name='" + HINT[0] + "' and archive_name='" + HINT[1] + "'")
			if GET == []:	return 1
			return 0

	elif SRC == "STORAGE_DATA":
		if DST == "STORAGE_PATH":
			GET = SqlPush("select * from kvm_storage where storage_node_name='" + HINT[0] + "' and storage_name='" + HINT[1] + "'")
			if GET == []:	return 1
			return GET[0][4].rstrip("/") + "/"


def SqlPush(SQL):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	get = cur.execute(SQL).fetchall()
	return get

def SqlHitL2less(HITCODE,HITNAME):
	if HITCODE == "NAMEtoDATA":
		datas = SqlGetL2less()
		getdata = []
		for data in datas:
			if data[0] == HITNAME:
				getdata = [(data[0],data[1],data[2],data[3],data[4])]
		return getdata

def SqlDomain_NameToNode_Ip(DOM_NAME):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'select node from domain where domain="' + DOM_NAME +'"'
	dom = cur.execute(sql)
	noden = ""
	for node in dom:
		noden = node[0]
	sql = 'select ip from domain where node="' + DOM_NAME +'"'
	dom = cur.execute(sql)
	for ip in ips:
		noden = ip[0]
	return noden
	con.commit()
	cur.close()
	con.close()	

def SqlHitNodeName(DOM_NAME):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'select node from domain where domain ="' + DOM_NAME +'"'
	for hit in cur.execute(sql):
		get = hit[0]
	return get
	con.close()	

def SqlHitNodeIp(NODENAME):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'select ip from node where node ="' + NODENAME +'"'
	for hit in cur.execute(sql):
		get = hit[0]
	return get
	con.close()	

def SqlHitImg(DOM_NAME):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'select * from kvm_img where img_domain_name ="' + DOM_NAME +'"'
	return cur.execute(sql).fetchall()
	cur.close()
	con.close()	

########### XML ###########
def XmlGenMac():
    import random
    mac = [ 0x00, 0x16, 0x3e,
    random.randint(0x00, 0x7f),
    random.randint(0x00, 0xff),
    random.randint(0x00, 0xff) ]
    return( ':'.join(map(lambda x: "%02x" % x, mac)))

def XmlDomainMake(DOMAIN,IMG,VNC,NICS,MEMORY,CORE):
    import xml.etree.ElementTree as ET
    import os, uuid
    os.chdir = SP

    tree = ET.parse(SP + '/xml/dom_base.xml') 
    root = tree.getroot()

    memory = MEMORY
    vcpu = CORE
    uuid = str(uuid.uuid4())
    mac = GenMac()
    #memory,vcpu,name,uuid
    root.findall('memory')[0].text= memory
    root.findall('currentMemory')[0].text= memory
    root.findall('vcpu')[0].text= vcpu
    root.findall('name')[0].text= DOMAIN
    root.findall('uuid')[0].text= uuid

    #VNC
    devices = root.findall('devices')[0]
    graphics = devices.findall('graphics')[0]
    graphics.set('port', VNC) 
    graphics.set('passwd', 'pass') 

    #disk
    disk = devices.findall('disk')[0]
    disk_source = disk.findall('source')[0]
    disk_source.set('file', IMG)
    print(disk_source.attrib)

    #NICADD
	
    a_interface = ET.SubElement(devices, 'interface') 
    a_interface.set('type', 'bridge')
    a_mac = ET.SubElement(a_interface, 'mac')
    a_source = ET.SubElement(a_interface, 'source')
    a_model = ET.SubElement(a_interface, 'model')
    a_address = ET.SubElement(a_interface, 'address')
    a_filter = ET.SubElement(a_interface, 'filterref')
    a_filter.set('filter', 'yamato')
    a_mac.set('address', mac)
    a_source.set('bridge', NICS)
    a_model.set('type', 'virtio')
    a_address.set('bus', '0x00')
    a_address.set('domain', '0x0000')
    a_address.set('function', '0x0')
    a_address.set('slot', '0x03')
    a_address.set('type', 'pci')

    tree.write(SP + '/xml/run.xml')

def XmlDomainBaseMake(DOM_NAME,MEMORY,CORE,VNC_PORT,VNC_PASS):
	import xml.etree.ElementTree as ET
	import os
	os.chdir = SP

	tree = ET.parse(SP + '/xml/dom_base.xml') 
	root = tree.getroot()

	root.findall('name')[0].text = DOM_NAME
	root.find('memory').text = MEMORY
	root.find('currentMemory').text = MEMORY
	root.find('vcpu').text = CORE

	if VNC_PORT == "auto":
		root.find('devices').find('graphics').set('autoport', "yes")
		root.find('devices').find('graphics').set('port', "0")	
		root.find('devices').find('graphics').set('passwd', "pass")	
	else:
		root.find('devices').find('graphics').set('autoport', "no")
		root.find('devices').find('graphics').set('port', VNC_PORT)
	
	tree.write(SP + '/define/' + DOM_NAME + '.xml')

def XmlBridgeNicAdd(DOM_NAME,SOURCE):
	import xml.etree.ElementTree as ET
	import os
	os.chdir = SP

	MAC_ADDRESS = XmlGenMac()

	tree = ET.parse(SP + '/define/' + DOM_NAME + '.xml') 
	root = tree.getroot()

	interface = ET.SubElement(root.find('devices'), "interface")
	interface.set('type', 'bridge')
	ET.SubElement(interface, 'mac').set('address', MAC_ADDRESS)
	ET.SubElement(interface, 'source').set('bridge', SOURCE)
	ET.SubElement(interface, 'model').set('type', 'virtio')
	
	address = ET.SubElement(interface, 'address')
	address.set('bus', '0x00')
	address.set('domain', '0x0000')
	address.set('function', '0x0')
	address.set('slot', '0x03')
	address.set('type', 'pci')

	tree.write(SP + '/define/' + DOM_NAME + '.xml')

def XmlL2lessnetMake(l2l_NAME,l2l_GW,l2l_IP):
	import xml.etree.ElementTree as ET
	tree = ET.parse(SP + '/xml/net_l2less.xml') 
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

	tree.write(SP + '/define/' + l2l_NAME + '.xml')

def XmlImgAdd(DOM_NAME,STORAGE_PATH,IMG_NAME,STORAGE_NAME,ARCHIVE_NAME):
	import xml.etree.ElementTree as ET
	import os
	os.chdir = SP

	IMG_PATH = STORAGE_PATH + DOM_NAME + IMG_NAME + '.img'

	tree = ET.parse(SP + '/define/' + DOM_NAME + '.xml') 
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
	
	tree.write(SP + '/define/' + DOM_NAME + '.xml')

	SqlAddImg([(IMG_NAME,ARCHIVE_NAME,DOM_NAME,"none")])


def XmlMetaSetStorage(DOM_NAME,STORAGE_NAME,ARCHIVE_NAME):
	import xml.etree.ElementTree as ET
	import os
	os.chdir = SP
	tree = ET.parse(SP + '/define/' + DOM_NAME + '.xml') 
	root = tree.getroot()

	storage = ET.SubElement(root.find('metadata'), "storage")
	storage.set('storage',STORAGE_NAME)
	storage.set('archive',ARCHIVE_NAME)

	tree.write(SP + '/define/' + DOM_NAME + '.xml')


########### Virty ########### 
def VirtyInit():
	inputvalue = input("Do you want to initialize the database?(y or other):")
	if inputvalue == "y":
		try:
			os.remove(SQLFILE)
		except:
			LogInfo("Info","Database file dose not exist")
		con = sqlite3.connect(SQLFILE)
		cur = con.cursor()
		cur.execute('create table if not exists kvm_node (node_name primary key, node_ip, node_core, node_memory, node_cpugen)')
		cur.execute('create table if not exists kvm_que (que_id integer primary key,que_type, que_json)')
		cur.execute('create table if not exists kvm_network (network_name,network_bridge,network_node,primary key (network_name,network_node))')
		cur.execute('create table if not exists kvm_storage (storage_name, storage_node_name, storage_device, storage_type, storage_path, primary key (storage_name, storage_node_name))')
		cur.execute('create table if not exists kvm_domain (domain_name, domain_status, domain_node_name, domain_core,domain_memory,domain_uuid, domain_type,domain_os,primary key (domain_name,domain_node_name))')
		cur.execute('create table if not exists kvm_vncpool (vncpool_port, vncpool_domain_name, vncpool_passwd, vncpool_node_name, primary key (vncpool_port,vncpool_node_name))')
		cur.execute('create table if not exists kvm_domainpool (domainpool_name, domainpool_node_name, domainpool_setram)')
		cur.execute('create table if not exists kvm_archive (archive_name, archive_path, archive_node_name,primary key (archive_name,archive_node_name))')
		cur.execute('create table if not exists kvm_img (img_name, img_archive_name, img_domain_name,img_node_name,primary key (img_name,img_domain_name))')
		cur.execute('create table if not exists kvm_l2lesspool (l2lesspool_name primary key, l2lesspool_ip, l2lesspool_gw, l2lesspool_domain_name, l2lesspool_node_name)')
		LogInfo("OK","Successfully")
		con.commit()
		cur.close()
		con.close()
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
		SqlAddNode(nodelist)
	inputvalue = input("Do you want to elase L2Lesspool?(y or other):")
	if inputvalue == "y":
		SqlClearL2lesspool()
	inputvalue = input("Do you want to initialize the L2Lesspool?(y or other):")
	if inputvalue == "y":
		with open(SP + '/file/l2l.csv', 'r') as f:
			for line in f:
				elements = line.split(',') 
				SqlAddL2lesspool([(elements[0],elements[1],elements[2],elements[3],elements[4])])
	inputvalue = input("Do you want to initialize the VNCPOOL?(y or other):")
	if inputvalue == "y":
		nodes = SqlGetAll("kvm_node")
		for node in nodes:
			for i in range(5900,6000):
				SqlAddVncpool([(i,"none","VNCpassWord",node[0])])
	exit(0)

def VirtyVncFree(NODENAME):
	vnc = SqlGetVncportFree(NODENAME)
	return int(vnc[0][0])

def Virtyl2lFree():
	get = SqlGetL2lessFree()
	print(get)
	
def VirtyNodeList():
	nodes = SqlGetAll("kvm_node")
	for data in nodes:
		LogInfo("NODE",'{0:8} {1:14} {2:6.2f} {3:2} {4:8}'.format(data[0], data[1], data[2], str(data[3]),data[4]))
	AnsibleNodelistInit()
	exit(0)

def VirtyVncList():
	vnc = SqlGetVncport()
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
	SqlAddNode(nodelist)	

def VirtyNodeAdd(NODE_NAME,NODE_IP):
	NODE_MEM = VirtyInfoMem(NODE_IP)
	NODE_CORE = VirtyInfocpu(NODE_IP)
	NODE_CPU = VirtyInfocpuname(NODE_IP)
	NODE_DATAS_NEW = []
	NODE_DATAS_NEW.append([NODE_NAME,NODE_IP,NODE_MEM,NODE_CORE,NODE_CPU])
	SqlAddNode(NODE_DATAS_NEW)

	print(
		"\nNAME: " + NODE_NAME +
		"\nIP: " + NODE_IP +
		"\nMemory: " + str(NODE_MEM) +
		"\nCore: " + str(NODE_CORE) +
		"\nCPU: " + str(NODE_CPU)	
	)
	LogInfo("OK","Node added")
	exit(0)

def VirtyNodeDelete(NODENAME):
	SqlDeleteNode(NODENAME)
	LogInfo("OK", str(NODENAME) + "is deleted")

def VirtyDomainpoolAdd():
	poollist = []
	pool_name = input("Enter the pool name:")
	pool_node_name = input("Enter the node name:")
	pool_setram = input("Enter the Set memory MB:")
	poollist.append([pool_name,pool_node_name,pool_setram])
	SqlAddDomainpool(poollist)

def VirtyDomainpoolAddLine(POOL_NAME,NODE_NAME,POOL_RAM):
	print([(POOL_NAME,NODE_NAME,POOL_RAM)])
	SqlAddDomainpool([(POOL_NAME,NODE_NAME,POOL_RAM)])

def VirtyDomainpoolList():
	pools = SqlGetDomainpool()
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
	domains = SqlGetAll("kvm_domain")
	poollist = SqlGetDomainpool()
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
	nodes = SqlGetAll("kvm_node")
	for node in nodes:
		ARCHIVE_DIR = SqlGetData("NODE_NAME","ARCHIVE_DIR",node[0])
		if ARCHIVE_DIR == None:
			LogInfo("Skip",node[0] + " archive storage dose not exits")
			break
		LogInfo("Info",node[0] + "  on  " + ARCHIVE_DIR)
		AnsibleFilecpTonode(node[1], SP + '/img/' + NAME + '.img', ARCHIVE_DIR + NAME + '.img')
		SqlAddArchive([(NAME,ARCHIVE_DIR + NAME + '.img',node[0])])
	exit(0)



def VirtyArchiveList():
	datas = SqlGetArchive()
	for data in datas:
		LogInfo("Archive","name: {0}     PATH: {1}    NODE: {2}".format(data[0], data[1], data[2]))
	exit(0)

def VirtyL2lesspoolList():
	datas = SqlGetL2less()
	for data in datas:
		LogInfo("l2l","name: {0} ip: {1} gw: {2} domain: {3} node: {4}".format(data[0], data[1], data[2], data[3], data[4]))

def VirtyDomainMakeNomal(ARCHIVE_NAME,NODE_NAME,DOM_NAME,NIC,VNC,MEMORY,CORE,DOMAINPOOL_NAME):
	NODE_IP = SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
	ARCHIVE_PATH = SqlHitData("ARCHIVE_NAMEtoARCHIVE_PATH",ARCHIVE_NAME)
	AnsibleFilecpInnode(NODE_IP,ARCHIVE_PATH,'/kvm/dom/'+ DOM_NAME + '.img')
	XmlDomainMake(DOM_NAME,'/kvm/dom/'+ DOM_NAME + '.img',VNC,NIC,MEMORY,CORE)
	VirshDefine(NODE_IP)
	SqlAddDomain([(DOM_NAME,0,NODE_NAME,CORE,MEMORY,DOMAINPOOL_NAME,"Nomal","Unkwon")])
	exit(0)
	
def VirtyDomMakeL2l(ARCHIVE_NAME,DOM_NAME,NIC,MEMORY,CORE,DOMAINPOOL_NAME):
	NODE_NAME = VirtyDomainpoolFree(DOMAINPOOL_NAME)
	NODE_IP = SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
	ARCHIVE_PATH = SqlHitData("ARCHIVE_NAMEtoARCHIVE_PATH",ARCHIVE_NAME)
	VNC = str(VirtyVncFree(NODE_NAME))
	SqlAddDomain([(DOM_NAME,0,NODE_NAME,CORE,MEMORY,DOMAINPOOL_NAME)])
	AnsibleFilecpInnode(NODE_IP,ARCHIVE_PATH,'/kvm/dom/'+ DOM_NAME + '.img')
	XmlDomainMake(DOM_NAME,'/kvm/dom/'+ DOM_NAME + '.img',VNC,NIC,MEMORY,CORE)
	VirshDefine(NODE_IP)
	VirtyNetMake(NIC,NODE_NAME,DOM_NAME)

def VirtyDomUndefine(DOM_NAME):
	NODE_NAME = SqlGetData("DOM_NAME","NODE_NAME",DOM_NAME)
	NODE_IP = SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)

	LibvirtDomainDestroy(NODE_IP,DOM_NAME)
	LibvirtDomainUndefine(NODE_IP,DOM_NAME)

	SqlDeleteDomain([(DOM_NAME)])
	exit(0)

def VirtyDiskDelete(DOM_NAME):
	NODE_NAME = SqlGetData("DOM_NAME","NODE_NAME",DOM_NAME)
	NODE_IP = SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)

	LibvirtDomainDestroy(NODE_IP,DOM_NAME)

	AnsibleFiledeleteInnode(NODE_IP,"/kvm/dom/" + DOM_NAME + ".img")


def VirtyNetDefine(NODEIP):
	with open(SP + "/xml/temp_net.xml") as f:
		s = f.read()
		conn = libvirt.open('qemu+ssh://' + NODEIP + '/system')
		conn.networkDefineXML(s)

def VirtyNetMake(L2l_NAME,NODE_NAME,DOM_NAME):
	NODE_IP = SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
	datas = SqlHitL2less("NAMEtoDATA",L2l_NAME)
	for data in datas:
		XmlL2lessnetMake(data[0],data[2],data[1])
		SqlAddL2lesspool([(data[0],data[1],data[2],DOM_NAME,NODE_NAME)])
	VirtyNetDefine(NODE_IP)
	VirtyNetStart(L2l_NAME)

##L2l
def VirtyL2lnetMake(L2L_NAME,NODE_NAME,GW_IP):
	NODE_IP = SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
	XmlL2lessnetMake(L2L_NAME,GW_IP,"None")
	VirtyNetDefine(NODE_IP)
	VirtyNetStart(L2l_NAME)



def VirtyNetDelete(l2l_NAME):
	l2l_NODE_NAME = SqlHitData("l2l_NAMEtol2l_NODE_NAME",l2l_NAME)
	l2l_NODE_IP = SqlHitData("NODE_NAMEtoNODE_IP",l2l_NODE_NAME)
	conn = libvirt.open('qemu+ssh://' + l2l_NODE_IP + '/system')
	con = conn.networkLookupByName(l2l_NAME)
	try: 
		con.undefine()
	except:
		LogError("NG",l2l_NAME + " catn't delete")
		exit(1)

def VirtyNetStart(l2l_NAME):
	l2l_NODE_NAME = SqlHitData("l2l_NAMEtol2l_NODE_NAME",l2l_NAME)
	l2l_NODE_IP = SqlHitData("NODE_NAMEtoNODE_IP",l2l_NODE_NAME)
	conn = libvirt.open('qemu+ssh://' + l2l_NODE_IP + '/system')
	con = conn.networkLookupByName(l2l_NAME)
	try:
		con.create()
	except:
		LogError("ERRO",l2l_NAME + " catn't start ")
		exit(1)
	LogSuccess("SUCC", l2l_NAME + " started")
	exit(0)

def VirtyNodeInit(PBNAME,EXVALUE):
	if PBNAME == "gluster":
		cmd = 'ansible-playbook ' + SP + '/ansible/pb_init_gluster.yml -i  ' + SP + '/ansible/host_node.ini --extra-vars ' + EXVALUE
		subprocess.check_call(cmd, shell=True)
	elif PBNAME == "libvirt":
		cmd = 'ansible-playbook ' + SP + '/ansible/pb_init_libvirt.yml -i  ' + SP + '/ansible/host_node.ini'
		subprocess.check_call(cmd, shell=True)	
	elif PBNAME == "frr":
		cmd = 'ansible-playbook ' + SP + '/ansible/pb_init_frr.yml -i  ' + SP + '/ansible/host_node.ini'
		subprocess.check_call(cmd, shell=True)
	exit(0)

def VirtyImgInit(IMG):
	nodes = SqlGetAll("kvm_node")
	for node in nodes:
		FileCpToNode(node[1], '../img/' + IMG + '.img', IMG + '.img')

def VirtyDevelopDomain(DOM_NAME):
	NODE_NAME = SqlGetData("DOM_NAME","NODE_NAME",DOM_NAME)
	NODE_IP = SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
	conn = libvirt.open('qemu+ssh://' + NODE_IP + '/system')
	p = conn.lookupByName(DOM_NAME)
	clist = dir(p)
	for item in clist:
		print(item)
	exit(0)


################## Virty List ##################
def VirtyDomainListInit():
	import xml.etree.ElementTree as ET 
	nodes = SqlGetAll("kvm_node")
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
	SqlAddDomain(domlist)
	VirtyDomainList()

def VirtyDomainList():
	datas = SqlGetDomain()
	print('POWER {0:16} {1:8} {2:4} {3:5} {4:36} {5:8} {6:8}'.format("NAME","NODE","CORE","MEMORY","UUID","TYPE","OS"))
	for data in datas:
		if data[1] == "SHT":
			LogError("SHT",'{0:16} {1:8} {2:4} {3:5.0f} {4:36} {5:8} {6:8}'.format(data[0], data[2], data[3],int(data[4])/1024,data[5], data[6], data[7]))
		elif data[1] == "RUN":
			LogSuccess("RUN",'{0:16} {1:8} {2:4} {3:5.0f} {4:36} {5:8} {6:8}'.format(data[0], data[2], data[3], int(data[4])/1024,data[5], data[6], data[7]))
def VirtyStorageList():
	datas = SqlGetAll("kvm_storage")
	print('          {0:12} {1:8} {2:8} {3:8} {4:8}'.format("NAME","NODE","DEVICE","TYPE","PATH"))
	for data in datas:
		LogSuccess("STORAGE",'{0:12} {1:8} {2:8} {3:8} {4:8}'.format(data[0], data[1], data[2], data[3], data[4]))
	exit(0)

def VirtyQueList():
	datas = SqlGetAll("kvm_que")
	print('          {0:12} {1:8}'.format("NAME","NODE"))
	for data in datas:
		LogSuccess("QUE",'{0:12} {1:8}'.format(data[0], data[1]))
	exit(0)

################## Virty Define ##################
def VirtyNicAdd(DOM_NAME):
	import xml.etree.ElementTree as ET 
	NODE_NAME = SqlGetData("DOM_NAME","NODE_NAME",DOM_NAME)
	NODE_IP = SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
	conn = libvirt.open('qemu+ssh://' + NODE_IP + '/system')
	dom = conn.lookupByName(DOM_NAME)
	
	xml = dom.XMLDesc()

	macaddress = XmlGenMac()
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




	exit(0)

def VirtyDomMakeBase(DOM_NAME,MEMORY,CORE,VNC_PORT,VNC_PASS):
	XmlDomainBaseMake(DOM_NAME,MEMORY,CORE,VNC_PORT,VNC_PASS)
	LogSuccess("OK","Base maked")
	exit(0)

def VirtyDomMakeNicBridge(DOM_NAME,SOURCE):
	XmlBridgeNicAdd(DOM_NAME,SOURCE)
	LogInfo("OK","Nic added")
	exit(0)

def VirtyDomMakeImg(DOM_NAME,STORAGE_NAME,ARCHIVE_NAME):
	XmlMetaSetStorage(DOM_NAME,STORAGE_NAME,ARCHIVE_NAME)
	LogInfo("OK","Img added")
	exit(0)

def VirtyDomXmldump(DOM_NAME):
	NODE_NAME = SqlGetData("DOM_NAME","NODE_NAME",DOM_NAME)
	NODE_IP = SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
	conn = libvirt.open('qemu+ssh://' + NODE_IP + '/system')
	con = conn.lookupByName(DOM_NAME)
	print(con.XMLDesc())

def VirtyDomXmlSummry(DOM_NAME):
	import xml.etree.ElementTree as ET 
	NODE_NAME = SqlGetData("DOM_NAME","NODE_NAME",DOM_NAME)
	NODE_IP = SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
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
	exit(0)


def VirtyDomXmlSummryGet(DOM_NAME):
	import xml.etree.ElementTree as ET 
	NODE_NAME = SqlGetData("DOM_NAME","NODE_NAME",DOM_NAME)
	NODE_IP = SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
	conn = libvirt.open('qemu+ssh://' + NODE_IP + '/system')
	con = conn.lookupByName(DOM_NAME)
	root = ET.fromstring(con.XMLDesc())
	NAME = root.find('name').text
	RAM = root.find('memory').text
	UNIT = root.find('memory').get("unit")
	vCPU = root.find('vcpu').text
	
	vnc = root.find('devices').find('graphics')
	
	PORT = vnc.get("port")
	AUTO = vnc.get("autoport")
	LISTEN = vnc.get("listen")
	PASSWD = vnc.get("passwd", "none")

	infodata = [NAME,RAM,vCPU,PORT,AUTO,PASSWD,[],[],NODE_NAME,NODE_IP]


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
	exit(0)



def VirtyDomDefineStatic(DOM_NAME,NODE_NAME):
	import xml.etree.ElementTree as ET

	NODE_IP = SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)

	try:
		tree = ET.parse(SP + '/define/' + DOM_NAME + '.xml') 
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

		STORAGE_PATH = SqlGetData("STORAGE_DATA","STORAGE_PATH",(NODE_NAME,STORAGE_NAME))
		IMG_PATH = STORAGE_PATH + DOM_NAME + IMG_NAME + '.img'

		ARCHIVE_NAME = storage.get('archive')
		ARCHIVE_PATH = SqlHitData("ARCHIVE_NAMEtoARCHIVE_PATH",ARCHIVE_NAME)
		XmlImgAdd(DOM_NAME,STORAGE_PATH,IMG_NAME,STORAGE_NAME,ARCHIVE_NAME)
		
		AnsibleFilecpInnode(NODE_IP,ARCHIVE_PATH,IMG_PATH)
		VirshDefine(DOM_NAME,NODE_IP)


def VirtyDomCheckStatic(DOM_NAME,NODE_NAME):
	import xml.etree.ElementTree as ET 

	NODE_IP = SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
	if NODE_IP == None:
		LogError("NG",NODE_NAME + " is not found")
		exit(1)
	else:
		LogSuccess("OK","Node is found")

	try:
		tree = ET.parse(SP + '/define/' + DOM_NAME + '.xml') 
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
		if SqlGetData("ARCHIVE_DATA","EXIST_STATUS",(NODE_NAME,storage.get('archive'))) == 1:
			LogError("NG","Archive dose not exits")
			exit(3)
		LogSuccess("OK",storage.get('archive') + " dose exits")	

		STORAGE_PATH = SqlGetData("STORAGE_DATA","STORAGE_PATH",(NODE_NAME,storage.get('storage')))
		if STORAGE_PATH == 1:
			LogError("NG","Storage dose not found in node")
			exit(4)
		LogSuccess("OK",str(storage.get('storage')) + " is exist")
	exit(0)
	# for img in IMG_DATAS:
	# 	IMG_NAME = img[0]
	# 	IMG_PATH = NODE_IMG + DOM_NAME + IMG_NAME + '.img'
	# 	ARCHIVE_NAME = img[1]
	# 	ARCHIVE_PATH = SqlHitData("ARCHIVE_NAMEtoARCHIVE_PATH",ARCHIVE_NAME)
	# 	AnsibleFilecpInnode(NODE_IP,ARCHIVE_PATH,IMG_PATH)
	# VirshDefine(DOM_NAME,NODE_IP)
	# exit(0)


################## Virty Undefine ##################
def VirtyImgDeleteStatic(DOM_NAME):
	import xml.etree.ElementTree as ET 
	NODE_NAME = SqlGetData("DOM_NAME","NODE_NAME",DOM_NAME)
	NODE_IP = SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
	conn = libvirt.open('qemu+ssh://' + NODE_IP + '/system')
	con = conn.lookupByName(DOM_NAME)
	root = ET.fromstring(con.XMLDesc())
	for disk in root.find('devices').findall('disk'):
		if disk.get("device") == "disk":
			IMG_PATH = disk.find("source").get("file","none")
			LogInfo("INFO",IMG_PATH + "    @" + NODE_NAME)
			AnsibleFiledeleteInnode(NODE_IP,IMG_PATH)
	LogSuccess("OK","All deletions are complete")
	exit(0)

def VirtyDomUndefineStatic(DOM_NAME):
	NODE_NAME = SqlGetData("DOM_NAME","NODE_NAME",DOM_NAME)	
	NODE_IP = SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
	LibvirtDomainUndefine(NODE_IP,DOM_NAME)
	SqlDeleteDomain([(DOM_NAME)])
	exit(0)


################## Virty Power ##################
def VirtyDomainStart(DOM_NAME):
	NODE_NAME = SqlGetData("DOM_NAME","NODE_NAME",DOM_NAME)
	NODE_IP = SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
	conn = libvirt.open('qemu+ssh://' + NODE_IP + '/system')
	con = conn.lookupByName(DOM_NAME)
	try:
		con.create()
	except libvirt.libvirtError as e:
		LogInfo("INFO",DOM_NAME + " " +e.args[0])
	LogSuccess("SUCC", DOM_NAME + " started")

def VirtyDomainAutostart(DOM_NAME):
	NODE_NAME = SqlGetData("DOM_NAME","NODE_NAME",DOM_NAME)
	NODE_IP = SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
	conn = libvirt.open('qemu+ssh://' + NODE_IP + '/system')
	con = conn.lookupByName(DOM_NAME)
	try:
		con.setAutostart(1)
	except libvirt.libvirtError as e:
		LogInfo("INFO",DOM_NAME + " " +e.args[0])
	LogSuccess("SUCC", DOM_NAME + " auto started")


def VirtyDomainShutdown(DOM_NAME):
	NODE_NAME = SqlGetData("DOM_NAME","NODE_NAME",DOM_NAME)
	NODE_IP = SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
	LibvirtDomainShutdown(NODE_IP,DOM_NAME)
	exit(0)

def VirtyDomainDestroy(DOM_NAME):
	NODE_NAME = SqlGetData("DOM_NAME","NODE_NAME",DOM_NAME)
	NODE_IP = SqlGetData("NODE_NAME","NODE_IP",NODE_NAME)
	LibvirtDomainDestroy(NODE_IP,DOM_NAME)


################## Bata ##################
def VirshCommandList():
	conn = libvirt.open('qemu:///system')
	names = conn.listDefinedDomains()
	print(names)
	clist = dir(conn)
	for item in clist:
		print(item)

def VirshStatus(DOM_NAMES):
	conn = libvirt.open('qemu:///system')
	for domname in DOM_NAMES:
		con = conn.lookupByName(domname)
		state, reason = con.state()
		if state == libvirt.VIR_DOMAIN_NOSTATE:
			print('The state is VIR_DOMAIN_NOSTATE')
		elif state == libvirt.VIR_DOMAIN_RUNNING:
			LogInfo(domname + " is Running reason code is " + str(reason))
		elif state == libvirt.VIR_DOMAIN_BLOCKED:
			print('The state is VIR_DOMAIN_BLOCKED')
		elif state == libvirt.VIR_DOMAIN_PAUSED:
			print('The state is VIR_DOMAIN_PAUSED')
		elif state == libvirt.VIR_DOMAIN_SHUTDOWN:
			print('The state is VIR_DOMAIN_SHUTDOWN')
		elif state == libvirt.VIR_DOMAIN_SHUTOFF:
			LogInfo(domname + " is Shutoff reason code is " + str(reason))
		elif state == libvirt.VIR_DOMAIN_CRASHED:
			print('The state is VIR_DOMAIN_CRASHED')
		elif state == libvirt.VIR_DOMAIN_PMSUSPENDED:
			print('The state is VIR_DOMAIN_PMSUSPENDED')
		else:
			print(' The state is unknown.')
	conn.close

def VirshDefine(DOM_NAME,NODE_IP):
	with open(SP + '/define/' + DOM_NAME + '.xml') as f:
		s = f.read()
		conn = libvirt.open('qemu+ssh://' + NODE_IP + '/system')
		conn.defineXML(s)

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
	datas = SqlPush("select * from kvm_storage where storage_name='" + STORAGE_NAME + "'")
	print('{0:12} {1:8} {2:8} {3:8} {4:8}'.format("NAME","NODE","DEVICE","TYPE","PATH"))
	for data in datas:
		NODE_IP = SqlGetData("NODE_NAME","NODE_IP",data[1])
		if NODE_IP == None:	break
		DF = VirtyInfoDir(NODE_IP,data[4])
		print('{0:12} {1:8} {2:8} {3:8} {4:8} {5:12} {6:4.0f} {7:4.0f} {8:4.0f} {9:4} {10:4}'
		.format(data[0], data[1], data[2], data[3], data[4], DF[0], int(DF[1])/1000000, int(DF[2])/1000000, int(DF[3])/1000000, DF[4], DF[5]))
	exit(0)


def VirtyNetworkAdd(NETWORK_NAME,NETWORK_BRIDGE,NETWORK_NODE):
	LogInfo("OK","Network added")
	SqlAddNetwork([(NETWORK_NAME,NETWORK_BRIDGE,NETWORK_NODE)])



################ Storage #################
def VirtyStorageAdd(STORAGE_NAME,STORAGE_NODE,STORAGE_DEVICE,STORAGE_TYPE,STORAGE_PATH):
	LogInfo("OK","Storage added")
	#virty storage add dir arhicve ssd chinon /kvm/archive
	SqlAddStorage([(STORAGE_NAME,STORAGE_NODE,STORAGE_DEVICE,STORAGE_TYPE,STORAGE_PATH)])


################ HELP ####################
def VirtyStorageAddHelp():
	print("\
	virty storage add archive NODE01 ssd dir /kvm/archive\n")
	exit(0)

def VirtyDomMakeHelp():
	print("\
	virty dom make base vm010 1024 2 auto pass \n \
	virty dom make nic bridge vm010 virbr1 \n \
	virty dom make img vm010 storage_vm CentOS7-1810 \n \
	virty dom define static vm010 Chinon \n")
	exit(0)

def VirtyDomMakeBaseHelp():
	print("\nHOW.")
	print("   virty dom make base (DomainNAME) (MEMORY) (CORE) (VNC_PORT) (VNCPassword)")
	print("\nEX.")
	print("   virty dom make base vm001 1024 2 auto Password\n‬")	
	exit(0)

def VirtyDomMakeNicHelp():
	print("\nHOW.")
	print("   virty dom make nic bridge (DomainNAME) (SOURCE)")
	print("\nEX.")
	print("   virty dom make nic bridge vm001 virbr0\n‬")	
	exit(0)

def VirtyNodeAddHelp():
	print("\n It is necessary to be able to connect with SSH in order to get memory and CPU information.")
	print("\nHOW.")
	print("   virty node add (NAME) (IP/DOMAIN)")
	print("\nEX.")
	print("   virty node add node01 192.168.0.1\n‬")
	exit(0)

def VirtyDomainMakeNomalHelp():
	print("\nHOW.")
	print("   virty dom make nomal (ArchiveNAME) (DomainNAME) (BridgeAddr) (VNCPASS) (MEMORY) (CORE) (POOL)")
	print("\nEX.")
	print("   virty dom make nomal CentOS chinon vm001 virbr0 5900 1024 2 none\n‬")	
	exit(0)

def VirtyHelp():
	print("\
	virty archive\n\
	virty storage\n\
	virty dom\n\
	virty develop \n\
	virty dom autostart CentOS_Virty \n\
	virty network \n\
	virty node \n\
 	")




if __name__ == "__main__":

	args = sys.argv
	argnum = len(args)

	if argnum == 1:
		VirtyHelp()
	elif argnum == 3:
		if args[1] == "dom" and args[2] == "make":VirtyDomMakeHelp()
		if args[1] == "node" and args[2] == "add":VirtyNodeAddHelp()
		if args[1] == "storage" and args[2] == "add":VirtyStorageAddHelp()
	elif argnum == 4:
		if args[1] == "dom" and args[2] == "make" and args[3] == "nomal":VirtyDomainMakeNomalHelp()
		if args[1] == "dom" and args[2] == "make" and args[3] == "base":VirtyDomMakeBaseHelp()
		if args[1] == "dom" and args[2] == "make" and args[3] == "nic":VirtyDomMakeNicHelp()






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
		if args[1] == "que" and args[2] == "delete": SqlDequeDomain(args[3])
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

	LogError("ErrOR","Command not funod")
