
from tests.fixtures.storage import create_storage, delete_storage


def test_delete_storage(env, client, created_storage):
    delete_storage(env, client)


def test_post_storage_ok(env, client, deleted_storage):
    create_storage(env, client)