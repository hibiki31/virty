import httpx

from common import BASE_URL, env, HEADERS, print_resp, wait_tasks, tester


@tester
def download_image():
    for server in env["servers"]:
        resp = httpx.request(method="get", url=f'{BASE_URL}/api/storages', headers=HEADERS, params={"name": "test-cloud", "nodeName": server["name"]})
        print_resp(resp=resp)
        
        req_data={
            "storage_uuid": resp.json()["data"][0]["uuid"],
            "image_url": env["image_url"]
        }
        resp = httpx.request(method="post",url=f'{BASE_URL}/api/tasks/images/download', headers=HEADERS, json=req_data)
        print_resp(resp=resp)
        wait_tasks(resp)
