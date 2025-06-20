from storage.schemas import StorageMetadataForUpdate
from tests.fixtures.storage import create_storage, delete_storage


def test_delete_storage(env, client, created_storage):
    delete_storage(env, client)


def test_post_storage_ok(env, client, deleted_storage):
    create_storage(env, client)
    
    
def test_change_metadata(env, client, created_storage):
    for storage in created_storage.data:
        if storage.name == "test-cloud":
            req_data = StorageMetadataForUpdate(
                uuid=storage.uuid,
                rool="template",
                protocol="local",
                device_type="ssd",
            )
        elif storage.name == "test-iso":
            req_data = StorageMetadataForUpdate(
                uuid=storage.uuid,
                rool="iso",
                protocol="local",
                device_type="ssd",
            )
        elif storage.name == "test-img":
            req_data = StorageMetadataForUpdate(
                uuid=storage.uuid,
                rool="img",
                protocol="local",
                device_type="ssd",
            )
        else:
            continue
        client.patch("/api/storage", data=req_data.model_dump_json(by_alias=True))