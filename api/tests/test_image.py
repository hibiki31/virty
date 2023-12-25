import httpx

from common import BASE_URL, env, HEADERS, print_resp, wait_tasks, tester


@tester
def test_image_download():
    for server in env["servers"]:
        image_download(node_name=server["name"], storage_name="test-cloud", image_url=env["image_url"])
        image_download(node_name=server["name"], storage_name="test-iso", image_url=env["iso_url"])
        

def image_download(node_name, storage_name, image_url):
    resp = httpx.request(method="get", url=f'{BASE_URL}/api/storages', headers=HEADERS, params={"nameLike": storage_name, "nodeName": node_name})
    print_resp(resp=resp)
    
    req_data={
        "storage_uuid": resp.json()["data"][0]["uuid"],
        "image_url": image_url
    }
    resp = httpx.request(method="post",url=f'{BASE_URL}/api/tasks/images/download', headers=HEADERS, json=req_data)
    print_resp(resp=resp)
    wait_tasks(resp)
    
    