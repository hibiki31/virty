import httpx
import time


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from virty.client import VirtyClinet


def delete(self: 'VirtyClinet', pool_name, node_name):
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
