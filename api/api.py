import requests, json

API_URL = "http://localhost:80"

POST_DATA = {}
POST_DATA["username"] = "user2"
POST_DATA["password"] = "abcxyz"

response = requests.post(API_URL+"/auth",json.dumps(POST_DATA),headers={'Content-Type': 'application/json'})
print(response.status_code)
token = json.loads(response.text)

print(token['access_token'])

response = requests.get(API_URL+"/protected",headers={'Authorization': 'JWT '+token['access_token']})
print(response.text)