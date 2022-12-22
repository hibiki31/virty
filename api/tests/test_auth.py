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
    print(response.json())
    print(json_load)
    assert response.status_code == 200
    assert response.json() == {
        "id": "foobar",
        "title": "Foo Bar",
        "description": "The Foo Barters",
    }