from pymongo import MongoClient
from pymongo.database import Database

# MongoDBに接続
client = MongoClient("mongodb://admin:password@mongo:27017/")  # 接続先を適宜変更
db = client["app"]  # データベース名


def get_mongo_client() -> Database:
    return db
