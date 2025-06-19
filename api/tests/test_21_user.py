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