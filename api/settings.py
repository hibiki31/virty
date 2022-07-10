import os
import pathlib
import secrets


SQLALCHEMY_DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL', 'postgresql://postgres:password@localhost:5432/mydatabase')
APP_ROOT = os.getenv('APP_ROOT', str(pathlib.Path('./').resolve()))
DATA_ROOT = os.getenv('DATA_ROOT', str(pathlib.Path('./data').resolve()))
IS_DEV = (APP_ROOT == str(pathlib.Path('./').resolve()))
API_VERSION = '3.0.3'
SECRET_KEY = 'DEV_KEY' if IS_DEV else os.getenv('SECRET_KEY', secrets.token_urlsafe(128))

# Ansible用のパスを指定
os.environ['ANSIBLE_LIBRARY'] = APP_ROOT + "/ansible"