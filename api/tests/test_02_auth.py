from fastapi.testclient import TestClient
import json

from main import app

client = TestClient(app)

headers = None

def test_auth():
    json_open = open('./tests/env.json', 'r')
    json_load = json.load(json_open)
    response = client.post(
        "/api/auth",
        data={"username": json_load["user"], "password": json_load["password"]},
    )

    assert response.status_code == 200

    global headers
    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    
    response = client.get(
        "/api/auth/validate",
        headers=headers,
        json={},
    )

    print(response.json())

    assert response.status_code == 200


def test_add_node():
    json_open = open('./tests/env.json', 'r')
    json_load = json.load(json_open)


    client.post(
        "/api/nodes/key",
        headers=headers,
        data={"publickKey": json_load["pub"], "privateKey": json_load["key"]},
    )

    
    response = client.get(
        "/api/nodes",
        headers=headers,
        json={},
    )

    if response.json() != []:
        return
    
    client.post(
        "/api/tasks/nodes",
        headers=headers,
        json={
            "name": "test",
            "description": "test",
            "domain": json_load["server"],
            "userName": json_load["server_user"],
            "port": 22,
            "libvirtRole": True
        }
    )
    

    assert False