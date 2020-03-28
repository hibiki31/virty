from flask import Flask, render_template, jsonify, request,redirect, Response, abort,send_from_directory
from flask_jwt import JWT, jwt_required, current_identity
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import safe_str_cmp
from functools import wraps
from time import  sleep
import subprocess, logging, bcrypt
import virty

############################
# flask                    #
############################
l = logging.getLogger()
l.addHandler(logging.FileHandler("/dev/null"))

app = Flask(__name__, static_folder='node_modules', static_url_path='/npm')
app.config['SECRET_KEY'] = 'super-secret'
app.config['JWT_AUTH_URL_RULE'] = '/auth'
app.config['JWT_LEEWAY'] = 100000000

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
def authenticate(user_id, password):
    user = virty.vsql.UserGet(user_id)
    if user and safe_str_cmp(user.password.encode('utf-8'), password.encode('utf-8')):
        return user

def identity(payload):
    user_id = payload['identity']
    return virty.vsql.UserGet(user_id)

jwt = JWT(app, authenticate, identity)

############################
# LOGIN                    #
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
        if user and check_password(user.password,request.form["password"]):
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
# SETUP                    #
############################
@app.route('/ui/setup',methods=["POST","GET"])
def setup():
    if request.method == 'POST':
        if request.form["status"] == "dbinit":
            virty.vsql.SqlInit()
            return "database init"
    elif request.method == 'GET':
        html = render_template('Setup.html')
        return html

############################
# WEB                      #
############################
@app.route('/')
@login_required
def route():
    return redirect("/ui/domain", code=302)

@app.route('/storage/<NODE>/<NAME>')
@login_required
def info_storage(NODE,NAME):
    html = render_template('StorageUndefine.html',domain=[NODE,NAME])
    return html

@app.route('/archive/list')
@login_required
def storage_listall():
    html = render_template('ArchiveImageList.html',datas=virty.ImageArchiveListAll())
    return html

@app.route('/network/delete/<NODE>/<SOURCE>')
@login_required
def network_delete(NODE,SOURCE):
    virty.vsql.NetworkDelete(NODE,SOURCE)
    return redirect("/list/network", code=302)

@app.route('/ui/<GET_DATA>')
@login_required
def node_list(GET_DATA):
    if GET_DATA == "node":
        html = render_template('NodeList.html',domain=virty.vsql.SqlGetAll("node"),sumdata=virty.vsql.SqlSumNode())
    elif GET_DATA == "archive":
        html = render_template('ArchiveList.html',domain=virty.ImageArchiveListAll())
    elif GET_DATA == "storage":
        data = virty.vsql.SqlGetAll('storage')
        html = render_template('StorageList.html',data=data)
    elif GET_DATA == "network":
        html = render_template('NetworkList.html',networks=virty.vsql.SqlGetAll("network"))
    elif GET_DATA == "que":
        domain = virty.vsql.RawFetchall("select * from que order by que_id desc",[])
        html = render_template('QueList.html',domain=domain,status=virty.WorkerStatus())
    elif GET_DATA == "users":
        groups = {}
        for i in virty.vsql.SqlGetAll("users_groups"):
            if groups.get(i[0],False):
                groups[i[0]].append(i[1])
            else:
                groups[i[0]] = [i[1]]
        html = render_template('UserList.html',users=virty.vsql.SqlGetAll("users"),groups=groups)
    
    elif GET_DATA == "groups":
        groups = {}
        for i in virty.vsql.SqlGetAll("users_groups"):
            if groups.get(i[1],False):
                groups[i[1]].append(i[0])
            else:
                groups[i[1]] = [i[0]]
        html = render_template('GroupList.html',users=virty.vsql.SqlGetAll("groups"),groups=groups)


    elif GET_DATA == "image":
        if request.args.get('tree') == "true":
            if not request.args.get('node') == None:
                if not request.args.get('pool') == None:
                    data = virty.vsql.RawFetchall("select img.name,img.node,img.pool,img.capa,img.allocation,img.physical,img.path,domain.name,count(*) from img left join domain_drive on img.path=domain_drive.source left join domain on domain_drive.dom_uuid=domain.uuid and img.node=domain.node_name where node=? and pool=? group by img.node,img.path;",[(request.args.get('node')),(request.args.get('pool'))])
                    html = render_template('ImageList.html',images=data)
                else:
                    data = virty.vsql.PoolListGet(request.args.get('node'))
                    html = render_template('ImageListPool.html',data=data)
            else:
                data = virty.vsql.SqlGetAll('storage')
                html = render_template('ImageListNode.html',domain=virty.vsql.SqlGetAll("node"))
        else:
            images = virty.vsql.RawFetchall("select img.name,img.node,img.pool,img.capa,img.allocation,img.physical,img.path,domain.name,count(*) from img left join domain_drive on img.path=domain_drive.source left join domain on domain_drive.dom_uuid=domain.uuid and img.node=domain.node_name group by img.node,img.path;",[])
            html = render_template('ImageList.html',images=images)
    elif GET_DATA == "domain":
        if not request.args.get('uuid') == None:
            xml = virty.DomainData(request.args.get('uuid'))
            db = virty.vsql.RawFetchall("select * from domain where uuid=?",[(request.args.get('uuid'))])
            net = virty.NodeNetworkList(virty.vsql.Convert("DOM_UUID","NODE_NAME",request.args.get('uuid')))
            html = render_template('DomainInfo.html',xml=xml,db=db,net=net)
        else:
            if current_user.isadmin:
                domain = virty.vsql.RawFetchall("select * from domain left join domain_owner on uuid=domain_owner.dom_uuid",[])
                users = virty.vsql.SqlGetAll("users")
                groups = virty.vsql.SqlGetAll("groups")
                html = render_template('DomainList.html',domain=domain,users=users,groups=groups)
            else:
                domain = []
                html = render_template('DomainList.html',domain=domain)

    else:
        return abort(404)
    return html

#GETでやろう
@app.route('/ui/edit/image/<NODE>/<POOL>/<FILE>')
@login_required
def ui_edit(NODE,POOL,FILE):
    data = [NODE,POOL,FILE]
    html = render_template('ImageEdit.html',data=data)
    return html

############################
# UI MAKE                  #
############################
@app.route('/ui/make/domain')
@login_required
def domain_add():
    virty.WorkerUp()
    html = render_template('DomainDefine.html',node=virty.vsql.SqlGetAll("node"))
    return html

@app.route('/ui/make/node')
@login_required
def node_add():
    virty.WorkerUp()
    html = render_template('NodeAdd.html')
    return html

@app.route('/ui/make/storage')
@login_required
def storage_add():
    virty.WorkerUp()
    html = render_template('StorageAdd.html')
    return html

@app.route('/ui/make/network')
@login_required
def network_add():
    virty.WorkerUp()
    html = render_template('NetworkAdd.html')
    return html

@app.route('/ui/make/user')
@login_required
def user_add():
    users = virty.vsql.SqlGetAll("users")
    groups = virty.vsql.SqlGetAll("groups")
    virty.WorkerUp()
    html = render_template('UserAdd.html',users=users,groups=groups)
    return html

############################
# DOMAIN                   #
############################
@app.route('/domain/<DOM_UUID>/disk/<TARGET>')
@login_required
def domain_cdrom(DOM_UUID,TARGET):
    NODE_NAME = virty.vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
    IMAGE_DATAS = virty.ImageIsoList(NODE_NAME)
    html = render_template('DomainCdromEdit.html',IMG=IMAGE_DATAS,DOM=[DOM_UUID,TARGET])
    return html


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

@app.route('/action/user/add',methods=["POST"])
@UserRoll
def action_user_add():
    virty.UserAdd(request.form['userid'],hash_password(request.form['password']))
    return redirect("/", code=302)

@app.route('/action/group/add',methods=["POST"])
@UserRoll
def action_group_add():
    virty.vsql.RawCommit("insert into groups ('id') values (?)",[request.form['groupid']])
    return redirect("/", code=302)

@app.route('/action/group/join',methods=["POST"])
@UserRoll
def action_group_join():
    virty.vsql.RawCommit("insert into users_groups ('user_id','group_id') values (?,?)",[request.form['userid'],request.form['groupid']])
    return redirect("/", code=302)

@app.route('/action/group/leave',methods=["POST"])
@UserRoll
def action_group_leave():
    virty.vsql.RawCommit("delete from users_groups where user_id=? and group_id=?",[request.form['userid'],request.form['groupid']])
    return redirect("/ui/groups", code=302)

@app.route('/action/owner/change',methods=["POST"])
@UserRoll
def action_owner_change():
    if request.form['target'] == "domain_user":
        virty.vsql.RawCommit("replace into domain_owner (dom_uuid,user_id,group_id) values (?,?,?)",[request.form['uuid'],request.form['userid'],None])
    return redirect("/", code=302)

############################
# JSON                     #
############################
@app.route('/api/sql/<TABLE_NAME>.json')
@login_required
def api_sql(TABLE_NAME):
    result=virty.vsql.SqlGetAll(TABLE_NAME)
    return jsonify(ResultSet=result)

@app.route('/api/json/<OBJECT>/')
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
    return jsonify(ResultSet=result)

@app.route('/ui/get/<OBJECT>/')
@login_required
def api_get(OBJECT):
    if OBJECT == "info":
        result={}
        result['que']=virty.vsql.SqlQueuget("running")
        result['user_id']=(current_user.id)
    return jsonify(result)

############################
# POST                     #
############################
@app.route("/api/edit/<POST_TASK>",methods=["POST"])
@login_required
def api_edit(POST_TASK):
    if POST_TASK == "cdrom":
        task = {}
        for key, value in request.form.items():
            task[key]=value
        if task['status'] == "edit":
            virty.DomCdromEdit(task['uuid'],task['target'],task['path'])
        elif task['status'] == "unmount":
            virty.DomCdromExit(task['uuid'],task['target'])
        virty.DomainListInit()
        return task

@app.route("/api/selinux",methods=["POST"])
@login_required
def api_selinux():
    task = {}
    for key, value in request.form.items():
        task[key]=value
    virty.DomSelinuxDisable(task['uuid'])
    return task

@app.route("/api/que/<OBJECT>/<METHOD>/",methods=["POST"])
@login_required
def api_que(OBJECT,METHOD):
    task = {}
    if OBJECT == "domain" and METHOD == "define":
        task["nic"] = []
        for key, value in request.form.items():
            if key == "bridge":
                for nic in request.form.getlist('bridge'):
                    task['nic'].append(["bridge",nic])
            else:
                task[key]=value
    else:
        for key, value in request.form.items():
            task[key]=value

    virty.Queuing(OBJECT,METHOD,task)
    
    return redirect(request.referrer, code=302)

if __name__ == "__main__":
    if virty.vsql.RawFetchall("select name from sqlite_master where type='table';",[]) == []:
        print("database init")
        virty.vsql.SqlInit()
    virty.WorkerUp()
    app.run(debug=True, host='0.0.0.0', port=80)