import requests, json

class Color():
    RED       = '\033[31m'
    GREEN     = '\033[32m'
    BLUE      = '\033[34m'
    CYAN      = '\033[36m'
    END       = '\033[0m'


def LogInfo(TAG,TEXT):
    print("[" + Color.CYAN + TAG + Color.END + "] " +  str(TEXT))

def LogError(TAG,TEXT):
    print("[" + Color.RED + TAG + Color.END + "] " +  str(TEXT))

def LogSuccess(TAG,TEXT):
    print("[" + Color.GREEN + TAG + Color.END + "] " +  str(TEXT))


class api ():
    def __init__(self, endpoint):
        self.endpoint = endpoint

    def domain_define(self, DOMAIN_DATA):
        response = requests.post(self.endpoint+"/api/create/domain/define", data=DOMAIN_DATA, headers=self.headers)
        if response.status_code == 200:
            res_json = json.loads(response.text)
            print(res_json)
            LogSuccess("OK","Domain define " + DOMAIN_DATA["name"] + " Queue ID: " + str(res_json["que-id"]))
        else:
            LogError("VM","Domain define " + DOMAIN_DATA["name"] + "response http code is " + str(response.status_code))

    def domain_undefine(self, DOMAIN_NAME):
        DOMAIN_DATA = {}
        DOMAIN_DATA["domain-list"] = DOMAIN_NAME
        response = requests.post(self.endpoint+"/api/que/domain/undefine/", data=DOMAIN_DATA)
        if response.status_code == 200:
            LogSuccess("OK","Domain undefine " + DOMAIN_DATA["domain-list"])
        else:
            LogError("ER","Domain undefine " + DOMAIN_DATA["domain-list"])

    def domain_data(self):
        return requests.get(self.endpoint+"/api/read/domain",headers=self.headers).json()

    def domain_start(self, DOMAIN_NAME):
        POST_DATA = {}
        POST_DATA["domain-list"] = DOMAIN_NAME
        POST_DATA["status"] = "poweron"
        response = requests.post(self.endpoint+"/api/que/domain/power/", data=POST_DATA)
        if response.status_code == 200:
            LogSuccess("OK","Domain start " + DOMAIN_NAME)
        else:
            LogError("ER","Domain start " + DOMAIN_NAME)

    def domain_stop(self, DOMAIN_NAME):
        POST_DATA = {}
        POST_DATA["domain-list"] = DOMAIN_NAME
        POST_DATA["status"] = "poweroff"
        response = requests.post(self.endpoint+"/api/que/domain/power/", data=POST_DATA)
        if response.status_code == 200:
            LogSuccess("OK","Domain stop " + DOMAIN_NAME)
        else:
            LogError("ER","Domain stop " + DOMAIN_NAME)


    def auth_login(self, userid,password):
        post_data = {"userid":userid,"passwd":password}
        response = requests.post(self.endpoint+"/auth",json.dumps(post_data),headers={'Content-Type': 'application/json'})
    
        if response.status_code == 200:
            self.token = json.loads(response.text)['access_token']
            self.headers = {'Authorization': 'JWT ' + self.token}
            LogInfo("AUTH","Succsess login.")
        elif response.status_code == 401:
            LogError("AUTH","Worng password or user_id.")
        else:
            LogError("AUTH","Login fail. http status code is "+str(response.status_code))

    def is_authed(self):
        response = requests.get(self.endpoint+"/protected",headers={'Authorization': 'JWT '+self.token})
        LogInfo("AUTH",response.text)