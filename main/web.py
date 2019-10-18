from flask import Flask, render_template, jsonify, request,redirect
from time import  sleep
import subprocess
import virty

app = Flask(__name__)

@app.route('/setup',methods=["POST","GET"])
def setup():
    if request.method == 'POST':
        if request.form["status"] == "dbinit":
            virty.vsql.SqlInit()
            return "database init"
    elif request.method == 'GET':
        html = render_template('Setup.html')
        return html



@app.route('/')
def route():
    DATA = virty.vsql.SqlSumDomain()
    if DATA[0] > 1000:
        DATA[0] = str(int(DATA[0])/1000) + "GB"
    html = render_template('DomainList.html',domain=virty.vsql.SqlGetAll("kvm_domain"),sumdata= DATA)
    return html

@app.route('/domain/info/<DOM_NAME>')
def info_domain(DOM_NAME):
    html = render_template('DomainInfo.html',domain=virty.VirtyDomXmlSummryGet(DOM_NAME))
    return html

@app.route('/domain/<DOM_UUID>/info')
def domain_info(DOM_UUID):
    html = render_template('DomainInfo.html',domain=virty.DomainData(DOM_UUID))
    return html

@app.route('/domain/<DOM_UUID>/nic/<DOM_MAC>')
def domain_nic(DOM_UUID,DOM_MAC):
    NODE_NAME = virty.vsql.Convert("DOM_UUID","NODE_NAME",DOM_UUID)
    NETWORK_DATAS = virty.vsql.Convert("NODE_NAME","NETWORK_DATAS",NODE_NAME)
    html = render_template('DomainNicEdit.html',NET=NETWORK_DATAS,DOM=[DOM_UUID,DOM_MAC])
    return html


@app.route('/list/<GET_DATA>')
def node_list(GET_DATA):
    if GET_DATA == "node":
        html = render_template('NodeList.html',domain=virty.vsql.SqlGetAll("kvm_node"),sumdata=virty.vsql.SqlSumNode())
        return html
    elif GET_DATA == "archive":
        html = render_template('ArchiveList.html',domain=virty.vsql.SqlGetAll("kvm_archive"))
        return html
    elif GET_DATA == "storage":
        html = render_template('StorageList.html',domain=virty.vsql.SqlGetAll("kvm_storage"))
        return html
    elif GET_DATA == "network":
        html = render_template('NetworkList.html',domain=virty.vsql.SqlGetAll("kvm_network"))
        return html
    elif GET_DATA == "que":
        html = render_template('QueList.html',domain=virty.vsql.SqlGetAll("kvm_que"),status=virty.QueuStatus())
        return html


@app.route('/domain/define')
def domain_add():
    virty.Pooler()
    html = render_template('DomainDefine.html',domain=virty.vsql.SqlGetAll("kvm_archive"))
    return html

@app.route('/network/2ldefine')
def net_define():
    virty.Pooler()
    html = render_template('NetworkDefine2l.html')
    return html

@app.route('/domain/power')
def domain_power():
    virty.Pooler()
    html = render_template('DomainPower.html',domain=virty.vsql.SqlGetAll("kvm_domain"))
    return html

@app.route('/domain/undefine')
def domain_undefine():
    virty.Pooler()
    html = render_template('DomainUndefine.html',domain=virty.vsql.SqlGetAll("kvm_domain"))
    return html
 

@app.route('/domain/listreload')
def domain_listinit():
    virty.Pooler()
    html = render_template('DomainListReload.html')
    return html

@app.route('/node/add')
def node_add():
    virty.Pooler()
    html = render_template('NodeAdd.html')
    return html

@app.route('/domain/nameedit')
def domainname_edit():
    virty.Pooler()
    html = render_template('DomainNameEdit.html',domain=virty.vsql.SqlGetAll("kvm_domain"))
    return html

@app.route('/storage/add')
def storage_add():
    virty.Pooler()
    html = render_template('StorageAdd.html')
    return html

@app.route('/network/add')
def network_add():
    virty.Pooler()
    html = render_template('NetworkAdd.html')
    return html

@app.route('/api/sql/<TABLE_NAME>.json')
def api_sql(TABLE_NAME):
    result=virty.vsql.SqlGetAll(TABLE_NAME)
    return jsonify(ResultSet=result)

@app.route('/api/getque.json')
def api_getque():
    result=virty.vsql.SqlQueuget()
    return jsonify(ResultSet=result)

@app.route("/api/add/<POST_TASK>",methods=["POST"])
def api_add(POST_TASK):
    if POST_TASK == "domain":
        task = {}
        task["nic"] = []
        for key, value in request.form.items():
            if key == "bridge":
                for nic in request.form.getlist('bridge'):
                    task['nic'].append(["bridge",nic])
            else:
                task[key]=value
        virty.vsql.SqlQueuing("domain",task)
        return task
    elif POST_TASK == "que_clear":
        if request.form["status"] == "que_clear":
            virty.vsql.SqlDeleteAll("kvm_que")
            return "que_list_clear"
    elif POST_TASK == "undefine":
        task = {}
        for key, value in request.form.items():
            task[key]=value
        virty.vsql.SqlQueuing("undefine",task)
        return task
    elif POST_TASK == "power":
        task = {}
        for key, value in request.form.items():
            task[key]=value
        virty.vsql.SqlQueuing("power",task)
        return redirect("/domain/power", code=302)
    elif POST_TASK == "dom_reload":
        task = {}
        for key, value in request.form.items():
            task[key]=value
        virty.vsql.SqlQueuing("listinit",task)
        return redirect("/", code=302)

    elif POST_TASK == "network2l":
        task = {}
        for key, value in request.form.items():
            task[key]=value
        virty.vsql.SqlQueuing("2ldefine",task)
        return task

    elif POST_TASK == "node":
        task = {}
        for key, value in request.form.items():
            task[key]=value
        virty.vsql.SqlQueuing("nodeadd",task)
        return task

    elif POST_TASK == "storage":
        task = {}
        for key, value in request.form.items():
            task[key]=value
        virty.vsql.SqlQueuing("storage",task)
        return task

    elif POST_TASK == "network":
        task = {}
        for key, value in request.form.items():
            task[key]=value
        virty.vsql.SqlAddNetwork([(task['name'],task['node-list'],task['source'])])
        return task

@app.route("/api/edit/<POST_TASK>",methods=["POST"])
def api_edit(POST_TASK):
    if POST_TASK == "dom_name":
        task = {}
        for key, value in request.form.items():
            task[key]=value
        virty.vsql.SqlQueuing("domnameedit",task)
        return task
    elif POST_TASK == "dom_nic":
        task = {}
        for key, value in request.form.items():
            task[key]=value
        virty.vsql.SqlQueuing("dom_nic",task)
        return task


@app.route("/api/selinux",methods=["POST","DELETE"])
def api_selinux():
    task = {}
    for key, value in request.form.items():
        task[key]=value
    virty.DomSelinuxDisable(task['uuid'])
    return task


if __name__ == "__main__":
    virty.Pooler()    
    app.run(debug=True, host='0.0.0.0', port=80)