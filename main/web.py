import subprocess
import logging
from time import sleep

from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request
from flask import redirect
from flask import Response
from flask import abort
from flask import send_from_directory
from flask import Blueprint

from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_cors import CORS
from flask_jwt_extended import jwt_required
from flask_jwt_extended import create_access_token
from flask_jwt_extended import JWTManager
from flask_jwt_extended import get_jwt_identity

from module import virty
from views import action
from views import api
from views import archive
from views import domain
from views import group
from views import queue
from views import settings
from views import user


############################
# flask                    #
############################
app = Flask(__name__, static_folder='node_modules', static_url_path='/module')

CORS(app)

app.register_blueprint(action.app)
app.register_blueprint(api.app)
app.register_blueprint(archive.app)
app.register_blueprint(domain.app)
app.register_blueprint(group.app)
app.register_blueprint(queue.app)
app.register_blueprint(settings.app)
app.register_blueprint(user.app)

#### Login config ####
app.config['SECRET_KEY'] = virty.setting.webSecret
login_manager = LoginManager()
login_manager.init_app(app)

#### JWT config ####
app.url_map.strict_slashes = False
app.config['JWT_SECRET_KEY'] = virty.setting.webSecret




############################
# JWT                      #
############################
def jwt_unauthorized_loader_handler(reason):
    return jsonify({'message': 'Unauthorized'}), 401

jwt = JWTManager(app)
jwt.unauthorized_loader(jwt_unauthorized_loader_handler)

@jwt.user_loader_callback_loader
def user_loader_callback(identity):
    user = virty.vsql.UserGet(identity)
    return user

@app.route('/api/auth', methods=['POST'])
def api_auth():
    if not request.is_json:
        body = {'message': 'Request type must be JSON'}
        return jsonify(body), 400

    request_body = request.get_json()
    if request_body is None:
        body = {'message': 'Request body is empty'}
        return jsonify(body), 400

    whitelist = {'userid', 'password'}
    if not request_body.keys() <= whitelist:
        body = {'message': 'Missing userid or password in request field'}
        return jsonify(body), 400

    user = virty.vsql.UserGet(request_body['userid'])
    if user == None:
        body = {'message': 'Login failure. Bad userid or password'}
        return jsonify(body), 401
    
    if virty.check_password(user.passwd, request_body['password']) == False:
        body = {'message': 'Login failure. Bad userid or password'}
        return jsonify(body), 401

    token = create_access_token(identity=user.id)
    body = {'message': 'Login succeeded', 'token': token, 'userid': user.id, 'isAdmin': True}
    return jsonify(body), 200

@app.route('/api/auth/validate', methods=['GET'])
@jwt_required
def api_auth_validate():
    token = request.headers.get("Authorization")
    userid = get_jwt_identity()
    return jsonify({'message': 'Validate succeeded', 'token': token, 'userid': userid}), 200




############################
# STARTUP                  #
############################
if virty.vsql.RawFetchall("select name from sqlite_master where type='table';",[]) == []:
    print("database init")
    virty.vsql.SqlInit()
    virty.WorkerUp()
else:
    virty.WorkerUp()




############################
# STATIC                   #
############################
@app.route('/')
@login_required
def route():
    return redirect("/domain", code=302)


@app.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('static', path)




############################
# LOGIN                    #
############################
@login_manager.unauthorized_handler
def unauthorized():
    return redirect("/login", code=301)


@login_manager.user_loader
def load_user(user_id):
    return virty.vsql.UserGet(user_id)


@app.route('/login', methods=["GET", "POST"])
def login():
    if(request.method == "POST"):
        user = virty.vsql.UserGet(request.form["username"])
        if user and virty.check_password(user.passwd,request.form["password"]):
            login_user(user)
            return redirect("/", code=301)
        else:
            return redirect("/login", code=302)
    elif(request.method == "GET"):
        if current_user.is_authenticated:
            return redirect("/", code=301)
        else:
            return render_template('Login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect("/login", code=301)


@app.route('/network/add')
@login_required
def network_add():
    virty.WorkerUp()
    html = render_template('NetworkAdd.html',node=virty.vsql.SqlGetAll("node"))
    return html




############################
# NETWORK                  #
############################
@app.route('/network',methods=["GET"])
@login_required
def network():
    html = render_template('NetworkList.html',networks=virty.vsql.SqlGetAll("network"),node=virty.vsql.SqlGetAll("node"))
    return html




############################
# IMAGE                    #
############################
@app.route('/image',methods=["GET"])
@login_required
def image():
    if request.args.get('tree') == "true":
        if not request.args.get('node') == None:
            if not request.args.get('pool') == None:
                archive = virty.vsql.SqlGetAll('archive')
                data = virty.vsql.imgListSelectAdmin(request.args.get('node'),request.args.get('pool'))
                html = render_template('ImageList.html',images=data,archive=archive)
            else:
                data = virty.vsql.PoolListGet(request.args.get('node'))
                html = render_template('ImageListPool.html',data=data)
        else:
            data = virty.vsql.SqlGetAll('storage')
            html = render_template('ImageListNode.html',domain=virty.vsql.SqlGetAll("node"))
    elif request.args.get('ui') == "edit":
        data = [request.args.get('node'),request.args.get('pool'),request.args.get('target')]
        html = render_template('ImageEdit.html',data=data)
    else:
        archive = virty.vsql.SqlGetAll('archive')
        images = virty.vsql.imgListAdmin()
        html = render_template('ImageList.html',images=images,archive=archive)
    return html




############################
# STORAGE                  #
############################
@app.route('/storage',methods=["GET"])
@login_required
def storage():
    if request.args.get('ui') == "undefine":
        html = render_template('StorageUndefine.html',domain=[request.args.get('node'),request.args.get('pool')])
    else:
        data = virty.vsql.SqlGetAll('storage')
        html = render_template('StorageList.html',data=data)
    return html

@app.route('/storage/add')
@login_required
def storage_add():
    virty.WorkerUp()
    node = virty.vsql.SqlGetAll('node')
    html = render_template('StorageAdd.html',node=node)
    return html




############################
# NODE                     #
############################
@app.route('/node',methods=["GET"])
@login_required
def node():
    html = render_template('NodeList.html',domain=virty.vsql.SqlGetAll("node"),sumdata=virty.vsql.SqlSumNode())
    return html

@app.route('/node/add')
@login_required
def node_add():
    virty.WorkerUp()
    html = render_template('NodeAdd.html')
    return html




if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=80)
    