import os
import json


CONFIG_PATH = f'{os.environ["HOME"]}/.virty_auth'
BASE_URL = ""
HEADERS = {}


if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'r') as f:
        auth_json = json.load(f)
        BASE_URL = auth_json["BASE_URL"]
        HEADERS = auth_json["HEADERS"]