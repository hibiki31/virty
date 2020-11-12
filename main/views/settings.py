from flask import Flask
from flask import Blueprint
from flask import render_template
from flask import request
from flask_login import login_required
from module import virty



app = Blueprint('settings', __name__)



@app.route('/setting',methods=["POST","GET"])
@login_required
def setting():
    if request.method == 'POST':
        if request.form["status"] == "dbinit":
            virty.vsql.SqlInit()
            return "database init"
    elif request.method == 'GET':
        html = render_template('Setting.html')
        return html


