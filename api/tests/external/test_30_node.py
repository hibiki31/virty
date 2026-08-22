from tests.external.conftest import EnvConfig


def test_key_generate(env, client):
    try:
        res = client.post("/api/nodes/key", json={"generate": True})
        assert res.status_code == 200
    finally:
        restore = client.post(
            "/api/nodes/key",
            json={"privateKey": env.key, "publicKey": env.pub},
        )
        assert restore.status_code == 200


def test_post_nodes_key(env, client):
    req_data = {
        "privateKey": env.key,
        "publicKey": env.pub,
    }
    res = client.post("/api/nodes/key", json=req_data)
    assert res.status_code == 200


def test_post_nodes(env: EnvConfig, nodes):
    assert nodes.count == len(env.servers)
