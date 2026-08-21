def test_create_user(env, client):
    for user in env.users:
        req_data = {
            "username": user.username,
            "password": user.password
        }
        res = client.post("/api/users", json=req_data)
        assert res.status_code == 200


def test_delete_user(env, client):
    for user in env.users:
        res = client.delete(f'/api/users/{user.username}')
        assert res.status_code == 200


def test_update_user(env, client):
    for user in env.users:
        client.post(
            "/api/users",
            json={"username": user.username, "password": user.password},
        )
        req_data = {
            "username": user.username,
            "password": user.password,
            "scopes": [{"name": "user"}],
            "publickeys": [
                {"name": "default", "publickey": user.publickey},
            ],
        }
        res = client.put(f"/api/users/{user.username}", json=req_data)
        assert res.status_code == 200
