from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_setup():
    response = client.get("/api/version")
    assert response.status_code == 200
    if response.json()["initialized"] == False:
        pass