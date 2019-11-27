import requests

API_URL = "http://localhost:80"

POST_DATA = {}
POST_DATA['node'] = ""
POST_DATA['archive'] = ""
POST_DATA['storage'] = "default"
POST_DATA['cpu'] = "1"
POST_DATA['memory'] = "1024"
POST_DATA['bridge'] = [["net":"virbr0"],["bridge":"virbr1"]]
POST_DATA['name'] = ""

response = requests.post(API_URL+"/api/que/domain/define/", data=POST_DATA)
print(response.status_code)
print(response.text)
