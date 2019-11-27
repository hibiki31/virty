import requests

API_URL = "http://localhost:80"

result = requests.get(API_URL+"/api/sql/kvm_domain.json").json()

for domain in result['ResultSet']:
    POST_DATA = {}
    POST_DATA['domain-list'] = domain[0]
    #response = requests.post(API_URL+"/api/que/domain/undefine/", data=POST_DATA)