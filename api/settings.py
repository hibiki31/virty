import os
import pathlib
import secrets

API_VERSION = '5.1.2'
SQLALCHEMY_DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL', 'postgresql://postgres:password@db:5432/mydatabase')
IS_DEV = bool(os.getenv('IS_DEV', False))
APP_ROOT = str(pathlib.Path('./').resolve()) if IS_DEV else "/opt/app"
DATA_ROOT = str(pathlib.Path('./data').resolve()) if IS_DEV else "/opt/data"
SECRET_KEY = 'DEV_KEY' if IS_DEV else os.getenv('SECRET_KEY', secrets.token_hex(32))
LOG_MODE = os.getenv('LOG_MODE', "TEXT")