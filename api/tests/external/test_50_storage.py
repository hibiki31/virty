from storage.schemas import Storage, StorageMetadataForUpdate


def test_storage_inventory(env, created_storage) -> None:
    expected = {
        (storage.name, server.name)
        for server in env.servers
        for storage in env.storages
    }
    actual = {
        (storage.name, storage.node_name)
        for storage in created_storage.data
        if (storage.name, storage.node_name) in expected
    }
    if actual != expected:
        raise AssertionError(
            f"storage inventory mismatch: count={len(actual.symmetric_difference(expected))}"
        )


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
        response.raise_for_status()

        read_response = client.get(f"/api/storages/{storage.uuid}")
        read_response.raise_for_status()
        updated = Storage.model_validate(read_response.json())
        assert updated.meta_data is not None
        assert updated.meta_data.rool == req_data.rool
        assert updated.meta_data.protocol == req_data.protocol
        assert updated.meta_data.device_type == req_data.device_type
