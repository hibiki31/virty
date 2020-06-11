import virty

api = virty.api(endpoint="")
api.auth_login("admin","admin")

for i in api.domain_data():
    print(i)