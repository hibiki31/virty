import os
import sqlite3
import json

from flask import Response

from module import setting
from module import xml_editor



class VirtyUser():
    def __init__(self, userid, password):
        self.userid = str(userid)
        self.password = password
        self.groups = []
        self.is_admin = False

        for group in raw_fetchall("select group_id from users_groups where user_id=?",[userid]):
            self.groups.append(group.group_id)
            if group.group_id == "admin":
                self.is_admin = True
            

    def __str__(self):
        return self.userid


class MyJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, AttributeDict): # NotSettedParameterは'NotSettedParameter'としてエンコード
            return o.obj
        return super(MyJSONEncoder, self).default(o) # 他の型はdefaultのエンコード方式を使用


class AttributeDict(object):
    def __init__(self, obj):
        if type(obj) != dict:
            raise 
        self.obj = obj

    ### Pickle
    def __getstate__(self):
        return self.obj.items()

    ### Pickle
    def __setstate__(self, items):
        if not hasattr(self, 'obj'):
            self.obj = {}
        for key, val in items:
            self.obj[key] = val

    ### Class["key"] = "val"
    def __setitem__(self, key, val):
        self.obj[key] = val

    ### Class["key"]
    def __getitem__(self, name):
        if name in self.obj:
            return self.obj.get(name)
        else:
            return None

    ### Class.name
    def __getattr__(self, name):
        if name in self.obj:
            return self.obj.get(name)
        else:
            return None

    ### dict互換
    def keys(self):
        return self.obj.keys()

    ### dict互換
    def values(self):
        return self.obj.values()



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


def get_domain():
    domains = raw_fetchall("select * from domain left join domain_owner on uuid=domain_owner.dom_uuid order by domain.name",[])
    return domains


def get_domain_by_uuid(uuid):
    xml = xml_editor.get_domain_info(uuid)
    db = raw_fetchall("select * from domain left join domain_owner on uuid=domain_owner.dom_uuid where uuid=? order by domain.name",[(uuid)])
    if len(db) == 1:
        xml.update(db[0].obj)
    else:
        db = None
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