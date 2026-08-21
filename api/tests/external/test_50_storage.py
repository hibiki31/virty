from storage.schemas import Storage, StorageMetadataForUpdate
from tests.external.fixtures.storage import create_storage, delete_storage


def test_delete_storage(env, client, created_storage):
    delete_storage(env, client)


def test_post_storage_ok(env, client, deleted_storage):
    create_storage(env, client)
    
    
def test_change_metadata(env, client, created_storage):
    for storage in created_storage.data:
        if storage.name.endswith("test-cloud"):
            req_data = StorageMetadataForUpdate(
                uuid=storage.uuid,
                rool="template",
                protocol="local",
                device_type="ssd",
            )
        elif storage.name.endswith("test-iso"):
            req_data = StorageMetadataForUpdate(
                uuid=storage.uuid,
                rool="iso",
                protocol="local",
                device_type="ssd",
            )
        elif storage.name.endswith("test-img"):
            req_data = StorageMetadataForUpdate(
                uuid=storage.uuid,
                rool="img",
                protocol="local",
                device_type="ssd",
            )
        else:
            continue
        response = client.patch(
            "/api/storages",
            json=req_data.model_dump(by_alias=True),
        )
        assert response.status_code == 200, response.text

        read_response = client.get(f"/api/storages/{storage.uuid}")
        assert read_response.status_code == 200, read_response.text
        updated = Storage.model_validate(read_response.json())
        assert updated.meta_data is not None
        assert updated.meta_data.rool == req_data.rool
        assert updated.meta_data.protocol == req_data.protocol
        assert updated.meta_data.device_type == req_data.device_type
