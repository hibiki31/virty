import sqlite3, vansible, os

SPATH = '/root/virty/main'
SQLFILE = SPATH + '/data.sqlite'

def SqlClearL2lesspool():
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	cur.execute('delete from kvm_l2lesspool')
	con.commit()
	
	con.close()

def SqlDeleteNode(NODENAMES):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	for node in NODENAMES:
		sql = 'delete from kvm_node where node_name = "' + node + '"'
		cur.execute(sql)
	con.commit()
	
	
	vansible.AnsibleNodelistInit()

def SqlDeleteDomain(DOM_NAMES):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	for dom in DOM_NAMES:
		sql = 'delete from kvm_domain where domain_name = "' + dom + '"'
		cur.execute(sql)
	con.commit()
	
	

def SqlGetVncport():
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'select * from kvm_vncpool'
	return cur.execute(sql).fetchall()


def SqlGetAll(TABLE):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'select * from ' + TABLE
	return cur.execute(sql).fetchall()


def SqlGetVncportFree(NODENAME):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'select min(vncpool_port) from kvm_vncpool where vncpool_domain_name="none" and vncpool_node_name ="' + NODENAME +'"'
	return cur.execute(sql).fetchall()


def SqlGetDomainpool():
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'select * from kvm_domainpool'
	return cur.execute(sql).fetchall()
	


def SqlGetArchive():
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'select * from kvm_archive'
	return cur.execute(sql).fetchall()
	


def SqlGetDomain():
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'select * from kvm_domain'
	return cur.execute(sql).fetchall()
	
	

def SqlSumNode():
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'select sum(node_memory) from kvm_node'
	RAM = cur.execute(sql).fetchone()
	sql = 'select sum(node_core) from kvm_node'
	CORE = cur.execute(sql).fetchone()
	if CORE[0] == None:CORE = 0
	else:CORE = CORE[0]
	if RAM[0] == None:RAM = 0
	else:RAM = RAM[0]	
	return [RAM,CORE]
	
	

def SqlSumDomain():
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'select sum(domain_memory) from kvm_domain'
	RAM = cur.execute(sql).fetchone()
	sql = 'select sum(domain_core) from kvm_domain'
	CORE = cur.execute(sql).fetchone()
	if CORE[0] == None:CORE = 0
	else:CORE = CORE[0]
	if RAM[0] == None:RAM = 0
	else:RAM = RAM[0]
	return [RAM,CORE]

	

def SqlGetL2less():
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'select * from kvm_l2lesspool'
	return cur.execute(sql).fetchall()

	
	

def SqlGetL2lessFree():
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'select * from kvm_l2lesspool where l2lesspool_domain_name="none"'
	return cur.execute(sql).fetchall()

def SqlAddNode(NODE_DATAS):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'replace into kvm_node (node_name, node_ip, node_core, node_memory, node_cpugen) values (?,?,?,?,?)'
	cur.executemany(sql, NODE_DATAS)
	con.commit()
	
	con.close()
	vansible.AnsibleNodelistInit()
	

def SqlAddStorage(STORAGE_DATAS):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'replace into kvm_storage (storage_name, storage_node_name, storage_device, storage_type, storage_path) values (?,?,?,?,?)'
	cur.executemany(sql, STORAGE_DATAS)
	con.commit()
	
	con.close()
	vansible.AnsibleNodelistInit()
	

def SqlAddNetwork(NETWORK_DATAS):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'replace into kvm_network (network_name,network_bridge,network_node) values (?,?,?)'
	cur.executemany(sql, NETWORK_DATAS)
	con.commit()
	
	con.close()
		

def SqlAddVncpool(VNC_DATAS):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'replace into kvm_vncpool (vncpool_port, vncpool_domain_name, vncpool_passwd, vncpool_node_name) values (?,?,?,?)'
	cur.executemany(sql, VNC_DATAS)
	con.commit()
	
	con.close()

def SqlAddL2lesspool(POOL_DATAS):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'replace into kvm_l2lesspool (l2lesspool_name, l2lesspool_ip, l2lesspool_gw, l2lesspool_domain_name, l2lesspool_node_name) values (?,?,?,?,?)'
	cur.executemany(sql, POOL_DATAS)
	con.commit()
	
	con.close()
	vansible.AnsibleNodelistInit()

def SqlAddArchive(ARCHIVE_DATAS):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'replace into kvm_archive (archive_name, archive_path, archive_node_name) values (?,?,?)'
	cur.executemany(sql, ARCHIVE_DATAS)
	con.commit()
	
	con.close()

def SqlAddImg(IMG_DATAS):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'replace into kvm_img (img_name, img_archive_name, img_domain_name,img_node_name) values (?,?,?,?)'
	cur.executemany(sql, IMG_DATAS)
	con.commit()
	
	con.close()

def SqlAddDomain(DOMAIN_DATAS):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'replace into kvm_domain (domain_name, domain_status, domain_node_name, domain_core,domain_memory,domain_uuid, domain_type,domain_os) values (?,?,?,?,?,?,?,?)'
	cur.executemany(sql, DOMAIN_DATAS)
	con.commit()
	
	con.close()

### QUE ###
def SqlQueuing(QUE_TYPE,DOMAIN_DATAS):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = "insert into kvm_que (que_time, que_status, que_progress, que_type, que_json) values (datetime('now', 'localtime'),?,?,?,?)"
	values = 'values ("'+QUE_TYPE+'","'+str(DOMAIN_DATAS)+'");'

	quedata = [[]]
	#quedata[0].append(str("now"))
	quedata[0].append(str("init"))
	quedata[0].append(str("0"))
	quedata[0].append(str(QUE_TYPE))
	quedata[0].append(str(DOMAIN_DATAS))



	print(quedata)
	cur.executemany(sql, quedata)
	con.commit()
	con.close()

def SqlDequeuing(QUE_ID,QUE_STATUS,QUE_PROGRESS):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'UPDATE kvm_que SET que_status=?, que_progress=? WHERE que_id=?'
	cur.executemany(sql, [(QUE_STATUS,QUE_PROGRESS,QUE_ID)])
	con.commit()
	
def SqlQueuget():
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'select * from kvm_que where que_status = "init"'
	return cur.execute(sql).fetchall()
	
def SqlDeleteAll(TABLE_NAME):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'delete from '+ TABLE_NAME +';'
	cur.execute(sql)
	con.commit()	
	return 0

def	SqlAddDomainpool(POOL_DATAS):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'replace into kvm_domainpool (domainpool_name,domainpool_node_name,domainpool_setram) values (?,?,?)'
	cur.executemany(sql, POOL_DATAS)
	con.commit()
	
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

def Convert(SRC,DST,HINT):
	if SRC == "DOM_UUID" and DST == "NODE_NAME":
		for data in SqlGetAll("kvm_domain"):
			if data[5] == HINT:
				return data[2]
	if SRC == "NODE_NAME" and DST == "NODE_IP":
		for data in SqlGetAll("kvm_node"):
			if data[0] == HINT:
				return data[1]
	if SRC == "NODE_NAME" and DST == "NETWORK_DATAS":
		return  SqlPush("select * from kvm_network where network_node='" + HINT + "'")





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

def SqlHitNodeName(DOM_NAME):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'select node from domain where domain ="' + DOM_NAME +'"'
	for hit in cur.execute(sql):
		get = hit[0]
	return get
	

def SqlHitNodeIp(NODENAME):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'select ip from node where node ="' + NODENAME +'"'
	for hit in cur.execute(sql):
		get = hit[0]
	return get
	

def SqlHitImg(DOM_NAME):
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	sql = 'select * from kvm_img where img_domain_name ="' + DOM_NAME +'"'
	return cur.execute(sql).fetchall()
	
	
def SqlInit():
	try:
		os.remove(SQLFILE)
	except:
		pass
	con = sqlite3.connect(SQLFILE)
	cur = con.cursor()
	cur.execute('create table if not exists kvm_node (node_name primary key, node_ip, node_core, node_memory, node_cpugen)')
	cur.execute('create table if not exists kvm_que (que_id integer primary key,que_time ,que_status,que_progress,que_type, que_json)')
	cur.execute('create table if not exists kvm_network (network_name,network_bridge,network_node,primary key (network_bridge,network_node))')
	cur.execute('create table if not exists kvm_storage (storage_name, storage_node_name, storage_device, storage_type, storage_path, primary key (storage_name, storage_node_name))')
	cur.execute('create table if not exists kvm_domain (domain_name, domain_status, domain_node_name, domain_core,domain_memory,domain_uuid, domain_type,domain_os,primary key (domain_name,domain_node_name))')
	cur.execute('create table if not exists kvm_vncpool (vncpool_port, vncpool_domain_name, vncpool_passwd, vncpool_node_name, primary key (vncpool_port,vncpool_node_name))')
	cur.execute('create table if not exists kvm_domainpool (domainpool_name, domainpool_node_name, domainpool_setram)')
	cur.execute('create table if not exists kvm_archive (archive_name, archive_path, archive_node_name,primary key (archive_name,archive_node_name))')
	cur.execute('create table if not exists kvm_img (img_name, img_archive_name, img_domain_name,img_node_name,primary key (img_name,img_domain_name))')
	cur.execute('create table if not exists kvm_l2lesspool (l2lesspool_name primary key, l2lesspool_ip, l2lesspool_gw, l2lesspool_domain_name, l2lesspool_node_name)')
	con.commit()
	cur.close()
	con.close()