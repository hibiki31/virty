from pathlib import PurePosixPath
from urllib.parse import quote, urlparse

from fastapi.testclient import TestClient

from images.function import url_body_size
from images.schemas import ImagePage
from storage.schemas import StoragePage
from tests.external.conftest import wait_tasks
from tests.external.support.remote_inventory import (
    assert_remote_path_absent,
    remote_file_metadata,
    remote_inventory_manager,
)


def _refresh_images(client: TestClient) -> None:
    response = client.put("/api/tasks/images")
    response.raise_for_status()
    assert wait_tasks(response, client) == "finish"


def _exact_storage(page: StoragePage, name: str, node_name: str):
    return [
        storage
        for storage in page.data
        if storage.name == name and storage.node_name == node_name
    ]


def _exact_images(page: ImagePage, storage_uuid: str, name: str, path: str):
    return [
        image
        for image in page.data
        if image.storage_uuid == storage_uuid
        and image.name == name
        and image.path == path
    ]


def test_image_download_inventory_and_delete(env, client, created_storage) -> None:
    targets = (
        (
            next(
                item.name
                for item in env.storages
                if item.name.endswith("test-cloud")
            ),
            env.image_url,
        ),
        (
            next(
                item.name
                for item in env.storages
                if item.name.endswith("test-iso")
            ),
            env.iso_url,
        ),
    )
    for server_index, server in enumerate(env.servers):
        with remote_inventory_manager(
            user=server.username,
            domain=server.domain,
            server_index=server_index,
        ) as remote:
            for storage_name, image_url in targets:
                response = client.get(
                    "/api/storages",
                    params={"nameLike": storage_name, "nodeName": server.name},
                )
                response.raise_for_status()
                exact_storage = _exact_storage(
                    StoragePage.model_validate(response.json()),
                    storage_name,
                    server.name,
                )
                if len(exact_storage) != 1:
                    raise AssertionError(
                        "image storage precondition failed: "
                        f"server_index={server_index} count={len(exact_storage)}"
                    )
                storage = exact_storage[0]
                filename = urlparse(image_url).path.rsplit("/", 1)[-1]
                if not filename:
                    raise AssertionError("image filename precondition failed: count=0")
                remote_path = str(PurePosixPath(storage.path) / filename)
                expected_size = url_body_size(image_url)
                if not isinstance(expected_size, int) or expected_size <= 0:
                    raise AssertionError("image size precondition failed: count=0")

                queued = client.post(
                    "/api/tasks/images/download",
                    json={"storage_uuid": storage.uuid, "image_url": image_url},
                )
                queued.raise_for_status()
                assert wait_tasks(queued, client) == "finish"
                _refresh_images(client)

                image_response = client.get(
                    "/api/images",
                    params={
                        "poolUuid": storage.uuid,
                        "nodeName": server.name,
                        "name": filename,
                    },
                )
                image_response.raise_for_status()
                exact_images = _exact_images(
                    ImagePage.model_validate(image_response.json()),
                    str(storage.uuid),
                    filename,
                    remote_path,
                )
                remote_size, remote_digest = remote_file_metadata(
                    remote,
                    path=remote_path,
                    server_index=server_index,
                )
                if (
                    len(exact_images) != 1
                    or remote_size != expected_size
                    or len(remote_digest) != 64
                ):
                    raise AssertionError(
                        "image download postcondition failed: "
                        f"server_index={server_index} count={len(exact_images)}"
                    )

                deleted = client.delete(
                    f"/api/tasks/storages/{storage.uuid}/images/"
                    f"{quote(filename, safe='')}"
                )
                deleted.raise_for_status()
                assert wait_tasks(deleted, client) == "finish"
                _refresh_images(client)
                confirm = client.get(
                    "/api/images",
                    params={
                        "poolUuid": storage.uuid,
                        "nodeName": server.name,
                        "name": filename,
                    },
                )
                confirm.raise_for_status()
                remaining = _exact_images(
                    ImagePage.model_validate(confirm.json()),
                    str(storage.uuid),
                    filename,
                    remote_path,
                )
                if remaining:
                    raise AssertionError(
                        "image delete API postcondition failed: "
                        f"server_index={server_index} count={len(remaining)}"
                    )
                assert_remote_path_absent(
                    remote,
                    path=remote_path,
                    server_index=server_index,
                )
