import json
import datetime
import time

from flask import Blueprint
from flask import request
from flask import redirect
from flask import abort
from flask import jsonify
from flask_jwt_extended import jwt_required
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import get_current_user

from module import virty
from module import model


app = Blueprint('api', __name__)


@app.route('/api/auth', methods=['POST'])
def api_auth():
    if not request.is_json:
        body = {'message': 'Request type must be JSON'}
        return jsonify(body), 400

    request_body = request.get_json()
    if request_body is None:
        body = {'message': 'Request body is empty'}
        return jsonify(body), 400

    whitelist = {'userId', 'password'}
    if not request_body.keys() <= whitelist:
        body = {'message': 'Missing userId or password in request field'}
        return jsonify(body), 400

    user = model.get_virty_user_class(request_body['userId'])
    if user == None:
        body = {'message': 'Login failure. Bad userId or password'}
        return jsonify(body), 401
    
    if virty.check_password(user.password, request_body['password']) == False:
        body = {'message': 'Login failure. Bad userId or password'}
        return jsonify(body), 401

    expires = datetime.timedelta(days=7)
    token = create_access_token(identity=user.user_id, expires_delta=expires)
    body = {'message': 'Login succeeded', 'token': token, 'userId': user.user_id, 'isAdmin': user.is_admin}
    return jsonify(body), 200


@app.route('/api/auth/validate', methods=['GET'])
@jwt_required
def api_auth_validate():
    token = request.headers.get("Authorization")
    user = get_current_user()
    return jsonify({'message': 'Validate succeeded', 'token': token, 'userId': user.user_id, 'isAdmin': user.is_admin}), 200


@app.route('/api/vm')
@jwt_required
def api_vm():
    vm = model.get_domain()
    return model.make_json_response(vm)

@app.route('/api/vm/<uuid>')
@jwt_required
def api_vm_uuid(uuid):
    domain = model.get_domain_by_uuid(uuid)
    if domain == None:
        return abort(404)
    return model.make_json_response(domain)


@app.route('/api/node')
@jwt_required
def api_node():
    data = model.get_node()
    return model.make_json_response(data)


@app.route('/api/archive', methods=["GET","POST","DELETE","PUT"])
@jwt_required
def api_archive():
    json = model.request_json_attribute(request)
    if request.method == "POST":
        validation = model.attribute_dict_validation(json,[
            {"type":"is_empty","key":"id"},
            {"type":"is_empty","key":"os"},
            {"type":"is_empty","key":"version"},
            {"type":"is_empty","key":"comment"},
            {"type":"is_empty","key":"url"},
            {"type":"is_empty","key":"icon"},
            {"type":"is_empty","key":"user"},
            {"type":"is_empty","key":"password"},
        ])

        if validation != True:
            return jsonify(validation), 400
        
        data = [json['id'],json['os'],json['version'],json['comment'],json['url'],json['icon'],json['user'],json['password']]
        virty.vsql.RawCommit("insert or ignore into archive (id,os,version,comment,url,icon,user,password) values (?,?,?,?,?,?,?,?)",data)
        return jsonify({'message': "succsess"}), 200

    elif request.method == "PUT":
        validation = model.attribute_dict_validation(json,[
            {"type":"is_empty","key":"archiveId"},
            {"type":"is_empty","key":"imageNode"},
            {"type":"is_empty","key":"imageStorage"},
            {"type":"is_empty","key":"imageName"}
        ])
        if validation != True:
            return jsonify(validation), 400
        
        data = [json['archiveId'],json['imageNode'],json['imageStorage'],json['imageName']]
        virty.vsql.RawCommit("insert or ignore into archive_img (archive_id,node,pool,name) values (?,?,?,?)",data)
        return jsonify({'message': "succsess"}), 200
    
    elif request.method == "DELETE":
        validation = model.attribute_dict_validation(json,[
            {"type":"is_empty","key":"archiveId"},
            {"type":"is_empty","key":"imageNode"},
            {"type":"is_empty","key":"imageStorage"},
            {"type":"is_empty","key":"imageName"}
        ])
        if validation != True:
            return jsonify(validation), 400
        
        data = [json['archiveId'],json['imageNode'],json['imageStorage'],json['imageName']]
        virty.vsql.RawCommit("delete from archive_img where archive_id=? and node=? and pool=? and name=?",data)
        return jsonify({'message': "succsess"}), 200


    else:
        data = model.get_archive()
        return model.make_json_response(data)


@app.route('/api/storage')
@jwt_required
def api_storage():
    data = model.get_storage()
    return model.make_json_response(data)


@app.route('/api/image')
@jwt_required
def api_image():
    data = model.get_image()
    return model.make_json_response(data)


@app.route('/api/network')
@jwt_required
def api_network():
    data = model.get_network()
    return model.make_json_response(data)


@app.route('/api/queue')
@jwt_required
def api_queue():
    if request.args.get('status') == None:
        data = model.get_queue()
        return model.make_json_response(data)
    elif request.args.get('status') == "incomplete":
        json_attribute = model.request_json_attribute(request)
        json = []
        validation = model.attribute_dict_validation(json,[])
        if validation != True:
            return jsonify(validation), 400

        for att in json_attribute.obj:
            json.append(model.AttributeDict(att))
        
        data = []
        for i in range(50):
            data = model.get_queue_incomplete()

            if data != json:
                return model.make_json_response({'message': 'not match','post':json, 'db': data})
            time.sleep(0.1)
        return model.make_json_response({'message': 'match','post':json, 'db': data})
    else:
        return abort(400)


@app.route('/api/user',methods=["GET","POST","DELETE","PUT"])
@jwt_required
def api_user():
    if request.method == "GET":
        users = model.get_user()
        return model.make_json_response(users)

    elif request.method == "POST":
        # バリデーション
        json = model.request_json_attribute(request)
        validation = model.attribute_dict_validation(json,[{"type":"is_empty","key":"password"}, {"type":"is_empty","key":"userId"}])

        if validation != True:
            return jsonify(validation), 400

        # ユーザ情報DB照会
        if virty.userIsExist(json['userId']):
            return abort(400)

        # ユーザ作成
        virty.UserAdd(json['userId'],virty.hash_password(json['password']))
        body = {'message': "succsess"}
        return jsonify(body), 200

    elif request.method == "DELETE":
        # バリデーション
        json = model.request_json_attribute(request)
        validation = model.attribute_dict_validation(json,[{"type":"in_value", "key":"userId", "value":"admin"}, {"type":"is_empty","key":"userId"}])

        if validation != True:
            return jsonify(validation), 400

        # ユーザー削除
        model.raw_commit("update domain_owner set user_id=? where user_id=?",[None,json['userId']])
        model.raw_commit("delete from users_groups where user_id=?",[json['userId']])
        model.raw_commit("delete from users where id=?",[json['userId']])
        body = {'message': "succsess"}
        return jsonify(body), 200
    
    elif request.method == "PUT":
        # バリデーション
        json = model.request_json_attribute(request)
        validation = model.attribute_dict_validation(json,[{"type":"is_empty","key":"password"}, {"type":"is_empty","key":"userId"}])

        if validation != True:
            return jsonify(validation), 400
        
        # パスワード更新
        virty.UserReset(json['userId'],virty.hash_password(json['password']))
        return jsonify({'message': "succsess"}), 200


@app.route('/api/group',methods=["GET","POST","DELETE","PUT"])
@jwt_required
def api_group():
    if request.method == "GET":
        return model.make_json_response(model.get_groups_users())

    elif request.method == "POST":
        # バリデーション
        json = model.request_json_attribute(request)
        validation = model.attribute_dict_validation(json,[{"type":"is_empty","key":"groupId"}])

        if validation != True:
            return jsonify(validation), 400

        # グループ情報DB照会
        if virty.groupIsExist(json['groupId']):
            return abort(400)

        # グループ作成
        model.raw_commit("insert into groups ('id') values (?)",[json['groupId']])
        return jsonify({'message': "succsess"}), 200

    elif request.method == "DELETE":
        # バリデーション
        json = model.request_json_attribute(request)
        validation = model.attribute_dict_validation(json,[{"type":"in_value", "key":"groupId", "value":"admin"}, {"type":"is_empty","key":"groupId"}])

        if validation != True:
            return jsonify(validation), 400

        # グループ削除
        model.raw_commit("update domain_owner set group_id=? where group_id=?",[None,json['groupId']])
        model.raw_commit("delete from users_groups where group_id=?",[json['groupId']])
        model.raw_commit("delete from groups where id=?",[json['groupId']])
        return jsonify({'message': "succsess"}), 200

    
    elif request.method == "PUT":
        # バリデーション
        json = model.request_json_attribute(request)
        validation = model.attribute_dict_validation(json,[{"type":"is_empty","key":"password"}, {"type":"is_empty","key":"userId"}])

        if validation != True:
            return jsonify(validation), 400
        
        # パスワード更新
        virty.UserReset(json['userId'],virty.hash_password(json['password']))
        return jsonify({'message': "succsess"}), 200



@app.route('/api/echo',methods=["POST"])
@jwt_required
def api_echo():
    if not request.is_json:
        body = {'message': 'Request type must be JSON'}
        return jsonify(body), 400

    request_body = request.get_json()
    if request_body is None:
        body = {'message': 'Request body is empty'}
        return jsonify(body), 400

    json = model.AttributeDict(request_body)
    return model.make_json_response(json)


@app.route("/api/queue/<resource>/<_object>",methods=["POST", "DELETE", "PUT"])
@jwt_required
def api_queue_object_method(resource,_object):
    user = get_current_user()

    if not request.is_json:
        body = {'message': 'Request type must be JSON'}
        return jsonify(body), 400

    request_body = request.get_json()
    if request_body is None:
        body = {'message': 'Request body is empty'}
        return jsonify(body), 400
    
    method = str(request.method).lower()

    json = model.AttributeDict(request_body)
    queue_id = model.create_queue(user.user_id, resource, _object, method, json)

    return model.make_json_response({'id': queue_id ,'resource':resource ,'object': _object, 'method': method ,'queue':json})
    