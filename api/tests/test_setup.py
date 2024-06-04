import httpx
import json
from pprint import pprint
import time
import datetime
import sys
from common import BASE_URL, HEADERS, print_resp, tester

@tester
def api_auth_validate():
    resp = httpx.get(f'{BASE_URL}/api/auth/validate',headers=HEADERS)
    print_resp(resp=resp)

@tester
def api_users_me():
    resp = httpx.get(f'{BASE_URL}/api/users/me',headers=HEADERS)
    print_resp(resp=resp)