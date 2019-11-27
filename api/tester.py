import virty_api as api

api.API_URL = "http://localhost:80"

POST_DATA = {}
POST_DATA['node'] = ""
POST_DATA['archive'] = "Ubuntu18.04_vda.img"
POST_DATA['storage'] = "default"
POST_DATA['cpu'] = "1"
POST_DATA['memory'] = "1024"
POST_DATA['bridge'] = ["virbr0"]

# for i in range(1,10):
#     POST_DATA['name'] = "ubuntu_"+str(i)
#     api.domain_define(POST_DATA)

# domains = api.domain_data()

# for domain in domains:
#     api.domain_stop(domain[0])

api.auth_login("user2","abcxyz")
api.auth_test()