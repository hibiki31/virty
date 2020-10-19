import sqlite3, os
from flask_login import UserMixin
from module import setting, vansible


############################
# Select                   #
############################
def SqlGetAll(TABLE):
    con = sqlite3.connect(setting.database_path)
    cur = con.cursor()
    sql = 'select * from ' + TABLE
    return cur.execute(sql).fetchall()

def SqlGetAllSort(TABLE,COLUMN):
    con = sqlite3.connect(setting.database_path)
    cur = con.cursor()
    sql = 'select * from ' + TABLE + ' order by ' + COLUMN + ' asc'
    return cur.execute(sql).fetchall()
    
def SqlGetData(SRC,DST,HINT):
    if SRC == "DOM_NAME":
        if DST == "NODE_NAME":
            for data in SqlGetAll("domain"):
                if data[0] == HINT:
                    return data[2]
    elif SRC == "NODE_NAME":
        if DST == "NODE_IP":
            for data in SqlGetAll("node"):
                if data[0] == HINT:
                    return data[1]
        elif DST == "ARCHIVE_DIR":
            GET = ExFetchall("select * from storage where name='archive' and node_name='" + HINT + "'")
            if GET == []:	return
            return GET[0][4].rstrip("/") + "/"
        elif DST == "NODE_DATA":
            GET = ExFetchall("select * from node where name='" + HINT + "'")
            if GET == []:	return
            return GET[0]

    elif SRC == "ARCHIVE_DATA":
        if DST == "EXIST_STATUS":
            GET = ExFetchall("select * from archive where archive_node_name='" + HINT[0] + "' and archive_name='" + HINT[1] + "'")
            if GET == []:	return 1
            return 0

    elif SRC == "STORAGE_DATA":
        if DST == "STORAGE_PATH":
            GET = ExFetchall("select * from storage where node_name='" + HINT[0] + "' and name='" + HINT[1] + "'")
            if GET == []:	return 1
            return GET[0][4].rstrip("/") + "/"

def Convert(SRC,DST,HINT):
    if SRC == "DOM_UUID" and DST == "NODE_NAME":
        for data in SqlGetAll("domain"):
            if data[5] == HINT:
                return data[2]
    if SRC == "DOM_NAME" and DST == "DOM_UUID":
        for data in SqlGetAll("domain"):
            if data[0] == HINT:
                return data[5]
    if SRC == "NODE_NAME" and DST == "NODE_IP":
        for data in SqlGetAll("node"):
            if data[0] == HINT:
                return data[1]
    if SRC == "NODE_NAME" and DST == "NETWORK_DATAS":
        return  ExFetchall("select * from network where network_node='" + HINT + "'")
    if SRC == "NODE_NAME" and DST == "NODE_STATUS":
        return int(RawFetchall("select * from node where name=?",[(HINT)])[0][8])



def SqlDeleteNode(NODENAMES):
    con = sqlite3.connect(setting.database_path)
    cur = con.cursor()
    for node in NODENAMES:
        sql = 'delete from node where node_name = "' + node + '"'
        cur.execute(sql)
    con.commit()
    vansible.AnsibleNodelistInit()

def SqlDeleteDomain(DOM_NAMES):
    con = sqlite3.connect(setting.database_path)
    cur = con.cursor()
    for dom in DOM_NAMES:
        sql = 'delete from domain where name = "' + dom + '"'
        cur.execute(sql)
    con.commit()

def NetworkDelete(NODE,SOURCE):
    con = sqlite3.connect(setting.database_path)
    cur = con.cursor()
    sql = 'delete from network where network_node = "' + NODE + '" and network_bridge = "' + SOURCE + '"'
    cur.execute(sql)
    con.commit()

def DomainDelete(UUID):
    con = sqlite3.connect(setting.database_path)
    cur = con.cursor()
    sql = 'delete from domain where uuid = "' + UUID + '"'
    cur.execute(sql)
    con.commit()
############################
# SUM                      #
############################
def SqlSumNode():
    con = sqlite3.connect(setting.database_path)
    cur = con.cursor()
    sql = 'select sum(memory) from node'
    RAM = cur.execute(sql).fetchone()
    sql = 'select sum(core) from node'
    CORE = cur.execute(sql).fetchone()
    if CORE[0] == None:CORE = 0
    else:CORE = CORE[0]
    if RAM[0] == None:RAM = 0
    else:RAM = RAM[0]	
    return [RAM,CORE]

def SqlSumDomain():
    con = sqlite3.connect(setting.database_path)
    cur = con.cursor()
    sql = 'select sum(memory) from dom'
    RAM = cur.execute(sql).fetchone()
    sql = 'select sum(core) from dom'
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
    RawCommits("replace into network (name,bridge,uuid,node,type,dhcp) values (?,?,?,?,?,?)",data)


def SqlAddNode(NODE_DATAS):
    con = sqlite3.connect(setting.database_path)
    cur = con.cursor()
    sql = ''
    cur.executemany(sql, NODE_DATAS)
    con.commit()
    
    con.close()
    vansible.AnsibleNodelistInit()
    
def StorageAdd(STORAGE_DATAS):
    con = sqlite3.connect(setting.database_path)
    cur = con.cursor()
    sql = 'replace into storage (name, node_name, device, type, path) values (?,?,?,?,?)'
    cur.executemany(sql, STORAGE_DATAS)
    con.commit()
    
    con.close()
    vansible.AnsibleNodelistInit()
    
def SqlAddNetwork(NETWORK_DATAS):
    con = sqlite3.connect(setting.database_path)
    cur = con.cursor()
    sql = 'replace into network (network_name,network_bridge,network_node) values (?,?,?)'
    cur.executemany(sql, NETWORK_DATAS)
    con.commit()
    
    con.close()
        
def SqlAddArchive(ARCHIVE_DATAS):
    con = sqlite3.connect(setting.database_path)
    cur = con.cursor()
    sql = 'replace into archive (archive_name, archive_path, archive_node_name) values (?,?,?)'
    cur.executemany(sql, ARCHIVE_DATAS)
    con.commit()
    
    con.close()

def ImageAdd(IMG_DATAS):
    con = sqlite3.connect(setting.database_path)
    cur = con.cursor()
    sql = 'replace into img (name, node, pool, capa, allocation, physical, path) values (?,?,?,?,?,?,?)'
    cur.executemany(sql, IMG_DATAS)
    con.commit()
    
    con.close()

def SqlAddDomain(DOMAIN_DATAS):
    con = sqlite3.connect(setting.database_path)
    cur = con.cursor()
    sql = 'replace into domain (name, status, node_name, core,memory,uuid, type,os) values (?,?,?,?,?,?,?,?)'
    cur.executemany(sql, DOMAIN_DATAS)
    con.commit()
    
    con.close()


############################
# UPDATE                   #
############################
def SqlUpdateDomain(DOM_DIC):
    con = sqlite3.connect(setting.database_path)
    cur = con.cursor()
    sql = 'replace into domain (name, status, node_name, core,memory,uuid, type,os) values (?,?,?,?,?,?,?,?)'
    
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
    con = sqlite3.connect(setting.database_path)
    cur = con.cursor()
    sql = 'replace into network (network_name,network_bridge,network_uuid,network_node,network_type,network_dhcp) values (?,?,?,?,?,?)'
    
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
    con = sqlite3.connect(setting.database_path)
    cur = con.cursor()
    sql = 'replace into img (img_name, img_archive_name, img_domain_name,img_node_name) values (?,?,?,?)'
    
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
    con = sqlite3.connect(setting.database_path)
    cur = con.cursor()
    sql = 'replace into storage(name, node_name, uuid, capacity, available,device, type, path) values (?,?,?,?,?,?,?,?)'
    
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

def DomainStatusUpdate(NODES,DOMAINS,CODE):
    con = sqlite3.connect(setting.database_path)
    cur = con.cursor()
    for NODE in NODES:
        sql = 'UPDATE domain SET status=? WHERE node_name=?'
        cur.executemany(sql, [(int(CODE),NODE)])
    for UUID in DOMAINS:
        sql = 'UPDATE domain SET status=? WHERE uuid=?'
        cur.executemany(sql, [(int(CODE),UUID)])
    con.commit()

def NodeStatusUpdate(NODES,CODE):
    con = sqlite3.connect(setting.database_path)
    cur = con.cursor()
    for NODE in NODES:
        sql = 'UPDATE node SET status=? WHERE name=?'
        cur.executemany(sql, [(int(CODE),NODE)])
    con.commit()

############################
# QUE                      #
############################

def Queuing(QUE_OBJECT,QUE_METHOD,QUE_JSON):
    con = sqlite3.connect(setting.database_path)
    cur = con.cursor()
    sql = "insert into queue (post_time, status, object, method, json, message) values (datetime('now', 'localtime'),?,?,?,?,?)"
    
    quedata = [[]]
    quedata[0].append(str("init"))
    quedata[0].append(str(QUE_OBJECT))
    quedata[0].append(str(QUE_METHOD))
    quedata[0].append(str(QUE_JSON))
    quedata[0].append(str("Not started"))

    cur.executemany(sql, quedata)
    que_id = cur.execute('select id from queue where id = last_insert_rowid()').fetchall()
    con.commit()
    con.close()
    return {"que-id":que_id[0]}

def Dequeuing(QUE_ID,QUE_STATUS,QUE_MESG):
    con = sqlite3.connect(setting.database_path)
    cur = con.cursor()
    sql = 'UPDATE queue SET status=?, message=? WHERE id=?'
    cur.executemany(sql, [(QUE_STATUS,QUE_MESG,QUE_ID)])
    con.commit()
    
def SqlQueuget(QUE_STATUS):
    con = sqlite3.connect(setting.database_path)
    cur = con.cursor()
    sql = 'select * from queue where status ="'+QUE_STATUS+'"'
    data = cur.execute(sql).fetchall()
    return data

def QueueUpdate(QUE_ID,QUE_STATUS,QUE_MESG):
    con = sqlite3.connect(setting.database_path)
    cur = con.cursor()
    sql = 'UPDATE queue SET status=?, message=? WHERE id=?'
    cur.executemany(sql, [(QUE_STATUS,QUE_MESG,QUE_ID)])
    con.commit()
    
def SqlDeleteAll(TABLE_NAME):
    con = sqlite3.connect(setting.database_path)
    cur = con.cursor()
    sql = 'delete from '+ TABLE_NAME +';'
    cur.execute(sql)
    con.commit()	
    return 0

def QueueUpdateTime(QUE_ID,QUE_TIME):
    RawCommit("UPDATE queue SET run_time=? WHERE id=?",[QUE_TIME,QUE_ID])

############################
# LONG                     #
############################
def imgListAdmin():
    SQL = (
        "select img.name,img.node,img.pool,img.capa,img.allocation,img.physical,img.path,domain.name,count(*),archive_img.archive_id "
        "from img "
        "left join domain_drive on img.path=domain_drive.source "
        "left join domain  on domain_drive.dom_uuid=domain.uuid and img.node=domain.node_name "
        "left join archive_img on img.name=archive_img.name and img.node=archive_img.node "
        "group by img.node,img.path;"
    )
    return RawFetchall(SQL,[])

def imgListSelectAdmin(node,pool):
    SQL = (
        "select img.name,img.node,img.pool,img.capa,img.allocation,img.physical,img.path,domain.name,count(*),archive_img.archive_id "
        "from img "
        "left join domain_drive on img.path=domain_drive.source "
        "left join domain  on domain_drive.dom_uuid=domain.uuid and img.node=domain.node_name "
        "left join archive_img on img.name=archive_img.name and img.node=archive_img.node "
        "where img.node=? and img.pool=? "
        "group by img.node,img.path;"
    )
    return RawFetchall(SQL,[node,pool])




############################
# USER                     #
############################
class User(UserMixin):
    def __init__(self, user_id, passwd):
        self.id = user_id
        self.passwd = passwd
        self.groups = RawFetchall("select group_id from users_groups where user_id=?",[user_id])
        self.isadmin = ("admin",) in self.groups

    def __str__(self):
        return str(self.id)

    def get_id(self):
        return self.id

def UserGet(username):
    user = RawFetchall("select * from users where id=?",[(username)])
    if len(user) == 0:
        return None
    elif len(user) >1:
        return None
    else:
        user = user[0]
        return User(user[0],user[1])

############################
# Domain                   #
############################
def DomainInterfaceAdd(DATA):
    SQL = "replace into domain_interface (dom_uuid, type, mac, target, source, network, is_updating) values (?,?,?,?,?,?,'false')"
    RawCommit(SQL,DATA)
    
def DomainDriveAdd(DATA):
    SQL = "replace into domain_drive (dom_uuid, device, type, source, target, is_updating) values (?,?,?,?,?,'false')"
    RawCommit(SQL,DATA)

def DataStatusIsUpdating(TABLE):
    SQL = "update "+ TABLE +" set is_updating='true'"
    RawCommit(SQL,[])

def DataStatusDelete(TABLE):
    SQL = "delete from "+ TABLE +" where is_updating='true'"
    RawCommit(SQL,[])

############################
# Pool                     #
############################
def PoolListGet(NODE):
    SQL = (" select *,count(*) from storage left join img on storage.node_name=img.node and storage.name=img.pool and storage.node_name=img.node where node_name=? group by storage.name,storage.node_name;")
    if NODE == True:
        return RawFetchall(SQL,[])
    else:
        return RawFetchall(SQL,[NODE])

############################
# RAW                      #
############################
def ExFetchall(SQL):
    con = sqlite3.connect(setting.database_path)
    cur = con.cursor()
    get = cur.execute(SQL).fetchall()
    return get

def RawCommits(SQL,DATAS):
    con = sqlite3.connect(setting.database_path)
    cur = con.cursor()
    cur.executemany(SQL,DATAS)
    con.commit()

def RawCommit(SQL,DATA):
    con = sqlite3.connect(setting.database_path)
    cur = con.cursor()
    cur.execute(SQL,DATA)
    con.commit()

def RawFetchall(SQL,DATA):
    print(setting.database_path)
    con = sqlite3.connect(setting.database_path)
    cur = con.cursor()
    return cur.execute(SQL,DATA).fetchall()

def SqlInit():
    try:
        os.remove(setting.database_path)
    except:
        pass
    con = sqlite3.connect(setting.database_path)
    cur = con.cursor()
    cur.execute('create table domain (name, status, node_name, core, memory, uuid, type, os, primary key (name, node_name))')
    cur.execute('create table domain_interface (dom_uuid, type, mac, target, source, network, is_updating, primary key (dom_uuid, mac))')
    cur.execute('create table domain_drive (dom_uuid, device, type, target, source, is_updating, primary key (dom_uuid, target))')
    cur.execute('create table domain_owner (dom_uuid, group_id, user_id, primary key (dom_uuid))')
    cur.execute('create table node (name, ip, core, memory, cpugen, os_like, os_name, os_version, status, qemu, libvirt, primary key (name))')
    cur.execute('create table users (id, password, primary key (id))')
    cur.execute('create table groups (id, primary key (id))')
    cur.execute('create table users_groups (user_id,group_id,primary key (user_id,group_id))')
    cur.execute('create table queue (id primary key, post_time , user_id, status, resource, object, method, json, message, run_time)')
    cur.execute('create table network (name,bridge,uuid,node,type,dhcp,primary key (name,node))')
    cur.execute('create table storage (name, node_name, uuid, capacity, available,device, type, path, primary key (name, node_name))')
    cur.execute('create table dompool (domainpool_name, domainpool_node_name, domainpool_setram)')
    cur.execute('create table archive (id, os, version, comment, url, icon, user, password, primary key (id))')
    cur.execute('create table archive_img (archive_id, name, node, pool, primary key (archive_id, name, node, pool))')
    cur.execute('create table img (name, node, pool, capa, allocation, physical, path, primary key (name,node,pool))')
    cur.execute("insert into users (id, password) values (?,?)",("admin","$2b$12$2wXcPezIzrE0BD0WngUGSOrARvInU88Hk/BLWxcE1JYaKeaCljBvG"))
    cur.execute("insert into users_groups (user_id,group_id) values (?,?)",["admin","admin"])
    cur.execute("insert into groups (id) values (?)",["admin"])
    con.commit()
    cur.close()
    con.close()