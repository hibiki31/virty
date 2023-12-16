import httpx
import time

import virty.storage

class VirtyClinet:
    def __init__(self, url, headers) -> None:
        self.BASE_URL = url
        self.HEADERS = headers
        self.last_task = None
        
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

    storage_delete = virty.storage.delete