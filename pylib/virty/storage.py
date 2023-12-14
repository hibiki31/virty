import httpx
import time

class VirtyClinet():
    def __init__(self, url, headers) -> None:
        self.BASE_URL = url
        self.HEADERS = headers
        self.last_task = None


    def api_delete_storage(self, pool_name, node_name):
        resp = httpx.request(
            method="get", 
            url=f'{self.BASE_URL}/api/storages', 
            headers=self.HEADERS, 
            params={"name": pool_name, "nodeName": node_name}
        )

        if resp.json()["data"] == []:
            return

        pool_uuid = resp.json()["data"][0]["uuid"]

        self.last_task = httpx.request(
            method="delete",
            url=f'{self.BASE_URL}/api/tasks/storages/{pool_uuid}', 
            headers=self.HEADERS
        )
        return self.last_task 
    
    def wait_task(self):
        for task in self.last_task.json():
            uuid = task["uuid"]
            counter = 0
            while True:
                resp = httpx.request(method="get",url=f'{self.BASE_URL}/api/tasks/{uuid}', headers=self.HEADERS).json()
                # print(f"wait {uuid} {resp['resource']} {resp['object']} {counter}s")
                if resp["status"] == "finish":
                    print(f"Task Finish {uuid} {resp['resource']} {resp['object']} {counter}s")
                    break
                elif resp["status"] == "error":
                    print(f"Task Error {uuid} {resp['resource']} {resp['object']} {counter}s")
                    break
                time.sleep(0.5)
                counter += 0.5