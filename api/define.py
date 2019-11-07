import requests

API_URL = "http://localhost:80"

POST_DATA = {}
POST_DATA['node'] = "node01"
POST_DATA['archive'] = "CentOS.img"
POST_DATA['storage'] = "default"
POST_DATA['cpu'] = "1"
POST_DATA['memory'] = "1024"
POST_DATA['bridge'] = "virbr0"

for i in range(1,10):
    POST_DATA['name'] = "test_"+str(i)
    response = requests.post(API_URL+"/api/que/domain/define/", data=POST_DATA)
    print(response.status_code)
    print(response.text)