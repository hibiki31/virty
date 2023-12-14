import httpx
from pprint import pprint
import time
import datetime

from module.settings import *


class Color:
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
    
    
def method_color(method):
    if method == "delete":
        return f"{Color.RED}delete{Color.END}"
    elif method == "post":
        return f"{Color.BLUE}post{Color.END}"
    elif method == "put":
        return f"{Color.YELLOW}put{Color.END}"


def complete_name():
    return ["aa"]


def pase_date_short(date_str):
    pase_datetime =  datetime.datetime.fromisoformat(date_str)

    local_timezone = datetime.datetime.now().astimezone().tzinfo

    return pase_datetime.astimezone(local_timezone).strftime('%Y-%m-%d %H:%M:%S')


def wait_tasks(resp):
    for task in resp.json():
        uuid = task["uuid"]
        counter = 0
        while True:
            resp = httpx.request(method="get",url=f'{BASE_URL}/api/tasks/{uuid}', headers=HEADERS).json()
            # print(f"wait {uuid} {resp['resource']} {resp['object']} {counter}s")
            if resp["status"] == "finish":
                print(f"{Color.GREEN}Task Finish {Color.END}{uuid} {resp['resource']} {resp['object']} {counter}s")
                break
            elif resp["status"] == "error":
                print(f"{Color.RED}Task Error {Color.END}{uuid} {resp['resource']} {resp['object']} {counter}s")
                break
            time.sleep(0.5)
            counter += 0.5


def print_resp(resp: httpx.Response, allow_not_found=False, debug=False):    
    if resp.status_code == 200:
        print(f"{Color.BLUE}{resp} {resp.request.method} {resp.url}{Color.END}")
    else:
        print(f"{Color.RED}{resp} {resp.request.method} {resp.url}{Color.END}")

    if debug:
        pprint(resp.json())

    if allow_not_found and resp.status_code == 404:
        print(f"{Color.GREEN}Allow not found{Color.END}")
    elif resp.status_code != 200:
        print(resp.json())
        raise Exception