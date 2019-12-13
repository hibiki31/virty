import virty_api as api

api.API_URL = "http://localhost:80"

domains = api.domain_data()

for domain in domains:
    print(domain[0],domain[2])