from flask import Flask
from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import abort
from flask_login import login_required
from module import virty



app = Blueprint('group', __name__)



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