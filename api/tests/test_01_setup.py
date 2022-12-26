from fastapi.testclient import TestClient
import json


from main import app

client = TestClient(app)


def test_setup():
    json_open = open('./tests/env.json', 'r')
    json_load = json.load(json_open)

    response = client.get("/api/version")
    assert response.status_code == 200
    if response.json()["initialized"] == False:
        response = client.post(
            "/api/setup",
            data={"userId": json_load["user"], "password": json_load["password"]},
        )