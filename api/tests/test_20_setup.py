def test_api_auth_validate_ng(gust_client):
    assert gust_client.get('/api/auth/validate').status_code == 401

    
def test_api_auth_validate_ok(client):
    assert client.get('/api/auth/validate').status_code == 200


def test_api_users_me(client, env):
    assert client.get('/api/users/me').json()["id"] == env.username