import requests, json

class Color():
    BLACK     = '\033[30m'
    RED       = '\033[31m'
    GREEN     = '\033[32m'
    YELLOW    = '\033[33m'
    BLUE      = '\033[34m'
    PURPLE    = '\033[35m'
    CYAN      = '\033[36m'
    WHITE     = '\033[37m'
    END       = '\033[0m'
    BOLD      = '\038[1m'
    UNDERLINE = '\033[4m'
    INVISIBLE = '\033[08m'
    REVERCE   = '\033[07m'

def LogInfo(TAG,TEXT):
    print("[" + Color.CYAN + TAG + Color.END + "] " +  TEXT)

def LogError(TAG,TEXT):
    print("[" + Color.RED + TAG + Color.END + "] " +  TEXT)

def LogSuccess(TAG,TEXT):
    print("[" + Color.GREEN + TAG + Color.END + "] " +  TEXT)

API_URL = "http://localhost:80"
API_TOKEN = ""

def domain_define(DOMAIN_DATA):
    response = requests.post(API_URL+"/api/que/domain/define/", data=DOMAIN_DATA)
    if response.status_code == 200:
        LogSuccess("OK","Domain define " + DOMAIN_DATA["name"])
    else:
        LogError("ER","Domain define " + DOMAIN_DATA["name"])

def domain_undefine(DOMAIN_NAME):
    DOMAIN_DATA = {}
    DOMAIN_DATA["domain-list"] = DOMAIN_NAME
    response = requests.post(API_URL+"/api/que/domain/undefine/", data=DOMAIN_DATA)
    if response.status_code == 200:
        LogSuccess("OK","Domain undefine " + DOMAIN_DATA["domain-list"])
    else:
        LogError("ER","Domain undefine " + DOMAIN_DATA["domain-list"])

def domain_data():
    return requests.get(API_URL+"/api/sql/dom.json").json()['ResultSet']

def domain_start(DOMAIN_NAME):
    POST_DATA = {}
    POST_DATA["domain-list"] = DOMAIN_NAME
    POST_DATA["status"] = "poweron"
    response = requests.post(API_URL+"/api/que/domain/power/", data=POST_DATA)
    if response.status_code == 200:
        LogSuccess("OK","Domain start " + DOMAIN_NAME)
    else:
        LogError("ER","Domain start " + DOMAIN_NAME)

def domain_stop(DOMAIN_NAME):
    POST_DATA = {}
    POST_DATA["domain-list"] = DOMAIN_NAME
    POST_DATA["status"] = "poweroff"
    response = requests.post(API_URL+"/api/que/domain/power/", data=POST_DATA)
    if response.status_code == 200:
        LogSuccess("OK","Domain stop " + DOMAIN_NAME)
    else:
        LogError("ER","Domain stop " + DOMAIN_NAME)


def auth_login(USER,PASSWORD):
    POST_DATA = {}
    POST_DATA["username"] = USER
    POST_DATA["password"] = PASSWORD
    global API_TOKEN
    response = requests.post(API_URL+"/auth",json.dumps(POST_DATA),headers={'Content-Type': 'application/json'})
    print(response.status_code)
    token = json.loads(response.text)
    API_TOKEN = token['access_token']

def auth_token(TOKEN):
    global API_TOKEN
    API_TOKEN = TOKEN



def auth_test():
    response = requests.get(API_URL+"/protected",headers={'Authorization': 'JWT '+API_TOKEN})
    print(response.text)