import subprocess
import logging
import bcrypt
from flask import Flask, render_template, jsonify, request,redirect, Response, abort, send_from_directory, Blueprint
from flask_jwt import JWT, jwt_required, current_identity
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import safe_str_cmp
from functools import wraps
from time import sleep
from module import virty
from views import domain, api

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

############################
# flask                    #
############################
app = Flask(__name__, static_folder='node_modules', static_url_path='/module')
app.config['SECRET_KEY'] = 'super-secret-key'
app.config['JWT_AUTH_URL_RULE'] = '/auth'
app.config['JWT_AUTH_USERNAME_KEY'] = 'userid'
app.config['JWT_AUTH_PASSWORD_KEY'] = 'passwd'
app.config['JWT_LEEWAY'] = 100000000

app.register_blueprint(domain.app)
app.register_blueprint(api.app)

login_manager = LoginManager()
login_manager.init_app(app)

def UserRoll(func):
    @wraps(func)
    @login_required
    def wrapper(*args, **kwargs):
        if not current_user.get_id() == "admin":
            return "<h1>Insufficient permissions</h1>"
        return func(*args, **kwargs)
    return wrapper

############################
# SETUP                    #
############################
if virty.vsql.RawFetchall("select name from sqlite_master where type='table';",[]) == []:
    print("database init")
    virty.vsql.SqlInit()


############################
# JWT                      #
############################
def authenticate(userid,passwd):
    user = virty.vsql.UserGet(userid)
    if user != None and check_password(user.passwd, passwd):
        print(user)
        return user
    else:
        print("password miss match.")
        

def identity(payload):
    userid = payload['identity']
    return virty.vsql.UserGet(userid)

jwt = JWT(app, authenticate, identity)




############################
# WEB                      #
############################
@app.route('/')
@login_required
def route():
    return redirect("/domain", code=302)




############################
# STATIC                   #
############################
@app.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('static', path)




############################
# LOGIN                    #
############################
def hash_password(password, rounds=12):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds)).decode()

def check_password(hashed_password, user_password):
    return bcrypt.checkpw(user_password.encode(), hashed_password.encode())

@login_manager.unauthorized_handler
def unauthorized():
    print("unauthorized")
    return redirect("/login", code=301)

@login_manager.user_loader
def load_user(user_id):
    return virty.vsql.UserGet(user_id)

@app.route('/login', methods=["GET", "POST"])
def login():
    if(request.method == "POST"):
        user = virty.vsql.UserGet(request.form["username"])
        if user and check_password(user.passwd,request.form["password"]):
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




############################
# SETTING                  #
############################
@app.route('/setting',methods=["POST","GET"])
@login_required
def setting():
    if request.method == 'POST':
        if request.form["status"] == "dbinit":
            virty.vsql.SqlInit()
            return "database init"
    elif request.method == 'GET':
        html = render_template('setting.html')
        return html



############################
# ARCHIVE                  #
############################
@app.route('/archive',methods=["GET"])
@login_required
def archive():
    if request.args.get("json") == None:
        img = {}
        for i in virty.vsql.SqlGetAll("archive_img"):
            if img.get(i[0],False):
                img[i[0]].append(i[1])
            else:
                img[i[0]] = [i[2]]
        html = render_template('ArchiveList.html',domain=virty.vsql.SqlGetAll('archive'),img=img)
        return html
    else:
        return abort(400)
    


@app.route('/archive',methods=["POST"])
@login_required
def archive_post():
    d = request.form
    if d.get('method') == "add":
        DATA = [d.get('id'),d.get('os'),d.get('version'),d.get('comment'),d.get('url'),d.get('icon'),d.get('user'),d.get('password')]
        virty.vsql.RawCommit("insert or ignore into archive (id,os,version,comment,url,icon,user,password) values (?,?,?,?,?,?,?,?)",DATA)
        return redirect("/archive",code=303)
    elif d.get('method') == "assign":
        DATA = [d.get('archive-id'),d.get('node'),d.get('pool'),d.get('name')]
        virty.vsql.RawCommit("insert or ignore into archive_img (archive_id,node,pool,name) values (?,?,?,?)",DATA)
        return redirect("/archive",code=303)
    else:
        return abort(400)

@app.route('/network/add')
@login_required
def network_add():
    virty.WorkerUp()
    html = render_template('NetworkAdd.html')
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






############################
# USER                     #
############################
@app.route('/user',methods=["GET","POST"])
@login_required
def user():
    if request.method == "GET":
        groups = {}
        for i in virty.vsql.SqlGetAll("users_groups"):
            if groups.get(i[0],False):
                groups[i[0]].append(i[1])
            else:
                groups[i[0]] = [i[1]]
        html = render_template('UserList.html',users=virty.vsql.SqlGetAll("users"),groups=groups)
        return html
    elif request.method == "POST":
        if request.form.get('method') == "delete":
            if request.form.get('user-id') == "admin":
                return abort(400)
            elif request.form.get('user-id') == None:
                return abort(400)
            else:
                virty.vsql.RawCommit("update domain_owner set user_id=? where user_id=?",[None,request.form['user-id']])
                virty.vsql.RawCommit("delete from users_groups where user_id=?",[request.form['user-id']])
                virty.vsql.RawCommit("delete from users where id=?",[request.form['user-id']])
                return redirect("/user", code=303)
        elif request.form.get('method') == "reset":
            if request.form.get('user-id') == None or request.form.get('password') == None:
                return abort(400)
            else:
                virty.UserReset(request.form['user-id'],hash_password(request.form['password']))
                return redirect("/user", code=303)
        elif request.form.get('method') == "add":
            if request.form.get('user-id') == None or request.form.get('password') == None:
                return abort(400)
            else:
                if virty.userIsExist(request.form['user-id']):
                    return abort(400)
                else:
                    virty.UserAdd(request.form['user-id'],hash_password(request.form['password']))
                    return redirect("/user", code=303)
        else:
            return abort(400)




############################
# GROUP                    #
############################
@app.route('/group',methods=["GET","POST"])
@login_required
def group():
    if request.method == "GET":
        tag = {}
        for i in virty.vsql.SqlGetAll("users_groups"):
            if tag.get(i[1],False):
                tag[i[1]].append(i[0])
            else:
                tag[i[1]] = [i[0]]
        html = render_template('GroupList.html',groups=virty.vsql.SqlGetAll("groups"),tag=tag,users=virty.vsql.SqlGetAll("users"))
        return html
    elif request.method == "POST":
        if request.form.get('method') == "delete":
            if request.form.get('group-id') == "admin":
                return abort(400)
            elif request.form.get('group-id') == None:
                return abort(400)
            else:
                virty.vsql.RawCommit("update domain_owner set group_id=? where group_id=?",[None,request.form['group-id']])
                virty.vsql.RawCommit("delete from users_groups where group_id=?",[request.form['group-id']])
                virty.vsql.RawCommit("delete from groups where id=?",[request.form['group-id']])
                return redirect("/group", code=303)
        elif request.form.get('method') == "add":
            if request.form.get('group-id') == None:
                return abort(400)
            else:
                if virty.groupIsExist(request.form['group-id']):
                    return abort(400)
                else:
                    virty.vsql.RawCommit("insert into groups ('id') values (?)",[request.form['group-id']])
                    return redirect("/group", code=303)
        elif request.form.get('method') == "assgin":
            virty.vsql.RawCommit("insert into users_groups ('user_id','group_id') values (?,?)",[request.form['user-id'],request.form['group-id']])
            return redirect("/group", code=303)
        elif request.form.get('method') == "leave":
            virty.vsql.RawCommit("delete from users_groups where user_id=? and group_id=?",[request.form['user-id'],request.form['group-id']])
            return redirect("/group", code=303)
        else:
            return abort(400)




############################
# ACTION                   #
############################
@app.route('/action/image/delete',methods=["POST"])
@login_required
def action_image_delete():
    task = {}
    for key, value in request.form.items():
        task[key]=value
    print(task)
    virty.ImageDelete(task['node'],task['pool'],task['name'])
    virty.DomainListInit()
    return redirect("/ui/image", code=302)


@app.route("/action/cdrom/change",methods=["POST"])
@login_required
def action_cdrom_change():
    task = {}
    for key, value in request.form.items():
        task[key]=value
    if task['status'] == "edit":
        virty.DomCdromEdit(task['uuid'],task['target'],task['path'])
    elif task['status'] == "unmount":
        virty.DomCdromExit(task['uuid'],task['target'])
    virty.DomainListInit()
    print(task)
    return redirect("/domain?uuid=" + task['uuid'])


@app.route("/action/selinux",methods=["POST"])
@login_required
def action_selinux():
    task = {}
    for key, value in request.form.items():
        task[key]=value
    virty.DomSelinuxDisable(task['uuid'])
    return redirect("/domain?uuid=" + task['uuid'])







if __name__ == "__main__":
    if virty.vsql.RawFetchall("select name from sqlite_master where type='table';",[]) == []:
        print("database init")
        virty.vsql.SqlInit()
    virty.WorkerUp()
    app.run(debug=True, host='0.0.0.0', port=80)