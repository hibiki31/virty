import httpx
from common import BASE_URL, env, HEADERS, print_resp, wait_tasks, tester


@tester
def create_project():
    for env_row in env["projects"]:
        req_data = {
            "projectName": env_row["name"],
            "userIds": [env["username"], env["users"][0]["username"]]
        }
        resp = httpx.request(method="post", url=f'{BASE_URL}/api/tasks/projects', json=req_data, headers=HEADERS)
        print_resp(resp=resp)
        wait_tasks(resp=resp)


@tester
def delete_project():
    get_resp = httpx.get(url=f'{BASE_URL}/api/projects', params={"name": "test"},headers=HEADERS)
    print_resp(resp=get_resp)
        
    for resp_row in get_resp.json():
        resp = httpx.request(method="delete", url=f'{BASE_URL}/api/tasks/projects/{resp_row["id"]}', headers=HEADERS)
        print_resp(resp=resp)
        wait_tasks(resp=resp)