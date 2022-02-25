from fastapi.testclient import TestClient

from auth.router import app

client = TestClient(app)


def test_read_main():
    response = client.get("/api/auth/setup")
    assert response.json() == {"msg": "Hello World"}