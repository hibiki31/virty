from flask import Flask, render_template, jsonify, request,redirect, Response, abort, send_from_directory, Blueprint
from flask_jwt import JWT, jwt_required, current_identity
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import safe_str_cmp
from functools import wraps
from time import sleep
import subprocess, logging, bcrypt
from module import virty

app = Blueprint('queue', __name__)


@app.route('/queue',methods=["GET"])
@login_required
def queue():
    domain = virty.vsql.RawFetchall("select * from que order by que_id desc",[])
    html = render_template('QueList.html',domain=domain,status=virty.WorkerStatus())
    return html


@app.route('/queue/log/<ID>/<STATUS>',methods=["GET"])
@login_required
def queue_log_id_status(ID,STATUS):
    if STATUS == "err":
        return str(virty.queueLogErr(ID))
    elif STATUS == "out":
        return str(virty.queueLogOut(ID))
    else:
        return abort(400)

@app.route('/queue/status/<ID>',methods=["GET"])
@login_required
def queue_status_id(ID):
    if request.args.get('interval') != None:
        try:
            interval = int(request.args.get('interval'))
        except:
            return abort(400)
        
        for i in range(interval,0,-100):
            if virty.vsql.RawFetchall("select que_status from que where que_id = ?",[ID])[0][0] == "success":
                return jsonify(status=virty.vsql.RawFetchall("select que_status from que where que_id = ?",[ID])[0][0])
            else:
                sleep(0.1)
        return jsonify(status=virty.vsql.RawFetchall("select que_status from que where que_id = ?",[ID])[0][0])
    else:
        return jsonify(status=virty.vsql.RawFetchall("select que_status from que where que_id = ?",[ID])[0][0])



@app.route('/queue',methods=["POST"])
@login_required
def queue_post():
    if request.form.get('status') == "que_clear":
        virty.vsql.RawCommit("delete from que",[])
        return redirect("/queue",code=303)
    else:
        return abort(400)
