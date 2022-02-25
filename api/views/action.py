from flask import Flask
from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask_login import login_required
from module import virty



app = Blueprint('action', __name__)



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