import virty_api as api

api.API_URL = ""

domains = api.domain_data()

for domain in domains:
    api.domain_stop(domain[0])
    api.domain_undefine(domain[0])