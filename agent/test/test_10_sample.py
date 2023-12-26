import httpx

from common import *


def main():
    get_index()
    get_users_id()
    get_users_query()
    post_users()
    

@tester
def get_index():
    resp = httpx.get(url=f'{BASE_URL}/sample')
    print_resp(resp=resp)
    return resp.headers, resp.text


@tester
def get_users_id():
    users_id = 1241351
    resp = httpx.get(url=f'{BASE_URL}/sample/users/{users_id}')
    print_resp(resp=resp)
    return resp.headers, resp.text


@tester
def get_users_query():
    query_params = {
        "member": "test_member",
        "team": "test_teams"
    }
    resp = httpx.get(url=f'{BASE_URL}/sample/users',params=query_params)
    print_resp(resp=resp)
    return resp.headers, resp.text


@tester
def post_users():
    send_json = {
        "name": "hibiki31",
        "email": "sample@example.com"
    }
    resp = httpx.post(url=f'{BASE_URL}/sample/users', json=send_json)
    print_resp(resp=resp, debug=True)
    return resp.headers