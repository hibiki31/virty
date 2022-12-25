from fastapi.testclient import TestClient
import json

from main import app

client = TestClient(app)


def test_auth():
    json_open = open('./tests/env.json', 'r')
    json_load = json.load(json_open)
    response = client.post(
        "/api/auth",
        data={"username": json_load["user"], "password": json_load["password"]},
    )

    assert response.status_code == 200

    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    
    response = client.get(
        "/api/auth/validate",
        headers=headers,
        json={},
    )

    print(response.json())

    assert response.status_code == 200

    response = client.get(
        "/api/nodes",
        headers=headers,
        json={},
    )

    print(response.json())

