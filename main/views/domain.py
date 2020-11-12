from flask import Flask, render_template, jsonify, request,redirect, Response, abort, send_from_directory, Blueprint
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import safe_str_cmp
from functools import wraps
from time import sleep
import subprocess, logging, bcrypt
from module import virty

app = Blueprint('domain', __name__)

@app.route('/domain',methods=["GET"])
@login_required
def domain_get():
    if not request.args.get('uuid') == None and request.args.get('ui') == None:
        owner = virty.vsql.RawFetchall("select * from domain_owner where dom_uuid=?",[request.args.get('uuid')])
        if not current_user.isadmin:
            if owner == []:
                return "<h1>Insufficient permissions</h1>"
            if not current_user.id == owner[0][2] and not (owner[0][1],) in current_user.groups:
                return "<h1>Insufficient permissions</h1>"
        xml = virty.DomainData(request.args.get('uuid'))
        db = virty.vsql.RawFetchall("select * from domain where uuid=?",[(request.args.get('uuid'))])
        net = virty.NodeNetworkList(virty.vsql.Convert("DOM_UUID","NODE_NAME",request.args.get('uuid')))
        html = render_template('DomainInfo.html',xml=xml,db=db,net=net)
    
    elif request.args.get('ui') == "cdrom":
        NODE_NAME = virty.vsql.Convert("DOM_UUID","NODE_NAME",request.args.get('uuid'))
        IMAGE_DATAS = virty.ImageIsoList(NODE_NAME)
        html = render_template('DomainCdromEdit.html',IMG=IMAGE_DATAS,DOM=[request.args.get('uuid'),request.args.get('target')])

    else:
        if current_user.isadmin:
            domain = virty.vsql.RawFetchall("select * from domain left join domain_owner on uuid=domain_owner.dom_uuid order by domain.name",[])
            users = virty.vsql.SqlGetAll("users")
            groups = virty.vsql.SqlGetAll("groups")
            html = render_template('DomainList.html',domain=domain,users=users,groups=groups,node=virty.vsql.SqlGetAll("node"))
        else:
            SQL = "select * from domain left join domain_owner on uuid=domain_owner.dom_uuid where domain_owner.user_id=? or domain_owner.group_id in (select group_id from users_groups where user_id =?)"
            domain = virty.vsql.RawFetchall(SQL,[current_user.id,current_user.id])
            users = virty.vsql.SqlGetAll("users")
            groups = virty.vsql.SqlGetAll("groups")
            html = render_template('DomainList.html',domain=domain,users=users,groups=groups,node=virty.vsql.SqlGetAll("node"))
    return html

@app.route('/domain',methods=["POST"])
@login_required
def domain_post():
    virty.vsql.RawCommit("insert or ignore into domain_owner (dom_uuid,user_id,group_id) values (?,?,?)",[request.form['uuid'],None,None])
    if request.form['target'] == "domain_user":
        if request.form['status'] == "delete":
            virty.vsql.RawCommit("update domain_owner set user_id=? where dom_uuid=?",[None,request.form['uuid']])
        elif request.form['status'] == "change":
            virty.vsql.RawCommit("update domain_owner set user_id=? where dom_uuid=?",[request.form['user-id'],request.form['uuid']])
        else:
            return abort(400)
    elif request.form['target'] == "domain_group":
        if request.form['status'] == "delete":
            virty.vsql.RawCommit("update domain_owner set group_id=? where dom_uuid=?",[None,request.form['uuid']])
        elif request.form['status'] == "change":
            virty.vsql.RawCommit("update domain_owner set group_id=? where dom_uuid=?",[request.form['group-id'],request.form['uuid']])
        else:
            return abort(400)
    else:
        return abort(400)
    return redirect("/", code=302)

@app.route('/domain/define')
@login_required
def domain_define():
    if request.args.get('json') == "define":
        network = virty.NodeNetworkList(request.args.get('node'))
        storage = virty.StorageList(request.args.get('node'))
        archive = virty.vsql.SqlGetAll('archive')
        return jsonify(network=network,storage=storage,archive=archive)
    else:
        virty.WorkerUp()
        html = render_template('domainDefineSteps.html',node=virty.vsql.SqlGetAll("node"))
        return html


