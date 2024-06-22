import os
import pathlib
import secrets

CLOUDFLARE_API_URL = "https://api.cloudflare.com/client/v4"
SQLALCHEMY_DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL', 'postgresql://postgres:password@db:5432/mydatabase')
APP_ROOT = os.getenv('APP_ROOT', str(pathlib.Path('./').resolve()))
DATA_ROOT = os.getenv('DATA_ROOT', str(pathlib.Path('./data').resolve()))
IS_DEV = (APP_ROOT == str(pathlib.Path('./').resolve()))
API_VERSION = '4.1.0'
SECRET_KEY = 'DEV_KEY' if IS_DEV else os.getenv('SECRET_KEY', secrets.token_urlsafe(128))

# Ansible用のパスを指定
os.environ['ANSIBLE_LIBRARY'] = APP_ROOT + "/ansible"