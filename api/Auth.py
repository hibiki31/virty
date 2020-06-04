import virty_api as api

api.API_URL = "http://192.168.0.1:80"

api.auth_login("admin","admin")
api.auth_test()
