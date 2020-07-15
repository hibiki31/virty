import json
from flask import Flask
from flask import Response
from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import abort
from flask import jsonify
from flask import send_from_directory
from flask_login import login_required
from flask_jwt import jwt_required
from module import virty

app = Blueprint('archive', __name__)

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