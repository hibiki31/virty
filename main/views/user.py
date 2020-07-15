from flask import Flask
from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import abort
from flask_login import login_required
from module import virty



app = Blueprint('user', __name__)



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
                virty.UserReset(request.form['user-id'],virty.hash_password(request.form['password']))
                return redirect("/user", code=303)
        elif request.form.get('method') == "add":
            if request.form.get('user-id') == None or request.form.get('password') == None:
                return abort(400)
            else:
                if virty.userIsExist(request.form['user-id']):
                    return abort(400)
                else:
                    virty.UserAdd(request.form['user-id'],virty.hash_password(request.form['password']))
                    return redirect("/user", code=303)
        else:
            return abort(400)

