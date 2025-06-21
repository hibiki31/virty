import requests

BASE_URL = 'http://localhost:8765'
TOKEN = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"


def main():
    deletion_match = "test-"
    
    vms = requests.get(f"{BASE_URL}/api/vms?admin=true",headers=HEADERS).json()
    
    for vm in vms["data"]:
        if deletion_match in vm["name"]:
            print("Delete VM: ",vm["uuid"], vm["name"])

            delete_uuid = vm["uuid"]
            requests.delete(f'{BASE_URL}/api/tasks/vms/{delete_uuid}', headers=HEADERS)

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "ja",
    "authorization": f"Bearer {TOKEN}",
}


if __name__ == "__main__":
    main()