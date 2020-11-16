import os
import sqlite3
import json
import humps
import uuid

from module import setting
from module import xmllib


from pydantic import BaseModel
from typing import List, Optional


class ImageModel(BaseModel):
    xml: str


class StorageModel(BaseModel):
    active: bool
    auto_start: bool
    status: int
    xml: str
    images: List[ImageModel]


class VirtyUser():
    def __init__(self, user_id, password):
        self.user_id = str(user_id)
        self.password = password
        self.groups = []
        self.is_admin = False

        for group in raw_fetchall("select group_id from users_groups where user_id=?",[user_id]):
            self.groups.append(group.group_id)
            if group.group_id == "admin":
                self.is_admin = True
            

    def __str__(self):
        return self.user_id


class MyJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, AttributeDict): # NotSettedParameterは'NotSettedParameter'としてエンコード
            return o.obj
        return super(MyJSONEncoder, self).default(o) # 他の型はdefaultのエンコード方式を使用


class AttributeDict(object):
    def __init__(self, attrs=None):
        if type(attrs) == dict:
            for k, v in attrs.items():
                setattr(self, k, v)
    
    def __repr__(self):
        return str(self.__dict__)

def attribute_dict_validation(att,rules):
    if att == None:
        return {'message': 'Request type must be JSON'}
    
    for rule in rules:
        if rule['type'] == "is_empty":
            if att[rule['key']] == None:
                return {'message': rule['key']+' key is not found'}
        
        elif rule['type'] == "in_value":
            if att[rule['key']] == rule['value']:
                return {'message': rule['key']+' is not allowd value ' + rule['value']}

    return True





def get_virty_user_class(userid):
    user = raw_fetchall("select * from users where id=?",[(userid)])
    if len(user) == 0:
        return None
    elif len(user) >1:
        return None
    else:
        return VirtyUser(user[0].id,user[0].password)


def make_json_response(obj: AttributeDict):
    if type(obj) == None:
        obj = []
    return Response(json.dumps(obj, cls=MyJSONEncoder), mimetype='application/json')


def attribute_args_convertor(args):
    data = {}
    for i in args.keys():
        if args.getlist(i) == [""]:
            data[i] = None
        elif len(args.getlist(i)) == 1:
            data[i] = args.get(i)
        else:
            data[i] = args.getlist(i)
        
    return AttributeDict(data)


def request_json_attribute(request):
    if not request.is_json:
        return None

    request_body = request.get_json()
    if request_body is None:
        return None

    return AttributeDict(request_body)


def create_queue(user_id, resource, _object, method, que_dic):
    queue_id = str(uuid.uuid4())
    sql = "insert into queue (post_time, user_id, id, status, resource, object, method, json, message) values (datetime('now', 'localtime'),?,?,?,?,?,?,?,?)"
    que_json = json.dumps(que_dic, cls=MyJSONEncoder, ensure_ascii=False)
    data = [user_id, queue_id, str("init") ,str(resource) ,str(_object), str(method), str(que_json), str("Not started")]
    raw_commit(sql,data)

    return queue_id


def get_domain():
    domains = raw_fetchall("""
    select name, status, node_name, core, memory, uuid, type, os, group_id, user_id 
    from domain left join domain_owner on uuid=domain_owner.dom_uuid order by domain.name
    """,[])

    return domains


def get_node():
    data = raw_fetchall("select * from node",[])
    return data


def get_user():
    data = raw_fetchall("select * from users",[])
    return data


def get_group():
    data = raw_fetchall("""
    select * from groups 
    """,[])
    return data


def get_groups_users():
    groups = {}

    users = raw_fetchall("""
    select * from groups 
    left join users_groups on groups.id = users_groups.group_id
    """,[])

    for user in users:
        if not user.groupId in groups:
            groups[user.groupId] = []
        groups[user.groupId].append(user.userId)

    data = []
    for k, v in groups.items():
        data.append({"groupId": k, "users": v})

    return data


def get_queue():
    data = raw_fetchall("select * from queue order by post_time desc",[])
    return_data = []
    for que in data:
        que['json'] = json.loads(que['json'])
        return_data.append(que)
    return return_data


def get_queue_uuid(uuid):
    data = raw_fetchall("select * from queue where id=?",[uuid])
    return_data = []
    for que in data:
        que['json'] = json.loads(que['json'])
        return_data.append(que)
    return return_data


def get_queue_incomplete():
    data = raw_fetchall("select * from queue where status='init' or status='running' order by post_time desc",[])
    return_data = []
    for que in data:
        que['json'] = json.loads(que['json'])
        return_data.append(que)
    return return_data


def get_archive():
    archives = raw_fetchall("""select * from archive""",[])
    archive_img = raw_fetchall("select * from archive_img",[])

    data = {}
    for r in archive_img:
        if not r['archiveId'] in data:
            data[r['archiveId']] = []
        data[r['archiveId']].append(r)

    archive_data = []
    for r in archives:
        r['images'] = []
        if r.id in data:
            r['images'] = data[r.id]
        archive_data.append(r)

    return archive_data


def get_storage():
    data = raw_fetchall("select * from storage",[])
    return data


def get_network():
    data = raw_fetchall("select * from network",[])
    return data


def get_image():
    sql = """
        select img.name,img.node,img.pool,img.capa,img.allocation,img.physical,img.path, 
        domain.name as domainName, 
        count(*) as numInUse, 
        archive_img.archive_id 

        from img 
        left join domain_drive on img.path=domain_drive.source 
        left join domain  on domain_drive.dom_uuid=domain.uuid and img.node=domain.node_name 
        left join archive_img on img.name=archive_img.name and img.node=archive_img.node 
        group by img.node,img.path;
    """
    data = raw_fetchall(sql,[])
    return data


def get_domain_by_uuid(uuid):
    db = raw_fetchall("""
    select name, status, node_name, core, memory, uuid, type, os, group_id, user_id 
    from domain left join domain_owner on uuid=domain_owner.dom_uuid where uuid=? order by domain.name
    """,[(uuid)])
    if len(db) == 0:
        return None
    xml = xmllib.get_domain_info(uuid)
    if xml == None:
        return None
    xml.update(db[0].obj)
    return xml


def attribute_dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return AttributeDict(d)


def raw_fetchall(SQL,DATA):
    con = sqlite3.connect(setting.databasePath)
    con.row_factory = attribute_dict_factory
    cur = con.cursor()
    return cur.execute(SQL,DATA).fetchall()


def raw_commit(SQL,DATA):
    con = sqlite3.connect(setting.databasePath)
    cur = con.cursor()
    cur.execute(SQL,DATA)
    result = cur.lastrowid
    con.commit()
    return result