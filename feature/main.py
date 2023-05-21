import os
import sys
import subprocess

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

AGENT_PATH = /opt/virty

# create the extension
db = SQLAlchemy()
# create the app
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{AGENT_PATH}/agent.sqlite"
# initialize the app with the extension
db.init_app(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String)


@app.route("/")
def hello_world():
    result = subprocess.run("ls", encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    
    return result.stdout


with app.app_context():
    db.create_all()