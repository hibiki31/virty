import os
import subprocess

from flask import Flask, request, Response, jsonify
from flask_sqlalchemy import SQLAlchemy

from gunicorn.app.base import BaseApplication


from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})



AGENT_PATH = os.environ.get('VIRTY_AGENT_PATH', '/opt/virty')
SQLALCHEMY_DATABASE_URI = f"sqlite:///{AGENT_PATH}/agent.sqlite"

db = SQLAlchemy()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
db.init_app(app)


class VXLANConnection(db.Model):
    vni = db.Column(db.Integer, primary_key=True)
    node_id = db.Column(db.Integer, primary_key=True)
    remote_ip = db.Column(db.String, nullable=False)



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String)


@app.route("/")
def hello_world():
    result = subprocess.run(["ip", "a"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    result_grep = subprocess.run(["grep", "vx"], encoding='utf-8', input=result.stdout, stdout=subprocess.PIPE, check=True)
    
    return result_grep.stdout


@app.route("/ip")
def get_ip():
    result = subprocess.run(["ip", "-j", "a"], encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    
    return result.stdout


@app.route("/vxlan", methods=["GET"])
def get_vxlan():
    result = subprocess.run(["ip", "-j", "l"], encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    
    return result.stdout


@app.route("/vxlan", methods=["POST"])
def post_vxlan():
    try:
        vni = request.json['vni']
        node_id = request.json['node_id']
        remote_ip = request.json['remote_ip']
    except:
        return jsonify({"detail": "Bad request body"}), 400
    
    net_id = str('{:06x}'.format(vni))
    device_name = f"vx-{net_id}-{node_id}"
    bridge_name = f"vbr-{net_id}"


    db.session.merge(VXLANConnection(
        vni=vni,
        node_id=node_id,
        remote_ip=remote_ip
    ))

    db.session.commit()

    create_vxlan(
        device_name=device_name,
        remote_ip=remote_ip,
        vni=vni,
        bridge_name=bridge_name
        )

    return str('{:06x}'.format(vni))


@app.route("/vxlan/<int:vni>/<int:node_id>", methods=["DELETE"])
def delete_vxlan(vni, node_id):
    
    net_id = str('{:06x}'.format(vni))
    device_name = f"vx-{net_id}-{node_id}"
    bridge_name = f"vbr-{net_id}"


    vxlan_int = VXLANConnection.query.get((vni, node_id))
    db.session.delete(vxlan_int)
    db.session.commit()

    delete_vxlan(device_name)

    return str('{:06x}'.format(vni))

def create_vxlan(device_name, remote_ip, vni, bridge_name):
    res = subprocess.run(["ip", "link", "show", device_name], encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode == 1:
        res = subprocess.run([
                "sudo", "ip", "link", "add", device_name,
                "type", "vxlan", "id", str(vni), 
                "remote", remote_ip, "dstport", "4789"
            ], encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        app.logger.info(res.args)
        if res.returncode != 0:
            app.logger.error(res.stderr)
    
    

    res = subprocess.run([
            "sudo", "ip", "link", "set", device_name,
            "master", bridge_name
        ], encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    app.logger.info(res.args)
    if res.returncode != 0:
        app.logger.error(res.stderr)

    res = subprocess.run([
            "sudo", "ip", "link", "set", device_name,
            "up"
        ], encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def delete_vxlan(device_name):
    res = subprocess.run(["ip", "link", "show", device_name], encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode == 0:
        res = subprocess.run([
                "sudo", "ip", "link", "delete", device_name
            ], encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    

def run_cmd(cmd):
        return subprocess.run(cmd, encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)


class Application(BaseApplication):
    def load_config(self):
        s = self.cfg.set
        s('bind', "0.0.0.0:8766")
        s('workers', 3)
        s('keepalive', 60)
        s('timeout', 600)
        s('accesslog', "-")
        s('reload', True)
        s('access_log_format', '%(t)s %(h)s "%(r)s" %(s)s %(b)s %(D)s "%(a)s"')

    def load(self):
        return app

def setup_ip():
    vxlans = VXLANConnection.query.all()
    app.logger.info("setup")
    for vxlan in vxlans:
        net_id = str('{:06x}'.format(vxlan.vni))
        device_name = f"vx-{net_id}-{vxlan.node_id}"
        bridge_name = f"vbr-{net_id}"
        create_vxlan(
            device_name=device_name,
            remote_ip=vxlan.remote_ip,
            vni=vxlan.vni,
            bridge_name=bridge_name
        )

if __name__ == '__main__':
    os.makedirs(AGENT_PATH, exist_ok=True)
    app.logger.info(SQLALCHEMY_DATABASE_URI)

    with app.app_context():
        db.create_all()
        setup_ip()

    Application().run()