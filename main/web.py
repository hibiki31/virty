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
# SETTING                  #
############################
@app.route('/setting',methods=["DELETE","GET"])
def setting():
    if request.method == 'DELETE':
        if request.form["status"] == "dbinit":
            virty.vsql.SqlInit()
            return "database init"
    elif request.method == 'GET':
        html = render_template('setting.html')
        return html




############################
# DOMAIN                   #
############################
@app.route('/domain',methods=["GET"])
def domain():
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
            domain = virty.vsql.RawFetchall("select * from domain left join domain_owner on uuid=domain_owner.dom_uuid",[])
            users = virty.vsql.SqlGetAll("users")
            groups = virty.vsql.SqlGetAll("groups")
            html = render_template('DomainList.html',domain=domain,users=users,groups=groups)
        else:
            SQL = "select * from domain left join domain_owner on uuid=domain_owner.dom_uuid where domain_owner.user_id=? or domain_owner.group_id in (select group_id from users_groups where user_id =?)"
            domain = virty.vsql.RawFetchall(SQL,[current_user.id,current_user.id])
            users = virty.vsql.SqlGetAll("users")
            groups = virty.vsql.SqlGetAll("groups")
            html = render_template('DomainList.html',domain=domain,users=users,groups=groups)
    return html



############################
# ARCHIVE                  #
############################
@app.route('/archive',methods=["GET"])
def archive():
    html = render_template('ArchiveList.html',domain=virty.ImageArchiveListAll())
    return html




############################
# NETWORK                  #
############################
@app.route('/network',methods=["GET"])
def network():
    html = render_template('NetworkList.html',networks=virty.vsql.SqlGetAll("network"),node=virty.vsql.SqlGetAll("node"))
    return html




############################
# IMAGE                    #
############################
@app.route('/image',methods=["GET"])
def image():
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
    elif request.args.get('ui') == "edit":
        data = [request.args.get('node'),request.args.get('pool'),request.args.get('target')]
        html = render_template('ImageEdit.html',data=data)
    else:
        images = virty.vsql.RawFetchall("select img.name,img.node,img.pool,img.capa,img.allocation,img.physical,img.path,domain.name,count(*) from img left join domain_drive on img.path=domain_drive.source left join domain on domain_drive.dom_uuid=domain.uuid and img.node=domain.node_name group by img.node,img.path;",[])
        html = render_template('ImageList.html',images=images)

    return html




############################
# STORAGE                  #
############################
@app.route('/storage',methods=["GET"])
def storage():
    if request.args.get('ui') == "undefine":
        html = render_template('StorageUndefine.html',domain=[request.args.get('node'),request.args.get('pool')])
    else:
        data = virty.vsql.SqlGetAll('storage')
        html = render_template('StorageList.html',data=data)
    return html




############################
# NODE                     #
############################
@app.route('/node',methods=["GET"])
def node():
    html = render_template('NodeList.html',domain=virty.vsql.SqlGetAll("node"),sumdata=virty.vsql.SqlSumNode())
    return html




############################
# QUEUE                    #
############################
@app.route('/queue',methods=["GET"])
def queue():
    domain = virty.vsql.RawFetchall("select * from que order by que_id desc",[])
    html = render_template('QueList.html',domain=domain,status=virty.WorkerStatus())
    return html




############################
# USER                     #
############################
@app.route('/user',methods=["GET"])
def user():
    groups = {}
    for i in virty.vsql.SqlGetAll("users_groups"):
        if groups.get(i[0],False):
            groups[i[0]].append(i[1])
        else:
            groups[i[0]] = [i[1]]
    html = render_template('UserList.html',users=virty.vsql.SqlGetAll("users"),groups=groups)
    return html




############################
# GROUP                    #
############################
@app.route('/group',methods=["GET"])
def group():
    groups = {}
    for i in virty.vsql.SqlGetAll("users_groups"):
        if groups.get(i[1],False):
            groups[i[1]].append(i[0])
        else:
            groups[i[1]] = [i[0]]
    html = render_template('GroupList.html',users=virty.vsql.SqlGetAll("groups"),groups=groups)
    return html

     


############################
# MAKE                     #
############################
@app.route('/make/domain')
@login_required
def domain_add():
    virty.WorkerUp()
    html = render_template('DomainDefine.html',node=virty.vsql.SqlGetAll("node"))
    return html

@app.route('/make/node')
@login_required
def node_add():
    virty.WorkerUp()
    html = render_template('NodeAdd.html')
    return html

@app.route('/make/storage')
@login_required
def storage_add():
    virty.WorkerUp()
    html = render_template('StorageAdd.html')
    return html

@app.route('/make/network')
@login_required
def network_add():
    virty.WorkerUp()
    html = render_template('NetworkAdd.html')
    return html

@app.route('/make/user')
@login_required
def user_add():
    users = virty.vsql.SqlGetAll("users")
    groups = virty.vsql.SqlGetAll("groups")
    virty.WorkerUp()
    html = render_template('UserAdd.html',users=users,groups=groups)
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
    virty.vsql.RawCommit("insert or ignore into domain_owner (dom_uuid,user_id,group_id) values (?,?,?)",[request.form['uuid'],None,None])
    if request.form['target'] == "domain_user":
        if request.form['status'] == "delete":
            virty.vsql.RawCommit("update domain_owner set user_id=? where dom_uuid=?",[None,request.form['uuid']])
        elif request.form['status'] == "change":
            virty.vsql.RawCommit("update domain_owner set user_id=? where dom_uuid=?",[request.form['userid'],request.form['uuid']])
    elif request.form['target'] == "domain_group":
        if request.form['status'] == "delete":
            virty.vsql.RawCommit("update domain_owner set group_id=? where dom_uuid=?",[None,request.form['uuid']])
        elif request.form['status'] == "change":
            virty.vsql.RawCommit("update domain_owner set group_id=? where dom_uuid=?",[request.form['groupid'],request.form['uuid']])
    return redirect("/", code=302)

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




############################
# API                      #
############################
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