import os
import pathlib

API_VERSION = '5.1.2'
SQLALCHEMY_DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL', 'postgresql://postgres:password@db:5432/mydatabase')
IS_DEV = os.getenv('IS_DEV', '').lower() in {'1', 'true', 'yes'}
APP_ROOT = str(pathlib.Path('./').resolve()) if IS_DEV else "/opt/app"
DATA_ROOT = str(pathlib.Path('./data').resolve()) if IS_DEV else "/opt/data"
SECRET_KEY = 'DEV_KEY' if IS_DEV else os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise RuntimeError('本番環境ではSECRET_KEYの設定が必要です')
if not IS_DEV and len(SECRET_KEY) < 32:
    raise RuntimeError('SECRET_KEYは32文字以上で設定してください')
LOG_MODE = os.getenv('LOG_MODE', "TEXT")
JWT_ISSUER = os.getenv('JWT_ISSUER', 'virty')
JWT_AUDIENCE = os.getenv('JWT_AUDIENCE', 'virty-api')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '60'))
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv('CORS_ORIGINS', '').split(',')
    if origin.strip()
]
