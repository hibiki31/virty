import httpx
from common import BASE_URL, HEADERS, env, print_resp, tester


@tester
def create_flavors():
    req_data = env["flavors"][0]
    resp = httpx.request(method="post", url=f'{BASE_URL}/api/flavors', json=req_data, headers=HEADERS)
    print_resp(resp=resp)
    
    resp = httpx.request(method="get", url=f'{BASE_URL}/api/flavors', headers=HEADERS)
    print_resp(resp=resp, debug=True)


@tester
def delete_flavors():
    resp = httpx.request(
        method="get", 
        url=f'{BASE_URL}/api/flavors', 
        params={"nameLike": env["flavors"][0]["name"]},
        headers=HEADERS
    )
    print_resp(resp=resp, debug=True)
    
    for i in resp.json()["data"]:
        flavor_id = i["id"]
        resp = httpx.request(method="delete", url=f'{BASE_URL}/api/flavors/{flavor_id}', headers=HEADERS)
        print_resp(resp=resp, debug=True)