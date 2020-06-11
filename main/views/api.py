import json
from flask import Flask
from flask import Response
from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import abort
from flask import jsonify
from flask import send_from_directory
from flask_login import login_required
from flask_jwt import jwt_required
from module import virty

app = Blueprint('api', __name__)



@app.route('/api/json/<OBJECT>')
@login_required
def api_json_object(OBJECT):
    NODE_NAME = request.args.get('node')
    if OBJECT == "network":
        if NODE_NAME == None:result = virty.NodeNetworkAllList()
        else:result=virty.NodeNetworkList(NODE_NAME)
    elif OBJECT == "interface":
        if NODE_NAME == None:result=virty.AllInterfaceList()
        else:result=virty.InterfaceList(NODE_NAME)
    elif OBJECT == "storage":
        if NODE_NAME == None:result = []
        else:result=virty.StorageList(NODE_NAME)
    elif OBJECT == "archive":
        if NODE_NAME == None:result = []
        else:result=virty.ImageArchiveList(NODE_NAME)   
    elif OBJECT == "stack-que":
        result=virty.vsql.SqlQueuget("running")
    else:
        return abort(404)
    return jsonify(ResultSet=result)


@app.route("/api/que/<OBJECT>/<METHOD>",methods=["POST"])
@login_required
def api_que(OBJECT,METHOD):
    form = virty.attribute_args_convertor(request.form)
    queueid = virty.Queuing(OBJECT,METHOD,form)
    
    if form.get('return') == "json":
        return jsonify(queueid)
    else:
        return redirect(request.referrer, code=302)

@app.route('/api/read/<OBJECT>')
@jwt_required()
def api_read_object(OBJECT):
    NODE_NAME = request.args.get('node')
    if OBJECT == "network":
        if NODE_NAME == None:result = virty.NodeNetworkAllList()
        else:result=virty.NodeNetworkList(NODE_NAME)
    elif OBJECT == "interface":
        if NODE_NAME == None:result=virty.AllInterfaceList()
        else:result=virty.InterfaceList(NODE_NAME)
    elif OBJECT == "storage":
        if NODE_NAME == None:result = []
        else:result=virty.StorageList(NODE_NAME)
    elif OBJECT == "archive":
        if NODE_NAME == None:result = []
        else:result=virty.ImageArchiveList(NODE_NAME)   
    elif OBJECT == "stack-que":
        result=virty.vsql.SqlQueuget("running")
    elif OBJECT == "domain":
        result = virty.vsql.SqlGetAll("domain")
    else:
        return abort(404)
    return jsonify(result)

@app.route("/api/create/<OBJECT>/<METHOD>",methods=["POST"])
@jwt_required()
def api_create_object_method(OBJECT,METHOD):
    # POSTデータを型クラスに
    form = virty.attribute_args_convertor(request.form)
    # そのままDICをJSONで返す
    return_dic = virty.Queuing(OBJECT,METHOD,form)
    return virty.attribute_args_dump(return_dic)