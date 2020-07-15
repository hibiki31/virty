import subprocess
import logging
from time import sleep

from flask import Flask, render_template, jsonify, request,redirect, Response, abort, send_from_directory, Blueprint
from flask_jwt import JWT, jwt_required, current_identity
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from module import virty
from views import action, api, archive, domain, group, queue, settings, user



############################
# flask                    #
############################
app = Flask(__name__, static_folder='node_modules', static_url_path='/module')
app.config['SECRET_KEY'] = 'secret-key'
app.config['JWT_AUTH_URL_RULE'] = '/auth'
app.config['JWT_AUTH_USERNAME_KEY'] = 'userid'
app.config['JWT_AUTH_PASSWORD_KEY'] = 'passwd'
app.config['JWT_LEEWAY'] = 100000000

app.register_blueprint(action.app)
app.register_blueprint(api.app)
app.register_blueprint(archive.app)
app.register_blueprint(domain.app)
app.register_blueprint(group.app)
app.register_blueprint(queue.app)
app.register_blueprint(settings.app)
app.register_blueprint(user.app)

login_manager = LoginManager()
login_manager.init_app(app)



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
# JWT                      #
############################
def authenticate(userid,passwd):
    user = virty.vsql.UserGet(userid)
    if user != None and virty.check_password(user.passwd, passwd):
        return user
        

def identity(payload):
    userid = payload['identity']
    return virty.vsql.UserGet(userid)

jwt = JWT(app, authenticate, identity)



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