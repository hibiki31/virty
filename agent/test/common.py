import httpx
import json
from pprint import pprint
import time
import functools


env = json.load(open('./env.json', 'r'))
BASE_URL = env["base_url"]


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


def tester(f):
    @functools.wraps(f)
    def _wrapper(*args, **keywords):
        # 前処理
        print(f'-------- {f.__name__} --------')

        # デコレート対象の関数の実行
        v = f(*args, **keywords)

        # 後処理
        print(f'Return: {v}')
        print("")
        print("")

        return v
    return _wrapper


def print_resp(resp: httpx.Response, allow_not_found=False, debug=False):    
    status_ok = (200, 201)
    
    if resp.status_code in status_ok:
        print(f"{Color.BLUE}{resp} {resp.request.method} {resp.url}{Color.END}")
    else:
        print(f"{Color.RED}{resp} {resp.request.method} {resp.url}{Color.END}")

    if debug:
        pprint(resp.json())

    if allow_not_found and resp.status_code == 404:
        print(f"{Color.GREEN}Allow not found{Color.END}")
    elif resp.status_code not in status_ok:
        print(resp.json())
        raise Exception