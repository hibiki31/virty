import virty_api as api

api.API_URL = "http://192.168.0.1:80"

domains = api.domain_data()

for domain in domains:
    print(domain[0],domain[2])
