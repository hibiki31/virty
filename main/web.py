from flask import Flask, render_template, jsonify, request
import virty,time,subprocess
from time import  sleep

virty.Pooler()



app = Flask(__name__)


@app.route('/')
def route():
    DATA = virty.SqlSumDomain()
    if DATA[0] > 1000:
        DATA[0] = str(int(DATA[0])/1000) + "GB"
    html = render_template('index.html',domain=virty.SqlGetAll("kvm_domain"),sumdata= DATA)
    return html

@app.route('/domain/info/<DOM_NAME>')
def info_domain(DOM_NAME):
    html = render_template('DomainInfo.html',domain=virty.VirtyDomXmlSummryGet(DOM_NAME))
    return html

@app.route('/node/list')
def node_list():
    html = render_template('NodeList.html',domain=virty.SqlGetAll("kvm_node"),sumdata=virty.SqlSumNode())
    return html

@app.route('/archive/list')
def archive_list():
    html = render_template('ArchiveList.html',domain=virty.SqlGetAll("kvm_archive"))
    return html

@app.route('/domain/add')
def domain_add():
    virty.Pooler()
    html = render_template('DomainAdd.html',domain=virty.SqlGetAll("kvm_archive"))
    return html

@app.route('/domain/power')
def domain_power():
    virty.Pooler()
    html = render_template('DomainPower.html',domain=virty.SqlGetAll("kvm_domain"))
    return html

@app.route('/domain/listinit')
def domain_listinit():
    virty.Pooler()
    html = render_template('DomainListinit.html')
    return html

@app.route('/storage/list')
def storage_list():
    html = render_template('StorageList.html',domain=virty.SqlGetAll("kvm_storage"))
    return html

@app.route('/network/list')
def network_list():
    html = render_template('NetworkList.html',domain=virty.SqlGetAll("kvm_network"))
    return html

@app.route('/node/add')
def node_add():
    html = render_template('NodeAdd.html')
    return html

@app.route('/api/domainlist.json')
def hello_world():
    result=virty.SqlGetAll("kvm_domain")
    return jsonify(ResultSet=result)

@app.route('/api/node_list.json')
def api_node_list():
    result=virty.SqlGetAll("kvm_node")
    return jsonify(ResultSet=result)

@app.route('/api/archive_list.json')
def api_archive_list():
    result=virty.SqlGetAll("kvm_archive")
    return jsonify(ResultSet=result)

@app.route('/api/sql/<TABLE_NAME>.json')
def api_sql(TABLE_NAME):
    result=virty.SqlGetAll(TABLE_NAME)
    return jsonify(ResultSet=result)

@app.route("/api/domain/add",methods=["POST"])
def api_domain_add():
    response = str(request.form)
    task = {}
    task["nic"] = []
    for key, value in request.form.items():
        if key == "bridge":
            task['nic'].append(["bridge",value])
        else:
            task[key]=value
    virty.SqlQueDomain("domain",task)
    return task

@app.route("/api/domain/power",methods=["POST"])
def api_domain_power():
    response = str(request.form)
    task = {}
    for key, value in request.form.items():
        task[key]=value
    virty.SqlQueDomain("power",task)
    return task

@app.route("/api/domain/listinit",methods=["POST"])
def api_domain_listinit():
    response = str(request.form)
    task = {}
    for key, value in request.form.items():
        task[key]=value
    virty.SqlQueDomain("listinit",task)
    return task

if __name__ == "__main__":
    virty.Pooler()    
    app.run(debug=True, host='0.0.0.0', port=80)