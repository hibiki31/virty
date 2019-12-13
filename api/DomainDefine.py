import virty_api as api

api.API_URL = "http://localhost:80"

POST_DATA = {}
POST_DATA['node'] = ""
POST_DATA['archive'] = "Ubuntu18.04_vda.img"
POST_DATA['storage'] = "ssd"
POST_DATA['cpu'] = "1"
POST_DATA['memory'] = "1024"
POST_DATA['bridge'] = ["virbr0"]

for i in range(1,10):
    POST_DATA['name'] = "ubuntu_"+str(i)
    api.domain_define(POST_DATA)