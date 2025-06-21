import requests

BASE_URL = 'http://localhost:8765'
TOKEN = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"


def main():
    poweron_match = "-"
    
    vms = requests.get(f"{BASE_URL}/api/vms?admin=true",headers=HEADERS).json()
    
    for vm in vms["data"]:
        if poweron_match in vm["name"]:
            res = requests.patch(f'{BASE_URL}/api/tasks/vms/{vm["uuid"]}/power', headers=HEADERS, json={"status": "on"})
            print("PowerON VM: ", res.status_code, vm["uuid"], vm["name"])

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "ja",
    "authorization": f"Bearer {TOKEN}",
}


if __name__ == "__main__":
    main()