import sqlite3, vansible, os
from flask_login import UserMixin

SPATH = '/root/virty/main'
SQLFILE = SPATH + '/data.sqlite'

############################
# Select                   #
############################
def SqlGetAll(TABLE):
    con = sqlite3.connect(SQLFILE)
    cur = con.cursor()
    sql = 'select * from ' + TABLE
    return cur.execute(sql).fetchall()

def SqlGetAllSort(TABLE,COLUMN):
    con = sqlite3.connect(SQLFILE)
    cur = con.cursor()
    sql = 'select * from ' + TABLE + ' order by ' + COLUMN + ' asc'
    return cur.execute(sql).fetchall()
    
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
            GET = ExFetchall("select * from kvm_storage where storage_name='archive' and storage_node_name='" + HINT + "'")
            if GET == []:	return
            return GET[0][4].rstrip("/") + "/"
        elif DST == "NODE_DATA":
            GET = ExFetchall("select * from kvm_node where name='" + HINT + "'")
            if GET == []:	return
            return GET[0]

    elif SRC == "ARCHIVE_DATA":
        if DST == "EXIST_STATUS":
            GET = ExFetchall("select * from kvm_archive where archive_node_name='" + HINT[0] + "' and archive_name='" + HINT[1] + "'")
            if GET == []:	return 1
            return 0

    elif SRC == "STORAGE_DATA":
        if DST == "STORAGE_PATH":
            GET = ExFetchall("select * from kvm_storage where storage_node_name='" + HINT[0] + "' and storage_name='" + HINT[1] + "'")
            if GET == []:	return 1
            return GET[0][4].rstrip("/") + "/"

def Convert(SRC,DST,HINT):
    if SRC == "DOM_UUID" and DST == "NODE_NAME":
        for data in SqlGetAll("kvm_domain"):
            if data[5] == HINT:
                return data[2]
    if SRC == "DOM_NAME" and DST == "DOM_UUID":
        for data in SqlGetAll("kvm_domain"):
            if data[0] == HINT:
                return data[5]
    if SRC == "NODE_NAME" and DST == "NODE_IP":
        for data in SqlGetAll("kvm_node"):
            if data[0] == HINT:
                return data[1]
    if SRC == "NODE_NAME" and DST == "NETWORK_DATAS":
        return  ExFetchall("select * from kvm_network where network_node='" + HINT + "'")
    if SRC == "NODE_NAME" and DST == "NODE_STATUS":
        return int(SqlFetchall("select * from kvm_node where name=?",[(HINT)])[0][8])



############################
# DELETE                   #
############################
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

def NetworkDelete(NODE,SOURCE):
    con = sqlite3.connect(SQLFILE)
    cur = con.cursor()
    sql = 'delete from kvm_network where network_node = "' + NODE + '" and network_bridge = "' + SOURCE + '"'
    cur.execute(sql)
    con.commit()

def DomainDelete(UUID):
    con = sqlite3.connect(SQLFILE)
    cur = con.cursor()
    sql = 'delete from kvm_domain where domain_uuid = "' + UUID + '"'
    cur.execute(sql)
    con.commit()
############################
# SUM                      #
############################
def SqlSumNode():
    con = sqlite3.connect(SQLFILE)
    cur = con.cursor()
    sql = 'select sum(memory) from kvm_node'
    RAM = cur.execute(sql).fetchone()
    sql = 'select sum(core) from kvm_node'
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

    
############################
# ADD                      #
############################
def NetworkAdd(NETWORK_DICS):
    data = []
    
    for temp in NETWORK_DICS:
        if temp['dhcp'] == []:
            temp['dhcp'] = "disable"
        else:
            temp['dhcp'] = "enable"
        SEND = [temp['name'],temp['bridge'],temp['uuid'],temp['node'],temp['type'],temp['dhcp']]
        data.append(SEND)
    SqlCommit("replace into kvm_network (name,bridge,uuid,node,type,dhcp) values (?,?,?,?,?,?)",data)


def SqlAddNode(NODE_DATAS):
    con = sqlite3.connect(SQLFILE)
    cur = con.cursor()
    sql = ''
    cur.executemany(sql, NODE_DATAS)
    con.commit()
    
    con.close()
    vansible.AnsibleNodelistInit()
    
def StorageAdd(STORAGE_DATAS):
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
        
def SqlAddArchive(ARCHIVE_DATAS):
    con = sqlite3.connect(SQLFILE)
    cur = con.cursor()
    sql = 'replace into kvm_archive (archive_name, archive_path, archive_node_name) values (?,?,?)'
    cur.executemany(sql, ARCHIVE_DATAS)
    con.commit()
    
    con.close()

def ImageAdd(IMG_DATAS):
    con = sqlite3.connect(SQLFILE)
    cur = con.cursor()
    sql = 'replace into kvm_img (name, node, pool, capa, allocation, physical, path) values (?,?,?,?,?,?,?)'
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


############################
# UPDATE                   #
############################
def SqlUpdateDomain(DOM_DIC):
    con = sqlite3.connect(SQLFILE)
    cur = con.cursor()
    sql = 'replace into kvm_domain (domain_name, domain_status, domain_node_name, domain_core,domain_memory,domain_uuid, domain_type,domain_os) values (?,?,?,?,?,?,?,?)'
    
    DOM_DATA = [(
        DOM_DIC['name'],
        DOM_DIC['power'],
        DOM_DIC['node-name'],
        DOM_DIC['vcpu'],
        DOM_DIC['memory'],
        DOM_DIC['uuid'],
        "unknown",
        "test"
    )]
    cur.executemany(sql, DOM_DATA)
    con.commit()
    con.close()

def NetworkListUpdate(NET_DIC_LIST):
    con = sqlite3.connect(SQLFILE)
    cur = con.cursor()
    sql = 'replace into kvm_network (network_name,network_bridge,network_uuid,network_node,network_type,network_dhcp) values (?,?,?,?,?,?)'
    
    NET_DATA = []

    for NET_DIC in NET_DIC_LIST:
        if NET_DIC['dhcp'] == []:
            NET_DIC['dhcp'] = "disable"
        else:
            NET_DIC['dhcp'] = "enable"
        TEMP = [
            NET_DIC['name'],
            NET_DIC['bridge'],
            NET_DIC['uuid'],
            NET_DIC['node'],
            NET_DIC['type'],
            NET_DIC['dhcp']
        ]
        NET_DATA.append(TEMP)
    cur.executemany(sql, NET_DATA)
    con.commit()
    con.close()

def UpdateImage(DIC_LIST):
    con = sqlite3.connect(SQLFILE)
    cur = con.cursor()
    sql = 'replace into kvm_img (img_name, img_archive_name, img_domain_name,img_node_name) values (?,?,?,?)'
    
    DATA = []

    for DIC in DIC_LIST:
        TEMP = [
            DIC['name'],
            DIC['archive'],
            DIC['domain'],
            DIC['node']
        ]
        DATA.append(TEMP)
    cur.executemany(sql, DATA)
    con.commit()
    con.close()

def UpdateStorage(DIC_LIST):
    con = sqlite3.connect(SQLFILE)
    cur = con.cursor()
    sql = 'replace into kvm_storage(storage_name, storage_node_name, storage_uuid, storage_capacity, storage_available,storage_device, storage_type, storage_path) values (?,?,?,?,?,?,?,?)'
    
    DATA = []

    for DIC in DIC_LIST:
        TEMP = [
            DIC['name'],
            DIC['node'],
            DIC['uuid'],
            DIC['capacity'],
            DIC['available'],
            DIC['device'],
            DIC['type'],
            DIC['path']
        ]
        DATA.append(TEMP)
    cur.executemany(sql, DATA)
    con.commit()
    con.close()

def UpdateDomainStatus(NODES,DOMAINS,CODE):
    con = sqlite3.connect(SQLFILE)
    cur = con.cursor()
    for NODE in NODES:
        sql = 'UPDATE kvm_domain SET domain_status=? WHERE domain_node_name=?'
        cur.executemany(sql, [(int(CODE),NODE)])
    for UUID in DOMAINS:
        sql = 'UPDATE kvm_domain SET domain_status=? WHERE domain_uuid=?'
        cur.executemany(sql, [(int(CODE),UUID)])
    con.commit()

def UpdateNodeStatus(NODES,CODE):
    con = sqlite3.connect(SQLFILE)
    cur = con.cursor()
    for NODE in NODES:
        sql = 'UPDATE kvm_node SET status=? WHERE name=?'
        cur.executemany(sql, [(int(CODE),NODE)])
    con.commit()

############################
# QUE                      #
############################

def Queuing(QUE_OBJECT,QUE_METHOD,QUE_JSON):
    con = sqlite3.connect(SQLFILE)
    cur = con.cursor()
    sql = "insert into kvm_que (que_time, que_status, que_object, que_method, que_json, que_mesg) values (datetime('now', 'localtime'),?,?,?,?,?)"
    
    quedata = [[]]
    quedata[0].append(str("init"))
    quedata[0].append(str(QUE_OBJECT))
    quedata[0].append(str(QUE_METHOD))
    quedata[0].append(str(QUE_JSON))
    quedata[0].append(str("Not started"))

    cur.executemany(sql, quedata)
    con.commit()
    con.close()

def Dequeuing(QUE_ID,QUE_STATUS,QUE_MESG):
    con = sqlite3.connect(SQLFILE)
    cur = con.cursor()
    sql = 'UPDATE kvm_que SET que_status=?, que_mesg=? WHERE que_id=?'
    cur.executemany(sql, [(QUE_STATUS,QUE_MESG,QUE_ID)])
    con.commit()
    
def SqlQueuget(QUE_STATUS):
    con = sqlite3.connect(SQLFILE)
    cur = con.cursor()
    sql = 'select * from kvm_que where que_status ="'+QUE_STATUS+'"'
    data = cur.execute(sql).fetchall()
    return data

def QueueUpdate(QUE_ID,QUE_STATUS,QUE_MESG):
    con = sqlite3.connect(SQLFILE)
    cur = con.cursor()
    sql = 'UPDATE kvm_que SET que_status=?, que_mesg=? WHERE que_id=?'
    cur.executemany(sql, [(QUE_STATUS,QUE_MESG,QUE_ID)])
    con.commit()
    
def SqlDeleteAll(TABLE_NAME):
    con = sqlite3.connect(SQLFILE)
    cur = con.cursor()
    sql = 'delete from '+ TABLE_NAME +';'
    cur.execute(sql)
    con.commit()	
    return 0

def QueueUpdateTime(QUE_ID,QUE_TIME):
    SqlCommit("UPDATE kvm_que SET run=? WHERE que_id=?",[(QUE_TIME,QUE_ID)])



############################
# USER                     #
############################
class User(UserMixin):
    def __init__(self, userid, username, password):
        self.id = userid
        self.username = username
        self.password = password

    def __str__(self):
        data = {}
        data['name'] = self.username
        data['id'] = self.id
        return str(self.id)

    def get_id(self):
        return self.id

def UserGet(username):
    user = SqlFetchall("select * from kvm_user where userid=?",[(username)])
    if len(user) == 0:
        return None
    elif len(user) >1:
        return None
    else:
        user = user[0]
        return User(user[0],user[1],user[2])


############################
# RAW                      #
############################
def SqlFetchall(SQL,DATA):
    con = sqlite3.connect(SQLFILE)
    cur = con.cursor()
    return cur.execute(SQL, DATA).fetchall()

def SqlCommit(SQL,DATA):
    con = sqlite3.connect(SQLFILE)
    cur = con.cursor()
    cur.executemany(SQL,DATA)
    con.commit()
    con.close()

def ExFetchall(SQL):
    con = sqlite3.connect(SQLFILE)
    cur = con.cursor()
    get = cur.execute(SQL).fetchall()
    return get

def SqlInit():
    try:
        os.remove(SQLFILE)
    except:
        pass
    con = sqlite3.connect(SQLFILE)
    cur = con.cursor()
    cur.execute('create table if not exists kvm_node (name, ip, core, memory, cpugen, os_like, os_name, os_version, status, qemu, libvirt, primary key (name))')
    cur.execute('create table if not exists kvm_user (userid, name, password, primary key (userid))')
    cur.execute('create table if not exists kvm_group (groupid, name, owner, primary key (groupid))')
    cur.execute('create table if not exists kvm_que (que_id integer primary key,que_time ,que_status,que_object,que_method, que_json, que_mesg, run)')
    cur.execute('create table if not exists kvm_network (name,bridge,uuid,node,type,dhcp,primary key (name,node))')
    cur.execute('create table if not exists kvm_storage (storage_name, storage_node_name, storage_uuid, storage_capacity, storage_available,storage_device, storage_type, storage_path, primary key (storage_name, storage_node_name))')
    cur.execute('create table if not exists kvm_domain (domain_name, domain_status, domain_node_name, domain_core,domain_memory,domain_uuid, domain_type,domain_os,primary key (domain_name,domain_node_name))')
    cur.execute('create table if not exists kvm_domainpool (domainpool_name, domainpool_node_name, domainpool_setram)')
    cur.execute('create table if not exists kvm_archive (archive_name, archive_path, archive_node_name,primary key (archive_name,archive_node_name))')
    cur.execute('create table if not exists kvm_img (name, node, pool, capa, allocation, physical, path, domain, primary key (name,node,pool))')
    cur.execute("insert into kvm_group VALUES (:groupid, :name, :owner)",("admin","admin","admin"))
    cur.execute("insert into kvm_user VALUES (:userid, :name, :password)",("admin","admin","$2b$12$2wXcPezIzrE0BD0WngUGSOrARvInU88Hk/BLWxcE1JYaKeaCljBvG"))
    con.commit()
    cur.close()
    con.close()