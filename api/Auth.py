import virty_api as api

api.API_URL = "http://192.168.144.44:80"

api.auth_login("user2","abcxyz")
api.auth_test()
